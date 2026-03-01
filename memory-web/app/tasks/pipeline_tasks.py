"""
Celery tasks for the processing pipeline.
Chains: segment → tag → extract_entities → synthesize_memories → embed
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from celery import chain, group

from ..celery_app import celery_app
from ..database import db_session
from ..models import Conversation, PipelineRun, Source
from ..pipelines import segmenter, tagger, entity_extractor, memory_synthesizer, embedder

logger = logging.getLogger(__name__)


def _update_pipeline_run(
    source_id: int,
    stage: str,
    status: str,
    task_id: str = None,
    records: int = 0,
    error: str = None,
) -> None:
    with db_session() as db:
        run = (
            db.query(PipelineRun)
            .filter(PipelineRun.source_id == source_id, PipelineRun.stage == stage)
            .first()
        )
        if not run:
            run = PipelineRun(source_id=source_id, stage=stage)
            db.add(run)

        run.status = status
        run.celery_task_id = task_id
        run.records_processed = records
        run.error_message = error
        if status == "running":
            run.started_at = datetime.utcnow()
        elif status in ("done", "failed"):
            run.completed_at = datetime.utcnow()


# ---------------------------------------------------------------------------
# Per-conversation pipeline
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="memoryweb.segment_conversation")
def segment_conversation_task(self, conversation_id: int) -> Dict[str, Any]:
    """Heuristic + LLM segmentation of one conversation."""
    self.update_state(state="STARTED", meta={"conversation_id": conversation_id})
    count = segmenter.segment_conversation(conversation_id, use_llm=True)
    return {"conversation_id": conversation_id, "segments_created": count}


@celery_app.task(bind=True, name="memoryweb.tag_conversation")
def tag_conversation_task(self, conversation_id: int) -> Dict[str, Any]:
    """Tag all segments in a conversation."""
    count = tagger.tag_conversation_segments(conversation_id)
    return {"conversation_id": conversation_id, "tags_created": count}


@celery_app.task(bind=True, name="memoryweb.extract_entities_conversation")
def extract_entities_conversation_task(self, conversation_id: int) -> Dict[str, Any]:
    """Extract entities from all segments in a conversation."""
    with db_session() as db:
        from ..models import Segment
        segments = (
            db.query(Segment)
            .filter(Segment.conversation_id == conversation_id)
            .all()
        )
        seg_ids = [s.id for s in segments]

    total = 0
    for seg_id in seg_ids:
        total += entity_extractor.extract_entities_for_segment(seg_id)

    return {"conversation_id": conversation_id, "entity_mentions_created": total}


@celery_app.task(bind=True, name="memoryweb.synthesize_conversation")
def synthesize_conversation_task(self, conversation_id: int) -> Dict[str, Any]:
    """Synthesize memories from all segments in a conversation."""
    with db_session() as db:
        from ..models import Segment
        segments = (
            db.query(Segment)
            .filter(Segment.conversation_id == conversation_id)
            .all()
        )
        seg_ids = [s.id for s in segments]

    total = 0
    for seg_id in seg_ids:
        total += memory_synthesizer.synthesize_memories_for_segment(seg_id)

    return {"conversation_id": conversation_id, "memories_created": total}


@celery_app.task(bind=True, name="memoryweb.embed_conversation")
def embed_conversation_task(self, conversation_id: int) -> Dict[str, Any]:
    """Embed segments for a conversation (memories are handled by embedding_worker daemon)."""
    segs = embedder.embed_segments(conversation_id)
    return {
        "conversation_id": conversation_id,
        "segments_embedded": segs,
        "memories_embedded": 0,  # handled by embedding_worker via EmbeddingQueue
    }


# ---------------------------------------------------------------------------
# Full pipeline for one source
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="memoryweb.run_full_pipeline")
def run_full_pipeline(self, source_id: int) -> Dict[str, Any]:
    """
    Run the complete processing pipeline for all conversations in a source.
    Chains: segment → tag → extract → synthesize → embed per conversation.
    """
    self.update_state(state="STARTED", meta={"source_id": source_id, "stage": "init"})
    _update_pipeline_run(source_id, "full_pipeline", "running", task_id=self.request.id)

    with db_session() as db:
        convs = (
            db.query(Conversation)
            .filter(Conversation.source_id == source_id)
            .all()
        )
        conv_ids = [c.id for c in convs]

    results = {"source_id": source_id, "conversations": len(conv_ids)}
    total_segs = total_mems = total_ents = 0

    for i, conv_id in enumerate(conv_ids):
        self.update_state(
            state="PROGRESS",
            meta={"source_id": source_id, "progress": i / len(conv_ids), "stage": "segment"},
        )
        try:
            segs = segmenter.segment_conversation(conv_id, use_llm=True)
            total_segs += segs

            tagger.tag_conversation_segments(conv_id)

            with db_session() as db:
                from ..models import Segment
                seg_ids = [s.id for s in db.query(Segment).filter(Segment.conversation_id == conv_id).all()]

            for seg_id in seg_ids:
                total_ents += entity_extractor.extract_entities_for_segment(seg_id)
                total_mems += memory_synthesizer.synthesize_memories_for_segment(seg_id)

            embedder.embed_segments(conv_id)

        except Exception as e:
            logger.error("Pipeline failed for conversation %d: %s", conv_id, e)

    # NOTE: memories are queued for embedding by memory_synthesizer (via EmbeddingQueue).
    # The embedding_worker daemon picks them up. No direct embed_memories() call needed.

    results.update({"segments": total_segs, "memories": total_mems, "entity_mentions": total_ents})
    _update_pipeline_run(source_id, "full_pipeline", "done", records=total_mems)
    return results


# ---------------------------------------------------------------------------
# Watchdog: requeue stalled pipeline and embedding jobs (Celery Beat task)
# ---------------------------------------------------------------------------

@celery_app.task(name="memoryweb.requeue_stalled")
def requeue_stalled() -> Dict[str, Any]:
    """
    Self-healing watchdog — runs every 10 minutes via Celery Beat.

    1. Pipeline runs stuck in 'running' for > 1 hour → mark failed
    2. Pipeline runs with status='failed' → re-trigger full pipeline
    3. embedding_queue items with status='failed' and attempts < MAX_ATTEMPTS → reset to pending
    """
    stale_cutoff = datetime.utcnow() - timedelta(hours=1)
    requeued_pipelines = 0
    reset_embeddings = 0
    marked_failed = 0

    with db_session() as db:
        # Step 1: mark stale running pipeline_runs as failed
        stale_runs = (
            db.query(PipelineRun)
            .filter(
                PipelineRun.status == "running",
                PipelineRun.started_at < stale_cutoff,
            )
            .all()
        )
        stale_ids = [r.source_id for r in stale_runs]
        for run in stale_runs:
            run.status = "failed"
            run.error_message = "Watchdog: timed out after >1h"
            run.completed_at = datetime.utcnow()
            marked_failed += 1

        # Step 2: re-trigger failed pipeline_runs (low attempt count = retriable)
        failed_runs = (
            db.query(PipelineRun)
            .filter(
                PipelineRun.status == "failed",
                PipelineRun.source_id.isnot(None),
            )
            .distinct(PipelineRun.source_id)
            .all()
        )
        for run in failed_runs:
            if run.source_id:
                run_full_pipeline.delay(run.source_id)
                requeued_pipelines += 1

    # Step 3: reset failed embedding_queue items to pending if retries remain
    from ..database import engine
    from sqlalchemy import text as _text
    from ..config import settings as _settings
    MAX_ATT = 3

    with engine.connect() as conn:
        result = conn.execute(
            _text(f"""
                UPDATE {_settings.MW_DB_SCHEMA}.embedding_queue
                SET status = 'pending',
                    error = NULL,
                    started_at = NULL
                WHERE status = 'failed'
                  AND attempts < :max_att
            """),
            {"max_att": MAX_ATT},
        )
        reset_embeddings = result.rowcount
        conn.commit()

    logger.info(
        "requeue_stalled: marked_failed=%d, requeued_pipelines=%d, reset_embeddings=%d",
        marked_failed, requeued_pipelines, reset_embeddings,
    )
    return {
        "marked_failed": marked_failed,
        "requeued_pipelines": requeued_pipelines,
        "reset_embeddings": reset_embeddings,
    }

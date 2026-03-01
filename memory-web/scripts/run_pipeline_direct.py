"""
Direct (non-Celery) pipeline runner for end-to-end testing.
Runs segment → tag → entity extract → synthesize → embed on a source.

Usage:
    python scripts/run_pipeline_direct.py --source-id 1
"""

import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
log = logging.getLogger("pipeline_direct")


def run(source_id: int):
    from app.database import db_session
    from app.models import Conversation, Segment, Memory

    from app.pipelines.segmenter import segment_conversation
    from app.pipelines.tagger import tag_segment
    from app.pipelines.entity_extractor import extract_entities_for_segment
    from app.pipelines.memory_synthesizer import synthesize_memories_for_segment
    from app.pipelines.embedder import embed_segments, embed_memories

    # Get conversations for this source
    with db_session() as db:
        conv_ids = [c.id for c in db.query(Conversation.id)
                    .filter(Conversation.source_id == source_id).all()]
    log.info("Source %d: %d conversations", source_id, len(conv_ids))

    # --- Step 1: Segment ---
    log.info("=== Step 1: Segmenting ===")
    for cid in conv_ids:
        try:
            n = segment_conversation(cid, use_llm=True)
            log.info("  Conv %d → %d segments", cid, n)
        except Exception as e:
            log.error("  Conv %d segmenting failed: %s", cid, e)

    # Gather all segment IDs from DB
    with db_session() as db:
        seg_rows = (db.query(Segment.id, Segment.conversation_id)
                    .filter(Segment.conversation_id.in_(conv_ids))
                    .filter(Segment.tombstoned_at.is_(None))
                    .all())
    seg_ids = [r.id for r in seg_rows]
    log.info("Total segments: %d", len(seg_ids))

    if not seg_ids:
        log.error("No segments — aborting pipeline")
        return

    # --- Step 2: Tag ---
    log.info("=== Step 2: Tagging ===")
    for sid in seg_ids:
        try:
            n = tag_segment(sid)
            log.info("  Seg %d → %d tags", sid, n)
        except Exception as e:
            log.error("  Seg %d tagging failed: %s", sid, e)

    # --- Step 3: Entity extraction ---
    log.info("=== Step 3: Entity extraction ===")
    for sid in seg_ids:
        try:
            n = extract_entities_for_segment(sid)
            log.info("  Seg %d → %d entities", sid, n)
        except Exception as e:
            log.error("  Seg %d entity extract failed: %s", sid, e)

    # --- Step 4: Memory synthesis ---
    log.info("=== Step 4: Memory synthesis ===")
    for sid in seg_ids:
        try:
            n = synthesize_memories_for_segment(sid)
            log.info("  Seg %d → %d memories", sid, n)
        except Exception as e:
            log.error("  Seg %d synthesis failed: %s", sid, e)

    # --- Step 5: Embed segments ---
    log.info("=== Step 5: Embedding segments ===")
    for cid in conv_ids:
        try:
            n = embed_segments(cid)
            log.info("  Conv %d → %d segment embeddings", cid, n)
        except Exception as e:
            log.error("  Conv %d embed_segments failed: %s", cid, e)

    # --- Step 6: Embed memories ---
    log.info("=== Step 6: Embedding memories ===")
    try:
        n = embed_memories(source_id=source_id)
        log.info("  Source %d → %d memory embeddings", source_id, n)
    except Exception as e:
        log.error("  embed_memories failed: %s", e)

    # --- Summary ---
    log.info("=== Pipeline complete. DB summary: ===")
    with db_session() as db:
        from app.models import Tag, Entity, Embedding
        n_segs = db.query(Segment).filter(Segment.tombstoned_at.is_(None)).count()
        n_tags = db.query(Tag).count()
        n_ents = db.query(Entity).count()
        n_mems = db.query(Memory).filter(Memory.tombstoned_at.is_(None)).count()
        n_embs = db.query(Embedding).count()
        log.info("  Segments:   %d", n_segs)
        log.info("  Tags:       %d", n_tags)
        log.info("  Entities:   %d", n_ents)
        log.info("  Memories:   %d", n_mems)
        log.info("  Embeddings: %d", n_embs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", type=int, required=True)
    args = parser.parse_args()
    run(args.source_id)

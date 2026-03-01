"""
Run pipeline on all conversations that haven't been segmented yet.
Usage: python scripts/run_all_pipelines.py [--limit N] [--skip-llm]
"""

import argparse
import logging
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.WARNING, format="%(name)s %(levelname)s %(message)s")
log = logging.getLogger("run_all")
log.setLevel(logging.INFO)


def run(limit: int = 0, skip_llm: bool = False):
    from app.database import db_session
    from app.models import Conversation, Segment, Memory, Tag, Entity, Embedding

    from app.pipelines.segmenter import segment_conversation
    from app.pipelines.tagger import tag_segment
    from app.pipelines.entity_extractor import extract_entities_for_segment
    from app.pipelines.memory_synthesizer import synthesize_memories_for_segment
    from app.pipelines.embedder import embed_segments, embed_memories

    # Get all conversations without segments
    with db_session() as db:
        segmented_conv_ids = {
            r.conversation_id
            for r in db.query(Segment.conversation_id).distinct().all()
        }
        all_conv_ids = [
            r.id for r in db.query(Conversation.id)
            .filter(~Conversation.id.in_(segmented_conv_ids))
            .order_by(Conversation.id)
            .all()
        ]

    log.info("Conversations needing pipeline: %d", len(all_conv_ids))
    if limit:
        all_conv_ids = all_conv_ids[:limit]
        log.info("Limited to %d", limit)

    total_segs = 0
    total_tags = 0
    total_ents = 0
    total_mems = 0
    total_embs = 0

    for idx, cid in enumerate(all_conv_ids):
        log.info("=== Conv %d (%d/%d) ===", cid, idx + 1, len(all_conv_ids))
        t0 = time.time()

        # Segment
        try:
            n_segs = segment_conversation(cid, use_llm=not skip_llm)
            total_segs += n_segs
            log.info("  segments: %d", n_segs)
        except Exception as e:
            log.error("  segmenting failed: %s", e)
            continue

        # Get segment IDs
        with db_session() as db:
            seg_ids = [r.id for r in db.query(Segment.id)
                       .filter(Segment.conversation_id == cid)
                       .filter(Segment.tombstoned_at.is_(None)).all()]

        # Tag
        for sid in seg_ids:
            try:
                n = tag_segment(sid)
                total_tags += n
            except Exception as e:
                log.warning("  tag seg %d: %s", sid, e)

        # Entity extract
        for sid in seg_ids:
            try:
                n = extract_entities_for_segment(sid)
                total_ents += n
            except Exception as e:
                log.warning("  entity seg %d: %s", sid, e)

        # Memory synthesis
        for sid in seg_ids:
            try:
                n = synthesize_memories_for_segment(sid)
                total_mems += n
            except Exception as e:
                log.warning("  synthesis seg %d: %s", sid, e)

        # Embed segments
        try:
            n = embed_segments(cid)
            total_embs += n
        except Exception as e:
            log.warning("  embed_segments: %s", e)

        elapsed = time.time() - t0
        log.info("  Conv %d done in %.1fs (segs=%d tags=%d ents=%d mems=%d)",
                 cid, elapsed, n_segs, total_tags, total_ents, total_mems)

    # Embed all memories at the end
    log.info("Embedding all memories...")
    try:
        n = embed_memories()
        total_embs += n
        log.info("  Memory embeddings: %d", n)
    except Exception as e:
        log.error("  embed_memories failed: %s", e)

    log.info("=== COMPLETE ===")
    with db_session() as db:
        n_segs = db.query(Segment).filter(Segment.tombstoned_at.is_(None)).count()
        n_tags = db.query(Tag).count()
        n_ents = db.query(Entity).count()
        n_mems = db.query(Memory).filter(Memory.tombstoned_at.is_(None)).count()
        n_embs = db.query(Embedding).count()
    log.info("DB: segs=%d tags=%d entities=%d memories=%d embeddings=%d",
             n_segs, n_tags, n_ents, n_mems, n_embs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Max conversations to process")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM calls (heuristics only)")
    args = parser.parse_args()
    run(args.limit, args.skip_llm)

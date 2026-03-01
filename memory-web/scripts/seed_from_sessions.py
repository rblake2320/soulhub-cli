"""
Seed MemoryWeb from existing Claude sessions.

Usage:
    python scripts/seed_from_sessions.py [--session path.jsonl] [--all] [--pipeline]

Examples:
    python scripts/seed_from_sessions.py --all
    python scripts/seed_from_sessions.py --session ~/.claude/projects/.../4b271270.jsonl --pipeline
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import ensure_schema_and_extensions, engine
from app.models import Base
from app.services.ingestion import ingest_session_file, ingest_all_sessions
from app.pipelines.segmenter import segment_conversation
from app.pipelines.tagger import tag_conversation_segments
from app.pipelines.entity_extractor import extract_entities_for_segment
from app.pipelines.memory_synthesizer import synthesize_memories_for_segment
from app.pipelines.embedder import embed_segments, embed_memories, build_ivfflat_index
from app.database import db_session
from app.models import Conversation, Segment


def main():
    parser = argparse.ArgumentParser(description="Seed MemoryWeb from Claude sessions")
    parser.add_argument("--session", help="Path to a single session JSONL")
    parser.add_argument("--all", action="store_true", help="Ingest all sessions")
    parser.add_argument("--directory", help="Sessions directory override")
    parser.add_argument("--pipeline", action="store_true", help="Run full pipeline after ingest")
    parser.add_argument("--force", action="store_true", help="Re-ingest even if unchanged")
    parser.add_argument("--build-index", action="store_true", help="Build IVFFlat index after embedding")
    args = parser.parse_args()

    # Ensure schema
    print("Setting up database...")
    ensure_schema_and_extensions()
    Base.metadata.create_all(bind=engine)

    source_ids = []

    if args.session:
        print(f"Ingesting session: {args.session}")
        result = ingest_session_file(args.session, force=args.force)
        print(f"Result: {result}")
        if result.get("source_id"):
            source_ids.append(result["source_id"])

    elif args.all:
        directory = args.directory or settings.MW_SESSIONS_DIR
        print(f"Ingesting all sessions from: {directory}")
        result = ingest_all_sessions(directory, force=args.force)
        print(f"Result: {result}")
        # Get source IDs for pipeline
        with db_session() as db:
            from app.models import Source
            sources = db.query(Source).filter(Source.source_type == "claude_session").all()
            source_ids = [s.id for s in sources]
    else:
        print("No input specified. Use --session or --all")
        parser.print_help()
        sys.exit(1)

    if args.pipeline and source_ids:
        print(f"\nRunning pipeline on {len(source_ids)} sources...")
        for source_id in source_ids:
            print(f"Processing source {source_id}...")
            with db_session() as db:
                convs = db.query(Conversation).filter(Conversation.source_id == source_id).all()
                conv_ids = [c.id for c in convs]

            for conv_id in conv_ids:
                print(f"  Segmenting conversation {conv_id}...")
                segs = segment_conversation(conv_id, use_llm=False)  # fast mode
                print(f"    → {segs} segments")

                tag_conversation_segments(conv_id)

                with db_session() as db:
                    seg_ids = [s.id for s in db.query(Segment).filter(Segment.conversation_id == conv_id).all()]

                for seg_id in seg_ids:
                    extract_entities_for_segment(seg_id)
                    synthesize_memories_for_segment(seg_id)

                embed_segments(conv_id)

            embed_memories(source_id=source_id)

        if args.build_index:
            print("Building IVFFlat index...")
            build_ivfflat_index()

        print("\nPipeline complete!")

    print("Done.")


if __name__ == "__main__":
    main()

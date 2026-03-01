"""
Memory synthesizer: extract atomic facts from segments with provenance pointers.

Each atomic fact becomes a Memory record linked back to its source segment/messages.
Dedup by fact_hash (SHA-256 of normalised fact text).
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..database import db_session
from ..models import EmbeddingQueue, Memory, MemoryProvenance, Message, Segment
from ..services.ollama_client import generate_json

logger = logging.getLogger(__name__)


def _normalise_fact(fact: str) -> str:
    """Lowercase, strip, collapse whitespace for dedup."""
    return " ".join(fact.lower().split())


def _fact_hash(fact: str) -> str:
    return hashlib.sha256(_normalise_fact(fact).encode()).hexdigest()


def _build_synthesis_prompt(content: str, summary: Optional[str] = None) -> str:
    summary_hint = f"\nConversation summary: {summary}" if summary else ""
    return f"""
Extract atomic facts from this conversation segment.
Each fact should be a single, standalone statement that can be recalled independently.
Focus on: decisions made, configuration values, technical choices, learned information,
user preferences, system states, problems encountered and solutions found.

Return a JSON array. Each element:
{{
  "fact": "A single atomic fact statement",
  "category": "infrastructure|preference|decision|configuration|problem|solution|learning|other",
  "confidence": 0.0-1.0,
  "importance": 1-5
}}

Return 1-10 facts only. No duplicates. Return empty array if no significant facts.
{summary_hint}

Conversation:
{content[:3000]}

Return ONLY the JSON array.
""".strip()


def synthesize_memories_for_segment(segment_id: int) -> int:
    """
    Extract atomic facts from a segment and store as Memory records with provenance.
    Returns number of new memories created.
    """
    with db_session() as db:
        seg = db.query(Segment).get(segment_id)
        if not seg:
            return 0

        # Check if already synthesized
        existing = db.query(MemoryProvenance).filter(
            MemoryProvenance.segment_id == segment_id
        ).count()
        if existing > 0:
            return 0

        messages = (
            db.query(Message)
            .filter(
                Message.conversation_id == seg.conversation_id,
                Message.ordinal >= seg.start_ordinal,
                Message.ordinal <= seg.end_ordinal,
                Message.tombstoned_at.is_(None),
            )
            .order_by(Message.ordinal)
            .all()
        )

        if not messages:
            return 0

        content = "\n".join(
            f"[{m.role.upper()}]: {m.content or ''}"
            for m in messages
        )

        # Get source_id from conversation
        from ..models import Conversation
        conv = db.query(Conversation).get(seg.conversation_id)
        source_id = conv.source_id if conv else None

        try:
            facts = generate_json(_build_synthesis_prompt(content, seg.summary))
        except Exception as e:
            logger.warning("Memory synthesis failed for segment %d: %s", segment_id, e)
            return 0

        # Handle {"facts": [...]} wrapper or bare list
        if isinstance(facts, dict):
            facts = facts.get("facts", facts.get("memories", []))
        if not isinstance(facts, list):
            return 0

        created = 0
        for fact_data in facts[:10]:  # max 10 per segment
            fact_text = fact_data.get("fact", "").strip()
            if not fact_text or len(fact_text) < 10:
                continue

            fhash = _fact_hash(fact_text)

            # Dedup check
            existing_mem = db.query(Memory).filter(Memory.fact_hash == fhash).first()
            if existing_mem:
                # Still link provenance
                prov = MemoryProvenance(
                    memory_id=existing_mem.id,
                    segment_id=segment_id,
                    source_id=source_id,
                    derivation_type="extracted",
                )
                db.add(prov)
                continue

            memory = Memory(
                fact=fact_text,
                fact_hash=fhash,
                category=fact_data.get("category", "other"),
                confidence=float(fact_data.get("confidence", 0.7)),
                importance=int(fact_data.get("importance", 3)),
                access_count=0,
            )
            db.add(memory)
            db.flush()

            # Link first message as primary provenance
            primary_msg = messages[len(messages) // 2]  # mid-point message
            prov = MemoryProvenance(
                memory_id=memory.id,
                segment_id=segment_id,
                message_id=primary_msg.id,
                source_id=source_id,
                derivation_type="extracted",
            )
            db.add(prov)
            # Queue for embedding
            db.add(EmbeddingQueue(target_type="memory", target_id=memory.id))
            created += 1

        db.flush()
        return created


def import_sqlite_memory_as_memories(
    journal_entries: List[Any],
    knowledge_items: List[Any],
    source_id: int,
    conversation_id: int,
) -> int:
    """
    Directly import SQLite memory DB entries as Memory records.
    Returns number created.
    """
    created = 0
    with db_session() as db:
        for item in journal_entries + knowledge_items:
            text = getattr(item, "text", None) or getattr(item, "content", "")
            if not text or len(text) < 5:
                continue

            fhash = _fact_hash(text)
            if db.query(Memory).filter(Memory.fact_hash == fhash).first():
                continue

            memory = Memory(
                fact=text[:2000],
                fact_hash=fhash,
                category=getattr(item, "category", None) or getattr(item, "topic", "imported"),
                confidence=0.8,
                importance=3,
            )
            db.add(memory)
            db.flush()

            prov = MemoryProvenance(
                memory_id=memory.id,
                source_id=source_id,
                derivation_type="imported",
            )
            db.add(prov)
            db.add(EmbeddingQueue(target_type="memory", target_id=memory.id))
            created += 1

        db.flush()
    return created

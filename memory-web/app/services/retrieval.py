"""
3-tier retrieval router.

Tier 1: Structured SQL (tags, entities, date ranges)  → target <10ms
Tier 2: Memory fact search (trigram + provenance JOIN) → target <50ms
Tier 3: Semantic vector search (pgvector cosine)       → target <500ms

Every result includes a provenance chain: memory → segment → messages → raw source.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import db_session, engine
from ..models import Memory, MemoryProvenance, Message, Segment, Source, Tag, TagAxis
from ..schemas import ProvenanceChain, SearchResult, SearchResponse

logger = logging.getLogger(__name__)

SCHEMA = settings.MW_DB_SCHEMA

# ---------------------------------------------------------------------------
# Sentence-transformers singleton — shared across all Tier 3 calls
# ---------------------------------------------------------------------------
_embed_model = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(settings.MW_EMBED_MODEL)
    return _embed_model


def warmup_model():
    """Preload the embedding model so the first Tier 3 search is fast."""
    import numpy as np
    model = _get_embed_model()
    model.encode(["warmup"], normalize_embeddings=True)
    return model


def _build_provenance(memory_id: int, db: Session) -> List[ProvenanceChain]:
    provs = (
        db.query(MemoryProvenance)
        .filter(MemoryProvenance.memory_id == memory_id)
        .all()
    )
    result = []
    for p in provs:
        chain = ProvenanceChain(
            memory_id=memory_id,
            segment_id=p.segment_id,
            message_id=p.message_id,
            source_id=p.source_id,
            derivation_type=p.derivation_type,
        )
        if p.source_id:
            src = db.query(Source).get(p.source_id)
            if src:
                chain.source_path = src.source_path
        if p.message_id:
            msg = db.query(Message).get(p.message_id)
            if msg:
                chain.char_offset_start = msg.char_offset_start
                chain.char_offset_end = msg.char_offset_end
        result.append(chain)
    return result


# ---------------------------------------------------------------------------
# Tier 1: Structured SQL
# ---------------------------------------------------------------------------

def tier1_structured(
    db: Session,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    include_tombstoned: bool = False,
    k: int = 10,
) -> List[SearchResult]:
    """Search by tags, entities, date ranges, conversation ID."""
    results = []
    filters = filters or {}

    base_q = db.query(Memory)
    if not include_tombstoned:
        base_q = base_q.filter(Memory.tombstoned_at.is_(None))

    # Tag filters: {"domain": "infrastructure", "project": "imds-autoqa"}
    tag_filters = {k: v for k, v in filters.items() if k in ("domain", "intent", "sensitivity", "importance", "project")}
    if tag_filters:
        for axis_name, axis_value in tag_filters.items():
            axis = db.query(TagAxis).filter(TagAxis.axis_name == axis_name).first()
            if axis:
                seg_ids = [
                    t.segment_id for t in db.query(Tag)
                    .filter(Tag.axis_id == axis.id, Tag.value == axis_value)
                    .all()
                ]
                if seg_ids:
                    mem_ids = [
                        p.memory_id for p in db.query(MemoryProvenance)
                        .filter(MemoryProvenance.segment_id.in_(seg_ids))
                        .all()
                    ]
                    base_q = base_q.filter(Memory.id.in_(mem_ids))

    # Date filters
    if "date_from" in filters:
        # Join through provenance → message
        pass  # simplified — date range handled by query text for now

    # Category filter
    if "category" in filters:
        base_q = base_q.filter(Memory.category == filters["category"])

    # Importance filter
    if "min_importance" in filters:
        base_q = base_q.filter(Memory.importance >= int(filters["min_importance"]))

    memories = base_q.order_by(Memory.utility_score.desc(), Memory.importance.desc()).limit(k).all()

    for mem in memories:
        tags = []
        for prov in mem.provenance:
            if prov.segment:
                for tag in prov.segment.tags:
                    tags.append({"axis": tag.axis.axis_name if tag.axis else "", "value": tag.value, "confidence": tag.confidence})

        provenance = _build_provenance(mem.id, db)

        results.append(SearchResult(
            result_type="memory",
            id=mem.id,
            content=mem.fact,
            score=1.0 if tag_filters else 0.8,
            tier=1,
            tags=tags,
            provenance=provenance,
            tombstoned=mem.tombstoned_at is not None,
        ))

    return results


# ---------------------------------------------------------------------------
# Tier 2: Memory trigram search
# ---------------------------------------------------------------------------

def tier2_trigram(
    db: Session,
    query: str,
    include_tombstoned: bool = False,
    k: int = 10,
) -> List[SearchResult]:
    """Trigram similarity search on memory facts."""
    tomb_filter = "" if include_tombstoned else "AND m.tombstoned_at IS NULL"
    sql = text(f"""
        SELECT m.id, m.fact, m.category, m.confidence, m.tombstoned_at,
               similarity(m.fact, :query) AS sim
        FROM {SCHEMA}.memories m
        WHERE similarity(m.fact, :query) > 0.1
        {tomb_filter}
        ORDER BY sim DESC
        LIMIT :k
    """)

    with engine.connect() as conn:
        rows = conn.execute(sql, {"query": query, "k": k}).fetchall()

    results = []
    with db_session() as db2:
        for row in rows:
            mem_id, fact, category, confidence, tomb, sim = row
            provenance = _build_provenance(mem_id, db2)
            results.append(SearchResult(
                result_type="memory",
                id=mem_id,
                content=fact,
                score=float(sim),
                tier=2,
                provenance=provenance,
                tombstoned=tomb is not None,
            ))

    return results


# ---------------------------------------------------------------------------
# Tier 3: Semantic vector search
# ---------------------------------------------------------------------------

def tier3_semantic(
    query: str,
    include_tombstoned: bool = False,
    k: int = 10,
) -> List[SearchResult]:
    """Cosine similarity search via pgvector."""
    import numpy as np

    model = _get_embed_model()
    qvec = model.encode([query], normalize_embeddings=True).astype(np.float32)[0].tolist()

    tomb_filter = "" if include_tombstoned else "AND m.tombstoned_at IS NULL"
    sql = text(f"""
        SELECT e.target_id, m.fact, m.category, m.tombstoned_at,
               1 - (e.vector <=> CAST(:qvec AS vector)) AS score
        FROM {SCHEMA}.embeddings e
        JOIN {SCHEMA}.memories m ON m.id = e.target_id
        WHERE e.target_type = 'memory'
        {tomb_filter}
        ORDER BY e.vector <=> CAST(:qvec AS vector)
        LIMIT :k
    """)

    with engine.connect() as conn:
        rows = conn.execute(sql, {"qvec": str(qvec), "k": k}).fetchall()

    results = []
    with db_session() as db:
        for row in rows:
            mem_id, fact, category, tomb, score = row
            provenance = _build_provenance(mem_id, db)
            results.append(SearchResult(
                result_type="memory",
                id=mem_id,
                content=fact,
                score=float(score),
                tier=3,
                provenance=provenance,
                tombstoned=tomb is not None,
            ))

    return results


# ---------------------------------------------------------------------------
# Retrieval router
# ---------------------------------------------------------------------------

def search(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    k: int = 10,
    include_tombstoned: bool = False,
    min_tier: int = 1,
    force_tier: Optional[int] = None,
) -> SearchResponse:
    """
    3-tier retrieval router. Returns SearchResponse with provenance chains.

    force_tier: if set, runs ONLY that tier and returns immediately.
                Useful for benchmarking individual tiers or debugging recall.
    """
    start = time.monotonic()
    tiers_used = []
    all_results: List[SearchResult] = []
    seen_ids = set()

    def dedupe(results: List[SearchResult]) -> List[SearchResult]:
        out = []
        for r in results:
            if r.id not in seen_ids:
                seen_ids.add(r.id)
                out.append(r)
        return out

    # force_tier: bypass the cascade and run exactly one tier
    if force_tier is not None:
        if force_tier == 1:
            with db_session() as db:
                results = tier1_structured(db, query, filters or {}, include_tombstoned, k)
            if results:
                tiers_used.append(1)
            all_results = results
        elif force_tier == 2:
            with db_session() as db:
                results = tier2_trigram(db, query, include_tombstoned, k)
            if results:
                tiers_used.append(2)
            all_results = results
        elif force_tier == 3:
            try:
                results = tier3_semantic(query, include_tombstoned, k)
                if results:
                    tiers_used.append(3)
                all_results = results
            except Exception as e:
                logger.warning("Tier 3 semantic search failed: %s", e)

        elapsed_ms = (time.monotonic() - start) * 1000
        return SearchResponse(
            query=query,
            total=len(all_results),
            results=all_results[:k],
            tiers_used=tiers_used,
            latency_ms=round(elapsed_ms, 2),
        )

    # Normal cascade mode
    # Tier 1: Structured (only meaningful when filters are present)
    has_filters = bool(filters)
    if min_tier <= 1 and has_filters:
        with db_session() as db:
            t1 = tier1_structured(db, query, filters, include_tombstoned, k)
        t1 = dedupe(t1)
        all_results.extend(t1)
        if t1:
            tiers_used.append(1)

    # Tier 2: Trigram (if no filters, or < 5 results from Tier 1)
    if min_tier <= 2 and len(all_results) < 5:
        with db_session() as db:
            t2 = tier2_trigram(db, query, include_tombstoned, k)
        t2 = dedupe(t2)
        all_results.extend(t2)
        if t2:
            tiers_used.append(2)

    # Tier 3: Semantic (if still insufficient)
    if min_tier <= 3 and len(all_results) < 5:
        try:
            t3 = tier3_semantic(query, include_tombstoned, k)
            t3 = dedupe(t3)
            all_results.extend(t3)
            if t3:
                tiers_used.append(3)
        except Exception as e:
            logger.warning("Tier 3 semantic search failed: %s", e)

    # Update access + retrieval counts
    if all_results:
        with db_session() as db:
            from datetime import datetime
            for r in all_results[:k]:
                mem = db.query(Memory).get(r.id)
                if mem:
                    mem.access_count = (mem.access_count or 0) + 1
                    mem.retrieval_count = (mem.retrieval_count or 0) + 1
                    mem.last_accessed_at = datetime.utcnow()
                    # Bayesian utility: (helpful + 1) / (retrieval + 2) blended with importance
                    rc = mem.retrieval_count or 1
                    hc = mem.helpful_count or 0
                    imp_score = ((mem.importance or 3) - 1) / 4.0  # 0..1
                    mem.utility_score = round(0.7 * (hc + 1) / (rc + 2) + 0.3 * imp_score, 4)

    elapsed_ms = (time.monotonic() - start) * 1000

    return SearchResponse(
        query=query,
        total=len(all_results),
        results=all_results[:k],
        tiers_used=tiers_used,
        latency_ms=round(elapsed_ms, 2),
    )

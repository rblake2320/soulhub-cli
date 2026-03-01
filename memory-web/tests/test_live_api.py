"""
Live integration tests — run against a real server at MEMORYWEB_URL (default http://127.0.0.1:8100).

These tests use actual PostgreSQL data, not the SQLite mock used by the unit tests.
Skip them if the server is unreachable (CI without a running instance).

Run:
    pytest tests/test_live_api.py -v
    MEMORYWEB_URL=http://192.168.12.198:8100 pytest tests/test_live_api.py -v
"""

import pytest
import httpx

BASE = "http://127.0.0.1:8100"

# ---------------------------------------------------------------------------
# Session-scoped client — one connection pool for all tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def api():
    # Probe GET / (fast static HTML) not /api/status (slow — celery inspect adds ~4s).
    try:
        r = httpx.get(f"{BASE}/", timeout=5)
        r.raise_for_status()
    except Exception as exc:
        pytest.skip(f"Live server not reachable at {BASE}: {exc}")
    with httpx.Client(base_url=BASE, timeout=15) as client:
        yield client


# ---------------------------------------------------------------------------
# Provenance shape constants (derived from live DB, not invented)
# ---------------------------------------------------------------------------

PROVENANCE_KEYS = {
    "memory_id", "segment_id", "message_id", "source_id",
    "source_path", "char_offset_start", "char_offset_end", "derivation_type",
}

MEMORY_TOP_KEYS = {
    "id", "fact", "category", "confidence", "importance",
    "access_count", "created_at", "tombstoned_at", "provenance",
}

# Memory id=1 is the first synthesised memory: "techai uses opusplan for smart token usage."
# It exists in every non-wiped DB because it was ingested in the first session.
KNOWN_MEMORY_ID = 1


# ---------------------------------------------------------------------------
# GET /api/memories/{id} — the previously-broken endpoint
# ---------------------------------------------------------------------------

class TestMemoryDetail:
    def test_returns_200(self, api):
        r = api.get(f"/api/memories/{KNOWN_MEMORY_ID}")
        assert r.status_code == 200

    def test_top_level_shape(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        assert MEMORY_TOP_KEYS == set(d.keys())

    def test_scalar_fields_typed(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        assert isinstance(d["id"], int)
        assert isinstance(d["fact"], str) and len(d["fact"]) > 0
        assert isinstance(d["access_count"], int)
        assert d["tombstoned_at"] is None

    def test_provenance_is_list(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        assert isinstance(d["provenance"], list)

    def test_provenance_entry_has_all_keys(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        assert len(d["provenance"]) >= 1, "memory/1 must have at least one provenance entry"
        for entry in d["provenance"]:
            missing = PROVENANCE_KEYS - set(entry.keys())
            assert not missing, f"provenance entry missing keys: {missing}"

    def test_provenance_memory_id_matches(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        for entry in d["provenance"]:
            assert entry["memory_id"] == KNOWN_MEMORY_ID

    def test_provenance_source_path_nonempty(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        for entry in d["provenance"]:
            assert entry["source_path"], "source_path must be a non-empty string"

    def test_provenance_derivation_type_valid(self, api):
        d = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()
        valid = {"extracted", "synthesised", "synthesized", "manual"}
        for entry in d["provenance"]:
            assert entry["derivation_type"] in valid, (
                f"unexpected derivation_type: {entry['derivation_type']!r}"
            )

    def test_access_count_increments(self, api):
        """Two consecutive calls must yield a strictly increasing access_count."""
        before = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()["access_count"]
        after = api.get(f"/api/memories/{KNOWN_MEMORY_ID}").json()["access_count"]
        assert after == before + 1

    def test_404_for_nonexistent_id(self, api):
        r = api.get("/api/memories/999999999")
        assert r.status_code == 404
        assert r.json() == {"detail": "Memory not found"}

    def test_several_ids_all_200(self, api):
        """IDs 1–5 must all exist and return 200 with a non-empty fact."""
        for mid in range(1, 6):
            r = api.get(f"/api/memories/{mid}")
            assert r.status_code == 200, f"memory/{mid} returned {r.status_code}"
            assert r.json()["fact"], f"memory/{mid} has empty fact"


# ---------------------------------------------------------------------------
# GET /api/memories — list (no provenance field — uses MemoryOut not MemoryWithProvenance)
# ---------------------------------------------------------------------------

class TestMemoryList:
    def test_returns_200(self, api):
        r = api.get("/api/memories")
        assert r.status_code == 200

    def test_pagination_shape(self, api):
        d = api.get("/api/memories?page=1&page_size=20").json()
        assert {"total", "page", "page_size", "items"} == set(d.keys())
        assert d["total"] > 0
        assert len(d["items"]) <= 20

    def test_list_items_have_no_provenance_key(self, api):
        """List endpoint returns MemoryOut, not MemoryWithProvenance."""
        d = api.get("/api/memories?page_size=5").json()
        for item in d["items"]:
            assert "provenance" not in item, (
                "List items must not include provenance (use GET /api/memories/{id})"
            )

    def test_category_filter(self, api):
        d = api.get("/api/memories?category=preference").json()
        for item in d["items"]:
            assert item["category"] == "preference"

    def test_min_importance_filter(self, api):
        d = api.get("/api/memories?min_importance=5").json()
        for item in d["items"]:
            assert item["importance"] >= 5


# ---------------------------------------------------------------------------
# POST /api/search — shape + repeated calls (guards #loading regression)
# ---------------------------------------------------------------------------

SEARCH_RESPONSE_KEYS = {"query", "total", "results", "tiers_used", "latency_ms"}
SEARCH_RESULT_KEYS   = {"result_type", "id", "content", "score", "tier", "tags",
                         "provenance", "tombstoned"}

class TestSearch:
    def test_valid_search_200(self, api):
        r = api.post("/api/search", json={"query": "pgvector installation", "k": 5})
        assert r.status_code == 200

    def test_response_shape(self, api):
        d = api.post("/api/search", json={"query": "pgvector installation", "k": 5}).json()
        assert SEARCH_RESPONSE_KEYS == set(d.keys())

    def test_result_item_shape(self, api):
        d = api.post("/api/search", json={"query": "pgvector installation", "k": 5}).json()
        for res in d["results"]:
            missing = SEARCH_RESULT_KEYS - set(res.keys())
            assert not missing, f"search result missing keys: {missing}"

    def test_latency_ms_is_float(self, api):
        d = api.post("/api/search", json={"query": "postgres", "k": 3}).json()
        assert isinstance(d["latency_ms"], float)
        assert d["latency_ms"] > 0

    def test_tiers_used_valid(self, api):
        d = api.post("/api/search", json={"query": "postgres", "k": 3}).json()
        for t in d["tiers_used"]:
            assert t in (1, 2, 3)

    def test_repeated_searches_no_crash(self, api):
        """Guard against the #loading DOM regression — server must handle rapid consecutive POSTs."""
        for i in range(5):
            r = api.post("/api/search", json={"query": f"test query {i}", "k": 3})
            assert r.status_code == 200, f"search {i} failed with {r.status_code}: {r.text[:200]}"

    def test_empty_query_422(self, api):
        r = api.post("/api/search", json={"query": ""})
        assert r.status_code == 422

    def test_force_tier_1(self, api):
        d = api.post("/api/search", json={"query": "postgres", "k": 3, "force_tier": 1}).json()
        if d["results"]:
            assert d["tiers_used"] == [1]

    def test_force_tier_2(self, api):
        d = api.post("/api/search", json={"query": "postgres", "k": 3, "force_tier": 2}).json()
        if d["results"]:
            assert d["tiers_used"] == [2]


# ---------------------------------------------------------------------------
# GET /api/status — shape + pipeline_health present
# ---------------------------------------------------------------------------

class TestStatus:
    def test_returns_200(self, api):
        assert api.get("/api/status").status_code == 200

    def test_services_list(self, api):
        d = api.get("/api/status").json()
        assert isinstance(d["services"], list)
        names = {s["name"] for s in d["services"]}
        assert {"postgres", "pgvector"} <= names

    def test_stats_shape(self, api):
        st = api.get("/api/status").json()["stats"]
        for field in ("sources", "conversations", "messages", "segments",
                      "memories", "embeddings", "tombstoned_memories"):
            assert field in st
            assert isinstance(st[field], int)

    def test_pipeline_health_present(self, api):
        """pipeline_health must be in the response (added in Phase A)."""
        d = api.get("/api/status").json()
        assert "pipeline_health" in d
        ph = d["pipeline_health"]
        if ph is not None:
            for field in ("done", "pending", "running", "failed", "total"):
                assert field in ph
                assert isinstance(ph[field], int)
            assert ph["total"] == ph["done"] + ph["pending"] + ph["running"] + ph["failed"]

    def test_stats_memories_nonzero(self, api):
        """Sanity: real DB must have memories ingested."""
        st = api.get("/api/status").json()["stats"]
        assert st["memories"] > 0

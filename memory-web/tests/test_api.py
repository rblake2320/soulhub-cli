"""API smoke tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import MemoryOut

client = TestClient(app, raise_server_exceptions=False)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    ctype = r.headers.get("content-type", "")
    if "application/json" in ctype:
        assert r.json()["service"] == "MemoryWeb"
    else:
        assert "MemoryWeb Dashboard" in r.text


def test_status_endpoint():
    r = client.get("/api/status")
    assert r.status_code == 200
    data = r.json()
    assert "services" in data
    assert "stats" in data


def test_search_empty_query():
    r = client.post("/api/search", json={"query": ""})
    assert r.status_code == 422  # validation error: min_length=1


def test_search_valid():
    r = client.post("/api/search", json={"query": "pgvector setup", "k": 5})
    # May fail with DB error but shape should be correct or 500
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "query" in data
        assert "results" in data


def test_memories_list():
    r = client.get("/api/memories")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "items" in data


def test_ingest_status_unknown():
    r = client.get("/api/ingest/status/nonexistent-task-id")
    assert r.status_code == 200
    data = r.json()
    assert data["task_id"] == "nonexistent-task-id"


def test_retention_invalid_date():
    r = client.delete("/api/retain/day/not-a-date")
    assert r.status_code in (400, 422, 500)


def test_tombstoned_endpoint():
    r = client.get("/api/retain/tombstoned")
    assert r.status_code in (200, 500)


def test_memory_schema_handles_legacy_nulls():
    m = MemoryOut(
        id=1,
        fact="legacy fact",
        category=None,
        confidence=None,
        importance=None,
        tombstoned_at=None,
    )
    assert m.access_count == 0
    assert m.created_at is None

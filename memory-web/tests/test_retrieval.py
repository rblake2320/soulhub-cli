"""Tests for retrieval service (mocked DB)."""

import pytest
from unittest.mock import MagicMock, patch

from app.schemas import SearchResponse


@patch("app.services.retrieval.tier3_semantic", return_value=[])
@patch("app.services.retrieval.tier2_trigram", return_value=[])
@patch("app.services.retrieval.tier1_structured", return_value=[])
def test_search_returns_response(mock_t1, mock_t2, mock_t3):
    from app.services.retrieval import search
    with patch("app.services.retrieval.db_session"):
        result = search("test query", k=5)
    assert isinstance(result, SearchResponse)
    assert result.query == "test query"
    assert result.total == 0
    assert result.results == []


def test_search_response_schema():
    resp = SearchResponse(
        query="test",
        total=0,
        results=[],
        tiers_used=[],
        latency_ms=1.5,
    )
    assert resp.query == "test"
    assert resp.latency_ms == 1.5

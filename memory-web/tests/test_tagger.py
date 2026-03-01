"""Tests for the multi-axis tagger (mocked Ollama)."""

from unittest.mock import patch

import pytest

from app.pipelines.tagger import AXES, _build_tag_prompt


def test_tag_prompt_includes_all_axes():
    prompt = _build_tag_prompt("We are debugging a pgvector installation on PostgreSQL 16.")
    assert "domain" in prompt
    assert "intent" in prompt
    assert "sensitivity" in prompt
    assert "importance" in prompt
    assert "project" in prompt


def test_axes_definition():
    assert "domain" in AXES
    assert "infrastructure" in AXES["domain"]
    assert "debugging" in AXES["intent"]
    assert "public" in AXES["sensitivity"]

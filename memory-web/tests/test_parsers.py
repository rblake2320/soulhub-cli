"""Tests for parsers."""

import json
import tempfile
from pathlib import Path

import pytest

from app.parsers.claude_session import parse_session_file
from app.parsers.shared_chat import parse_shared_chat_file
from app.parsers.sqlite_memory import list_tables, import_journal_entries


def _make_session_file(tmp_path: Path) -> Path:
    lines = [
        json.dumps({
            "uuid": "aaa-111",
            "parentUuid": None,
            "type": "user",
            "message": {"role": "user", "content": "Hello, how do I install pgvector?"},
            "timestamp": "2025-01-15T10:00:00.000Z",
            "sessionId": "sess-abc",
        }),
        json.dumps({
            "uuid": "bbb-222",
            "parentUuid": "aaa-111",
            "type": "assistant",
            "message": {"role": "assistant", "content": "Download the DLL from the pgvector releases page."},
            "timestamp": "2025-01-15T10:00:05.000Z",
            "sessionId": "sess-abc",
        }),
    ]
    f = tmp_path / "sess-abc.jsonl"
    f.write_text("\n".join(lines))
    return f


def test_parse_session_file(tmp_path):
    f = _make_session_file(tmp_path)
    conv = parse_session_file(str(f))
    assert conv.external_id == "sess-abc"
    assert len(conv.messages) == 2
    assert conv.messages[0].role == "user"
    assert "pgvector" in conv.messages[0].content
    assert conv.started_at is not None


def test_parse_session_file_empty(tmp_path):
    f = tmp_path / "empty.jsonl"
    f.write_text("")
    conv = parse_session_file(str(f))
    assert len(conv.messages) == 0


def _make_shared_chat_file(tmp_path: Path) -> Path:
    content = """# [FROM: WindowsClaude] [TO: SparkDaemon]
**Time:** 2025-01-15 10:30:00
**Subject:** pgvector installation status

Has pgvector been installed on Spark-1 yet?
"""
    f = tmp_path / "msg_001.md"
    f.write_text(content)
    return f


def test_parse_shared_chat_file(tmp_path):
    f = _make_shared_chat_file(tmp_path)
    msg = parse_shared_chat_file(str(f))
    assert msg is not None
    assert msg.from_agent == "WindowsClaude"
    assert msg.to_agent == "SparkDaemon"
    assert msg.subject == "pgvector installation status"
    assert "pgvector" in msg.body


def test_parse_shared_chat_missing_file(tmp_path):
    msg = parse_shared_chat_file(str(tmp_path / "nonexistent.md"))
    assert msg is None


def test_list_tables_nonexistent():
    tables = list_tables("/nonexistent/path.db")
    assert tables == []

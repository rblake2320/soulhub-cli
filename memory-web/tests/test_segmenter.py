"""Tests for the heuristic segmenter."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.pipelines.segmenter import heuristic_segment


def _make_msg(ordinal, sent_at=None):
    m = MagicMock()
    m.ordinal = ordinal
    m.sent_at = sent_at
    m.content = f"Message {ordinal}"
    return m


def test_heuristic_single_message():
    msgs = [_make_msg(0, datetime(2025, 1, 1, 10, 0))]
    segs = heuristic_segment(msgs)
    assert len(segs) == 1
    assert segs[0][0] == 0
    assert segs[0][1] == 0


def test_heuristic_time_gap_split():
    t = datetime(2025, 1, 1, 10, 0)
    msgs = [
        _make_msg(0, t),
        _make_msg(1, t + timedelta(minutes=5)),
        _make_msg(2, t + timedelta(hours=2)),  # > 30 min gap
        _make_msg(3, t + timedelta(hours=2, minutes=2)),
    ]
    segs = heuristic_segment(msgs)
    assert len(segs) == 2


def test_heuristic_max_count_split():
    t = datetime(2025, 1, 1, 10, 0)
    msgs = [_make_msg(i, t + timedelta(minutes=i)) for i in range(25)]
    segs = heuristic_segment(msgs)
    # Should split after 20 messages
    assert len(segs) >= 2


def test_heuristic_empty():
    assert heuristic_segment([]) == []

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from Engines.Analysis.canonical import (
    CanonicalizationError,
    canonical_json_bytes,
    semantic_fingerprint,
)


def test_mapping_order_does_not_change_fingerprint():
    assert semantic_fingerprint({"b": 2, "a": 1}) == semantic_fingerprint({"a": 1, "b": 2})


def test_runtime_telemetry_does_not_change_fingerprint():
    first = {"result": {"x": 1}, "elapsed_seconds": 1.2, "worker_id": "worker-a"}
    second = {"result": {"x": 1}, "elapsed_seconds": 9.7, "worker_id": "worker-b"}
    assert semantic_fingerprint(first) == semantic_fingerprint(second)


def test_timezone_normalizes_to_utc():
    value = {"t": datetime(2026, 8, 7, 19, 0, tzinfo=timezone.utc)}
    assert b"2026-08-07T19:00:00Z" in canonical_json_bytes(value)


def test_naive_datetime_is_rejected():
    with pytest.raises(CanonicalizationError, match="Naive datetime"):
        canonical_json_bytes({"t": datetime(2026, 8, 7, 19, 0)})


def test_non_finite_float_is_rejected():
    with pytest.raises(CanonicalizationError, match="Non-finite"):
        canonical_json_bytes({"x": float("nan")})

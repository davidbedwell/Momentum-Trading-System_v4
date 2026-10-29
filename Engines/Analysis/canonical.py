from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence


NON_SEMANTIC_KEYS = frozenset(
    {
        "elapsed_seconds",
        "worker_id",
        "process_id",
        "temporary_path",
        "local_cache_path",
        "memory_usage",
        "cpu_usage",
    }
)


class CanonicalizationError(ValueError):
    """Raised when scientific content cannot be canonically serialized."""


def _iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise CanonicalizationError("Naive datetime is not allowed in canonical scientific content")
    normalized = value.astimezone(timezone.utc)
    return normalized.isoformat().replace("+00:00", "Z")


def canonical_data(value: Any, *, exclude_keys: frozenset[str] = NON_SEMANTIC_KEYS) -> Any:
    """Convert scientific content to a deterministic JSON-compatible structure."""
    if is_dataclass(value):
        return canonical_data(asdict(value), exclude_keys=exclude_keys)

    if isinstance(value, Enum):
        return canonical_data(value.value, exclude_keys=exclude_keys)

    if isinstance(value, datetime):
        return _iso_utc(value)

    if isinstance(value, date):
        return value.isoformat()

    if value is None or isinstance(value, (str, bool, int)):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalizationError("Non-finite float is not allowed in canonical scientific content")
        # JSON's stable finite numeric representation is sufficient for Phase A.
        return value

    if isinstance(value, Mapping):
        normalized = {}
        for key, item in value.items():
            key = str(key)
            if key in exclude_keys:
                continue
            normalized[key] = canonical_data(item, exclude_keys=exclude_keys)
        return {key: normalized[key] for key in sorted(normalized)}

    if isinstance(value, (set, frozenset)):
        normalized = [canonical_data(item, exclude_keys=exclude_keys) for item in value]
        return sorted(
            normalized,
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        )

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [canonical_data(item, exclude_keys=exclude_keys) for item in value]

    if hasattr(value, "to_dict") and callable(value.to_dict):
        return canonical_data(value.to_dict(), exclude_keys=exclude_keys)

    raise CanonicalizationError(f"Unsupported canonical value type: {type(value)!r}")


def canonical_json_bytes(value: Any) -> bytes:
    data = canonical_data(value)
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def semantic_fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()

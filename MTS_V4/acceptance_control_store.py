from __future__ import annotations

import hashlib
from typing import Mapping, Sequence

from .derived_market_store import DerivedFeatureDefinition, DerivedFeatureSetDefinition


NEGATIVE_CONTROL_FEATURE_SET_ID = "mts_acceptance_negative_control"
NEGATIVE_CONTROL_FEATURE_SET_VERSION = "v1"
NEGATIVE_CONTROL_COLUMN = "deterministic_null__v1"


def negative_control_feature_set() -> DerivedFeatureSetDefinition:
    return DerivedFeatureSetDefinition(
        feature_set_id=NEGATIVE_CONTROL_FEATURE_SET_ID,
        version=NEGATIVE_CONTROL_FEATURE_SET_VERSION,
        description="Identity/date-hash neutral measurement isolated for blinded scientific negative-control calibration.",
        features=(
            DerivedFeatureDefinition(
                feature_id="deterministic_null",
                version="v1",
                description="Deterministic SHA-256 security/date hash mapped to [0,1]; contains no market measurement.",
                dependencies=("SECURITY_ID", "EFFECTIVE_DATE"),
                required_lookback_sessions=0,
                classification="CONTEXT",
                attributes={"acceptance_negative_control": True, "market_measurement_used": False},
            ),
        ),
        attributes={"acceptance_control_only": True, "expected_result_exposed_to_rd": False},
    )


def build_negative_control_rows(rows: Sequence[Mapping[str, object]], *, salt: str = "MTS_V4_ACCEPTANCE_NULL_V1"):
    output = []
    seen = set()
    for raw in rows:
        security_id = str(raw.get("security_id", "")).strip()
        effective_date = str(raw.get("effective_date", "")).strip()
        if not security_id or not effective_date:
            raise ValueError("negative-control source row requires security_id and effective_date")
        key = (security_id, effective_date)
        if key in seen:
            raise ValueError(f"duplicate negative-control identity: {security_id} {effective_date}")
        seen.add(key)
        token = f"{salt}|{security_id}|{effective_date}".encode("utf-8")
        integer = int.from_bytes(hashlib.sha256(token).digest()[:8], "big")
        output.append(
            {
                "security_id": security_id,
                "effective_date": effective_date,
                "eligible": bool(raw.get("eligible", True)),
                NEGATIVE_CONTROL_COLUMN: integer / float(2**64 - 1),
            }
        )
    return tuple(output)

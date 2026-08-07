
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from Core.research_nexus import (
    ResearchNexusConfig,
    SchemaRegistry,
    SchemaValidator,
    build_research_nexus,
)
from Engines.Intake import (
    IntakeEngine,
    IntakeRequest,
    ResearchNexusIntakePublisher,
)
from Engines.Intake.adapters import DataFrameAdapter
from Engines.Intake.nexus_adapter import (
    canonical_payload_bytes,
    deterministic_artifact_id,
    market_history_payload,
)


def source_frame(n: int = 320) -> pd.DataFrame:
    close = pd.Series(np.linspace(100.0, 150.0, n))
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC"),
        "open": close - 0.2,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": np.arange(n, dtype=float) + 1000.0,
    })


def artifact():
    return IntakeEngine().process(
        DataFrameAdapter(source_frame(), source_id="fixture"),
        IntakeRequest(symbol="AAPL", timeframe="1D"),
    )


def test_market_history_schema_is_governed_and_resolvable():
    schema = SchemaRegistry().get("mts.market-history", 1)
    assert schema.schema_id == "mts.market-history"
    assert schema.schema_version == 1


def test_payload_validates_against_governed_schema():
    item = artifact()
    payload = market_history_payload(item)
    SchemaValidator().validate(
        payload,
        schema_id="mts.market-history",
        schema_version=1,
    )


def test_semantic_fingerprint_is_not_artifact_version():
    item = artifact()
    assert len(item.semantic_fingerprint) == 64
    assert isinstance(item.semantic_fingerprint, str)


def test_opaque_artifact_identity_is_retry_stable():
    item = artifact()
    first = deterministic_artifact_id(item.semantic_fingerprint)
    second = deterministic_artifact_id(item.semantic_fingerprint)
    assert first == second
    assert first.startswith("artifact:")
    assert "AAPL" not in first
    assert "1D" not in first


def test_payload_serialization_is_deterministic():
    item = artifact()
    payload = market_history_payload(item)
    assert canonical_payload_bytes(payload) == canonical_payload_bytes(payload)


def test_publish_retrieve_verify_and_idempotent_retry(tmp_path):
    nexus = build_research_nexus(
        ResearchNexusConfig(tmp_path / "nexus-runtime")
    )
    publisher = ResearchNexusIntakePublisher(nexus)
    item = artifact()

    first = publisher.publish_intake_artifact(item)
    second = publisher.publish_intake_artifact(item)

    assert first.artifact_ref == second.artifact_ref
    assert first.artifact_ref.artifact_version == 1
    assert second.reconciled is True

    retrieved = nexus.get(first.artifact_ref)
    expected = canonical_payload_bytes(market_history_payload(item))
    assert retrieved.payload == expected
    nexus.verify(first.artifact_ref)

    decoded = json.loads(retrieved.payload)
    assert decoded["symbol"] == "AAPL"
    assert decoded["timeframe"] == "1D"
    assert decoded["semantic_fingerprint"] == item.semantic_fingerprint

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from Engines.Intake import (
    IntakeEngine,
    IntakeRequest,
    MaterializationMode,
    MaterializationPolicy,
)
from Engines.Intake.adapters import DataFrameAdapter
from Engines.Intake.publisher import PublicationNotConfigured


def source_frame(n: int = 320) -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    close = pd.Series(np.linspace(100.0, 150.0, n))
    return pd.DataFrame({
        "date": dates,
        "open": close - 0.2,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": np.arange(n, dtype=float) + 1000.0,
    })


def test_intake_processes_observations_and_measurements():
    artifact = IntakeEngine().process(
        DataFrameAdapter(source_frame(), source_id="fixture"),
        IntakeRequest(symbol="AAPL", timeframe="1D"),
    )
    assert artifact.symbol == "AAPL"
    assert artifact.quality_report["status"] == "PASSED"
    assert "sma_20" in artifact.observations.columns
    assert "dollar_volume" in artifact.observations.columns
    assert len(artifact.measurement_columns) > 0
    assert artifact.provenance["temporal_classification"]["observations"] == "OBSERVED"
    assert (
        artifact.provenance["temporal_classification"]["measurements"]
        == "DERIVED_CONTEMPORANEOUS"
    )


def test_observations_only_is_lean_intake_policy():
    policy = MaterializationPolicy(mode=MaterializationMode.OBSERVATIONS_ONLY)
    artifact = IntakeEngine().process(
        DataFrameAdapter(source_frame(), source_id="fixture"),
        IntakeRequest(symbol="AAPL", timeframe="1D", policy=policy),
    )
    assert tuple(artifact.observations.columns) == (
        "date", "open", "high", "low", "close", "volume"
    )
    assert artifact.measurement_columns == ()


def test_explicit_measurement_policy():
    policy = MaterializationPolicy(
        mode=MaterializationMode.EXPLICIT_MEASUREMENTS,
        measurement_names=("sma_20", "dollar_volume"),
    )
    artifact = IntakeEngine().process(
        DataFrameAdapter(source_frame(), source_id="fixture"),
        IntakeRequest(symbol="AAPL", timeframe="1D", policy=policy),
    )
    assert artifact.measurement_columns == ("sma_20", "dollar_volume")


def test_identical_intake_has_identical_semantic_fingerprint():
    engine = IntakeEngine()
    request = IntakeRequest(symbol="AAPL", timeframe="1D")
    a = engine.process(
        DataFrameAdapter(source_frame(), source_id="fixture"), request
    )
    b = engine.process(
        DataFrameAdapter(source_frame(), source_id="fixture"), request
    )
    assert a.semantic_fingerprint == b.semantic_fingerprint
    assert len(a.semantic_fingerprint) == 64


def test_malformed_ohlc_rejected_before_publication():
    df = source_frame()
    df.loc[10, "high"] = 1.0
    with pytest.raises(ValueError, match="Malformed canonical OHLCV"):
        IntakeEngine().process(
            DataFrameAdapter(df, source_id="bad"),
            IntakeRequest(symbol="AAPL", timeframe="1D"),
        )


def test_duplicate_timestamp_rejected():
    df = source_frame()
    df.loc[10, "date"] = df.loc[9, "date"]
    with pytest.raises(ValueError, match="duplicate_dates"):
        IntakeEngine().process(
            DataFrameAdapter(df, source_id="bad"),
            IntakeRequest(symbol="AAPL", timeframe="1D"),
        )


def test_no_nexus_publisher_means_no_durable_publish():
    artifact = IntakeEngine().process(
        DataFrameAdapter(source_frame(), source_id="fixture"),
        IntakeRequest(symbol="AAPL", timeframe="1D"),
    )
    with pytest.raises(PublicationNotConfigured):
        IntakeEngine().publish(artifact)


class RecordingPublisher:
    def __init__(self):
        self.artifacts = []

    def publish_intake_artifact(self, artifact):
        self.artifacts.append(artifact)
        return {
            "published": True,
            "semantic_fingerprint": artifact.semantic_fingerprint,
        }


def test_run_uses_publication_port_without_assuming_nexus_identity():
    publisher = RecordingPublisher()
    result = IntakeEngine(publisher=publisher).run(
        DataFrameAdapter(source_frame(), source_id="fixture"),
        IntakeRequest(symbol="AAPL", timeframe="1D"),
    )
    assert len(publisher.artifacts) == 1
    assert result.nexus_reference["published"] is True
    assert (
        result.nexus_reference["semantic_fingerprint"]
        == result.artifact.semantic_fingerprint
    )

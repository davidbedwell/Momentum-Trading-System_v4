from __future__ import annotations

import pytest

from MTS_V4.blind_validation import (
    BlindValidationError,
    HistoricalBlindValidationSession,
    HistoricalEvidenceWindow,
)
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import EvidenceDescriptor, SubjectMetadata


def _fixture():
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
    cache = TemporaryResearchCache()
    cache.put(
        "source:ohlcv",
        (
            {"date": "2026-01-01", "close": 100.0},
            {"date": "2026-01-02", "close": 101.0},
            {"date": "2026-01-05", "close": 120.0},
            {"date": "2026-01-06", "close": 90.0},
        ),
    )
    evidence = EvidenceDescriptor(
        evidence_id="evidence:equity:AAPL:ohlcv",
        subject_id="equity:AAPL",
        evidence_type="OHLCV",
        artifact_type="NORMALIZED_ROW_DATASET",
        source_identity="fixture",
        coverage_start="2026-01-01",
        coverage_end="2026-01-06",
        row_count=4,
        schema=("date", "close"),
        cache_key="source:ohlcv",
    )
    return subject, cache, evidence


def test_prediction_view_physically_withholds_post_cutoff_rows_and_metadata():
    subject, cache, evidence = _fixture()
    session = HistoricalBlindValidationSession.build(
        trial_id="trial:1",
        hypothesis_id="H-1",
        subject=subject,
        evidence=(evidence,),
        source_cache=cache,
        windows=(
            HistoricalEvidenceWindow(
                evidence_id=evidence.evidence_id,
                time_field="date",
                cutoff="2026-01-02",
                outcome_end="2026-01-06",
            ),
        ),
    )

    blind_descriptor = session.evidence[0]
    visible_rows = session.cache.get(blind_descriptor.cache_key)

    assert visible_rows == (
        {"date": "2026-01-01", "close": 100.0},
        {"date": "2026-01-02", "close": 101.0},
    )
    assert blind_descriptor.row_count == 2
    assert blind_descriptor.coverage_end == "2026-01-02"
    assert blind_descriptor.provenance["blind_validation"]["future_rows_withheld"] is True
    assert session.audits[0].withheld_row_count == 2


def test_outcomes_cannot_be_revealed_before_prediction_lock_and_prediction_is_frozen():
    subject, cache, evidence = _fixture()
    session = HistoricalBlindValidationSession.build(
        trial_id="trial:1",
        hypothesis_id="H-1",
        subject=subject,
        evidence=(evidence,),
        source_cache=cache,
        windows=(
            HistoricalEvidenceWindow(
                evidence_id=evidence.evidence_id,
                time_field="date",
                cutoff="2026-01-02",
                outcome_end="2026-01-06",
            ),
        ),
    )

    with pytest.raises(BlindValidationError, match="before the prediction is locked"):
        session.reveal_outcomes()

    session.lock_prediction("AAPL will rise during the frozen horizon.")
    assert session.prediction_locked is True
    assert session.prediction_statement == "AAPL will rise during the frozen horizon."

    with pytest.raises(BlindValidationError, match="cannot be revised"):
        session.lock_prediction("AAPL will fall instead.")

    revealed = session.reveal_outcomes()
    assert revealed[evidence.evidence_id] == (
        {"date": "2026-01-05", "close": 120.0},
        {"date": "2026-01-06", "close": 90.0},
    )


def test_blind_session_uses_isolated_nexus_and_exposes_only_frozen_hypothesis_context():
    subject, cache, evidence = _fixture()
    session = HistoricalBlindValidationSession.build(
        trial_id="trial:1",
        hypothesis_id="H-1",
        subject=subject,
        evidence=(evidence,),
        source_cache=cache,
        windows=(
            HistoricalEvidenceWindow(
                evidence_id=evidence.evidence_id,
                time_field="date",
                cutoff="2026-01-02",
            ),
        ),
    )

    assert session.nexus.findings_for_subject(subject.subject_id) == ()
    assert session.nexus.analysis_result_metadata_for_subject(subject.subject_id) == ()

    context = session.blind_context(
        hypothesis_statement="Condition A predicts expansion.",
        success_definition="The frozen outcome occurs within the frozen horizon.",
    )
    assert context["blind_validation"] is True
    assert context["prediction_locked"] is False
    assert context["exploratory_rp_or_nexus_memory_included"] is False
    assert context["frozen_hypothesis"] == {
        "statement": "Condition A predicts expansion.",
        "success_definition": "The frozen outcome occurs within the frozen horizon.",
    }


def test_every_supplied_evidence_requires_an_explicit_window():
    subject, cache, evidence = _fixture()
    with pytest.raises(BlindValidationError, match="exactly one window"):
        HistoricalBlindValidationSession.build(
            trial_id="trial:1",
            hypothesis_id="H-1",
            subject=subject,
            evidence=(evidence,),
            source_cache=cache,
            windows=(),
        )


def test_numeric_temporal_fields_are_supported_without_inference():
    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
    cache = TemporaryResearchCache()
    cache.put(
        "source:flow",
        (
            {"ts": 1000, "premium": 10.0},
            {"ts": 2000, "premium": 20.0},
            {"ts": 3000, "premium": 30.0},
        ),
    )
    evidence = EvidenceDescriptor(
        evidence_id="evidence:equity:AAPL:flow",
        subject_id="equity:AAPL",
        evidence_type="FLOW",
        artifact_type="NORMALIZED_ROW_DATASET",
        source_identity="fixture",
        coverage_start="1000",
        coverage_end="3000",
        row_count=3,
        schema=("ts", "premium"),
        cache_key="source:flow",
    )
    session = HistoricalBlindValidationSession.build(
        trial_id="trial:numeric",
        hypothesis_id="H-num",
        subject=subject,
        evidence=(evidence,),
        source_cache=cache,
        windows=(
            HistoricalEvidenceWindow(
                evidence_id=evidence.evidence_id,
                time_field="ts",
                cutoff=2000,
            ),
        ),
    )
    assert session.cache.get(session.evidence[0].cache_key) == (
        {"ts": 1000, "premium": 10.0},
        {"ts": 2000, "premium": 20.0},
    )

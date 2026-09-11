from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from MTS_V4.blind_validation import HistoricalBlindValidationSession, HistoricalEvidenceWindow
from MTS_V4.blind_validation_runtime import build_blind_prediction_orchestrator
from MTS_V4.bootstrap import build_runtime
from MTS_V4.contracts import EvidenceDescriptor, SubjectMetadata
from MTS_V4.research_package_store import JsonResearchPackageStore


class _UnusedRD:
    def begin_research(self, **kwargs):
        raise AssertionError("not used")

    def resume_research(self, **kwargs):
        raise AssertionError("not used")

    def repair_request(self, **kwargs):
        raise AssertionError("not used")

    def interpret_result(self, **kwargs):
        raise AssertionError("not used")


def test_blind_runtime_accepts_explicit_provider_without_rd_environment() -> None:
    runtime = build_runtime(rd=_UnusedRD())
    subject = SubjectMetadata(subject_id="equity:MSFT", ticker="MSFT")
    descriptor = EvidenceDescriptor(
        evidence_id="evidence:MSFT:ohlcv",
        subject_id=subject.subject_id,
        evidence_type="OHLCV",
        artifact_type="NORMALIZED_DATASET",
        source_identity="fixture",
        coverage_start="2026-01-01",
        coverage_end="2026-01-03",
        row_count=3,
        schema=("date", "close"),
        cache_key="cache:MSFT",
    )
    runtime.cache.put(
        descriptor.cache_key,
        (
            {"date": "2026-01-01", "close": 100.0},
            {"date": "2026-01-02", "close": 99.0},
            {"date": "2026-01-03", "close": 101.0},
        ),
    )
    session = HistoricalBlindValidationSession.build(
        trial_id="trial:MSFT:1",
        hypothesis_id="hyp:test",
        subject=subject,
        evidence=(descriptor,),
        source_cache=runtime.cache,
        windows=(
            HistoricalEvidenceWindow(
                evidence_id=descriptor.evidence_id,
                time_field="date",
                cutoff="2026-01-02",
                outcome_end="2026-01-03",
            ),
        ),
    )

    with tempfile.TemporaryDirectory() as tmp, patch.dict(
        os.environ,
        {"MTS_RD_BASE_URL": "", "MTS_RD_MODEL": "", "MTS_RD_API_KEY": ""},
        clear=False,
    ):
        orchestrator = build_blind_prediction_orchestrator(
            session=session,
            runtime=runtime,
            research_package_store=JsonResearchPackageStore(Path(tmp) / "packages"),
            hypothesis_statement="If triggered, price will finish higher after one session.",
            success_definition="Outcome close is greater than cutoff close.",
            base_url="https://api.openai.com",
            model="gpt-5.6-sol",
            api_key="dummy",
        )

    assert orchestrator._rd._base_url == "https://api.openai.com"
    assert orchestrator._rd._model == "gpt-5.6-sol"
    assert orchestrator._rd._api_key == "dummy"

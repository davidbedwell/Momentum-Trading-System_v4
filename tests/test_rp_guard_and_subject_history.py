from __future__ import annotations

import json

import pytest

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope
from MTS_V4.cross_subject_memory import (
    InMemoryCrossSubjectScientificMemory,
    ScientificMemoryRecord,
)
from MTS_V4.research_package import ResearchPackage, ResearchPackageError
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.subject_selection import SolAdaptiveSubjectSelector


class StubRD:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls = []

    def _chat_completion(self, messages):
        self.calls.append(messages)
        return json.dumps(self.response)


def test_research_package_allows_scalar_rows_as_aggregate_sample_count(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "packages")
    package = ResearchPackage(
        rp_id="rp-1",
        subject_id="equity:NVDA",
        campaign_id="campaign-1",
        originating_question="Do severe down moves rebound?",
        originating_rationale="Explore a candidate relationship.",
    )
    store.create(package)

    evolved = package.append_finding(
        {
            "finding_id": "F-1",
            "summary": "Severe group descriptive result.",
            "severe_group": {
                "rows": 71,
                "positive_finishes": 49,
                "positive_finish_fraction": 0.690141,
            },
            "nonsevere_group": {
                "rows": 420,
                "positive_finishes": 232,
                "positive_finish_fraction": 0.552381,
            },
        }
    )
    store.save(evolved)

    loaded = store.load("rp-1")
    assert loaded is not None
    assert loaded.findings[0]["severe_group"]["rows"] == 71
    assert loaded.findings[0]["nonsevere_group"]["rows"] == 420


def test_research_package_rejects_structured_raw_rows_collection(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "packages")
    package = ResearchPackage(
        rp_id="rp-raw",
        subject_id="equity:NVDA",
        campaign_id="campaign-raw",
        originating_question="Bad raw persistence attempt",
        originating_rationale="Regression fixture.",
        findings=(
            {
                "finding_id": "F-RAW",
                "rows": [
                    {"date": "2026-09-01", "close": 100.0},
                    {"date": "2026-09-02", "close": 101.0},
                ],
            },
        ),
    )
    with pytest.raises(ResearchPackageError, match="raw/cache evidence data"):
        store.create(package)


def test_research_package_rejects_payload_or_cache_key_anywhere(tmp_path):
    store = JsonResearchPackageStore(tmp_path / "packages")
    payload_package = ResearchPackage(
        rp_id="rp-payload",
        subject_id="equity:NVDA",
        campaign_id="campaign-payload",
        originating_question="Bad payload persistence attempt",
        originating_rationale="Regression fixture.",
        findings=({"finding_id": "F-P", "details": {"payload": {"x": 1}}},),
    )
    with pytest.raises(ResearchPackageError, match="raw/cache evidence data"):
        store.create(payload_package)

    cache_package = ResearchPackage(
        rp_id="rp-cache",
        subject_id="equity:NVDA",
        campaign_id="campaign-cache",
        originating_question="Bad cache persistence attempt",
        originating_rationale="Regression fixture.",
        findings=({"finding_id": "F-C", "details": {"cache_key": "abc"}},),
    )
    with pytest.raises(ResearchPackageError, match="raw/cache evidence data"):
        store.create(cache_package)


def test_selector_distinguishes_completed_incomplete_exposure_and_unseen_subjects():
    memory = InMemoryCrossSubjectScientificMemory()
    memory.publish(
        ScientificMemoryRecord(
            record_id="aapl-record",
            subject_id="equity:AAPL",
            kind="FINDING",
            summary="AAPL completed scientific memory.",
        )
    )
    memory.publish(
        ScientificMemoryRecord(
            record_id="msft-record",
            subject_id="equity:MSFT",
            kind="FINDING",
            summary="MSFT completed scientific memory.",
        )
    )
    rd = StubRD(
        {
            "subject_id": "equity:NVDA",
            "rationale": "Use an unexposed discriminator next.",
            "mode": "EXPLORATION",
            "hypothesis_id": None,
        }
    )
    selector = SolAdaptiveSubjectSelector(
        rd=rd,
        scientific_memory=memory,
        eligibility=SubjectEligibilityEnvelope(
            approved_subject_ids=frozenset(
                {"equity:AAPL", "equity:MSFT", "equity:XOM", "equity:NVDA"}
            )
        ),
        validatable_hypothesis_ids=frozenset(),
    )

    selector.choose_next(
        mission="predict T+1 onward",
        previously_seen=("equity:AAPL", "equity:MSFT", "equity:XOM"),
        candidate_subject_ids=("equity:AAPL", "equity:MSFT", "equity:XOM", "equity:NVDA"),
    )

    payload = json.loads(rd.calls[0][1]["content"])
    history = payload["subject_history_by_subject"]
    assert history["equity:AAPL"]["status"] == "COMPLETED_RESEARCH_WITH_DURABLE_MEMORY"
    assert history["equity:MSFT"]["status"] == "COMPLETED_RESEARCH_WITH_DURABLE_MEMORY"
    assert history["equity:XOM"]["status"] == "PRIOR_EXPOSURE_WITHOUT_DURABLE_COMPLETED_RESEARCH"
    assert history["equity:NVDA"]["status"] == "UNEXPOSED"
    assert history["equity:XOM"]["retrospective_blind_validation_eligible"] is False
    assert history["equity:NVDA"]["retrospective_blind_validation_eligible"] is True
    assert payload["prior_exposure_subject_ids"] == ["equity:AAPL", "equity:MSFT", "equity:XOM"]

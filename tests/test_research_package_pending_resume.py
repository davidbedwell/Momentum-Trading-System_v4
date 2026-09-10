from __future__ import annotations

from dataclasses import asdict, replace
import json

from MTS_V4.contracts import AnalysisRequest, ResearchDecision, ResearchPhase
from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage, ResearchQuestionRecord
from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector
from MTS_V4.research_package_store import JsonResearchPackageStore


def _request(*, request_id: str = "req:pending", parameters=None) -> AnalysisRequest:
    return AnalysisRequest(
        request_id=request_id,
        subject_id="equity:AAPL",
        question="Check aligned dark-pool data integrity",
        method_id="analysis.descriptive.statistics",
        evidence_ids=(),
        analysis_inputs=(),
        parameters=parameters or {"columns": ["dark_pool_volume_sum", "close"]},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Confirm the aligned columns are numeric and usable.",
        rp_id="RP-0001",
        question_id="Q-0002",
        parent_question_id="Q-0001",
        parent_rp_id=None,
    )


def _store_with_pending_request(tmp_path, request: AnalysisRequest) -> JsonResearchPackageStore:
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    package = ResearchPackage(
        rp_id="RP-0001",
        subject_id="equity:AAPL",
        campaign_id="campaign:aapl",
        originating_question="Initial question",
        originating_rationale="Initial rationale",
    )
    store.create(package)
    package = package.append_question(
        ResearchQuestionRecord(
            question_id="Q-0001",
            question="Initial question",
            rationale="Initial rationale",
            research_phase="EXPLORATION",
        )
    )
    package = package.append_question(
        ResearchQuestionRecord(
            question_id=request.question_id,
            parent_question_id=request.parent_question_id,
            question=request.question,
            rationale=request.rationale,
            research_phase=request.research_phase.value,
        )
    )
    package = package.append_analysis(
        ResearchAnalysisRecord(
            request_id=request.request_id,
            question_id=request.question_id,
            method_id=request.method_id,
            parameters=dict(request.parameters),
            evidence_ids=tuple(request.evidence_ids),
            analysis_inputs=tuple(asdict(item) for item in request.analysis_inputs),
            research_phase=request.research_phase.value,
        )
    )
    store.save(package)
    return store


def _provider(store: JsonResearchPackageStore) -> ResearchPackageAwareResearchDirector:
    return ResearchPackageAwareResearchDirector(
        research_package_store=store,
        base_url="http://example.invalid",
        model="test-model",
    )


def _resume_payload(prior: ResearchDecision):
    return {
        "subject": {"subject_id": "equity:AAPL"},
        "prior_decision": ResearchPackageAwareResearchDirector._json_safe(asdict(prior)),
    }


def test_exact_pending_request_id_is_allowed_only_for_resume(tmp_path):
    request = _request()
    store = _store_with_pending_request(tmp_path, request)
    provider = _provider(store)
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        next_request=request,
    )

    defect = provider._decision_representation_defect(
        "RESUME_RESEARCH",
        decision,
        _resume_payload(decision),
    )

    assert defect is None


def test_changed_pending_request_requires_fresh_request_id_on_resume(tmp_path):
    pending = _request()
    store = _store_with_pending_request(tmp_path, pending)
    provider = _provider(store)
    prior = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        next_request=pending,
    )
    changed = replace(pending, parameters={"columns": ["close"]})
    decision = replace(prior, next_request=changed)

    defect = provider._decision_representation_defect(
        "RESUME_RESEARCH",
        decision,
        _resume_payload(prior),
    )

    assert defect == (
        "next_request.request_id belongs to a durable pending request, but RESUME_RESEARCH "
        "changed that request's execution identity; any changed request requires a new request_id: "
        "req:pending"
    )


def test_pending_request_id_is_still_rejected_outside_resume(tmp_path):
    request = _request()
    store = _store_with_pending_request(tmp_path, request)
    provider = _provider(store)
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        analysis_interpretation="The result motivates another execution.",
        next_request=request,
    )

    defect = provider._decision_representation_defect(
        "INTERPRET_ANALYSIS_RESULT",
        decision,
        {"analysis_request": {"rp_id": "RP-0001"}},
    )

    assert defect == (
        "next_request.request_id has already been durably used; every new Analysis "
        "execution attempt requires a new request_id: req:pending"
    )


def test_completed_request_id_is_rejected_even_on_resume(tmp_path):
    request = _request()
    store = _store_with_pending_request(tmp_path, request)
    package = store.load("RP-0001")
    assert package is not None
    store.save(
        package.record_analysis_outcome(
            request_id=request.request_id,
            result_id="analysis-result:completed",
            execution_status="SUCCESS",
            interpretation="Completed.",
        )
    )
    provider = _provider(store)
    decision = ResearchDecision(
        continue_research=True,
        rp_id="RP-0001",
        next_request=request,
    )

    defect = provider._decision_representation_defect(
        "RESUME_RESEARCH",
        decision,
        _resume_payload(decision),
    )

    assert defect == (
        "next_request.request_id has already been durably used; every new Analysis "
        "execution attempt requires a new request_id: req:pending"
    )


def test_rd_prompt_explains_exact_pending_resume_exception():
    messages = ResearchPackageAwareResearchDirector._decision_messages(
        operation="RESUME_RESEARCH",
        mission="test",
        payload={
            "subject": {"subject_id": "equity:AAPL"},
            "prior_decision": {},
        },
    )

    system_text = messages[0]["content"]
    user = json.loads(messages[1]["content"])
    instruction_text = " ".join(user["instructions"])

    assert "checkpointed pending request is reserved rather than completed" in system_text
    assert "during RESUME_RESEARCH only" in system_text
    assert "Recovery exception: during RESUME_RESEARCH only" in instruction_text
    assert "every request field remains identical" in instruction_text
    assert "assign a fresh request_id" in instruction_text

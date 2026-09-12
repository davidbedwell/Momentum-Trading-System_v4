from __future__ import annotations

from datetime import date, timedelta
import json

from MTS_V4.prospective_validation import (
    JsonProspectiveValidationStore,
    ProspectiveValidationFrontier,
    ProspectiveValidationProtocol,
)
from MTS_V4.prospective_validation_runtime import (
    AuthoritativeSession,
    PublicConditionObservation,
    advance_matching_runtime,
    build_public_condition_feed,
    compile_execution_plan,
    derive_pairs,
    load_public_condition_feed,
    save_public_condition_feed,
)
from MTS_V4.research_package import PredictiveHypothesisRecord, ResearchPackage
from MTS_V4.research_package_store import JsonResearchPackageStore


def _protocol() -> ProspectiveValidationProtocol:
    statement = (
        "For AMD-like daily equity observations, an instrument closing at or above "
        "its trailing 20-session simple moving average has a higher subsequent "
        "10-session terminal return than a contemporaneously designed comparison "
        "observation closing below that average."
    )
    success = (
        "In each blind, predeclared matched comparison trial, success occurs when "
        "the 10-session close-to-close return of the observation whose close_vs_sma_20 "
        "is at least zero exceeds the 10-session return of the matched observation "
        "whose close_vs_sma_20 is below zero. The tentative hypothesis passes only "
        "if at least 12 of the first 20 locked matched trials succeed; matching rules, "
        "observation eligibility, and non-overlap must be frozen before outcomes are exposed."
    )
    return ProspectiveValidationProtocol(
        protocol_id="AMD-H001-FUTURE-SAME-SUBJECT-PBV-V1-20260912",
        hypothesis_id="AMD-H001",
        source_subject_id="equity:AMD",
        route="FUTURE_SAME_SUBJECT",
        frozen_hypothesis_statement=statement,
        frozen_success_definition=success,
        minimum_required_trials=20,
        collection_start_utc="2026-09-12T00:00:00Z",
        last_historical_exposure_utc="2026-09-11T23:59:59Z",
        authoritative_daily_close_series=(
            "Use Nasdaq Official Closing Price. SMA20_t uses the observation and "
            "immediately preceding 19 Nasdaq sessions."
        ),
        exchange_session_calendar="Official XNAS session calendar.",
        corporate_action_adjustment_policy="Use exact mandatory share multipliers.",
        missing_or_corrected_data_policy=(
            "Terminal records finalize on the fifth Nasdaq session after the terminal session."
        ),
        candidate_condition="close_vs_sma_20 is greater than or equal to zero.",
        comparison_condition="close_vs_sma_20 is less than zero.",
        matching_rule=(
            "Use the chronological anchor and examine the next nine Nasdaq sessions "
            "for the first eligible opposite condition."
        ),
        observation_eligibility="Require the current and previous 19 official closes.",
        outcome_horizon_sessions=10,
        non_overlap_scope="BETWEEN_TRIALS_ONLY",
        tie_handling="Exact equality is a failed trial.",
        trial_ordering_rule="The first 20 locked pairs in chronological lock order.",
        outcome_embargo_rule=(
            "No validation outcome may be decrypted, queried, displayed, exported, "
            "or used until all 20 trials are evaluable."
        ),
        outcome_evaluable_rule=(
            "The terminal session is the tenth subsequent Nasdaq session after t; "
            "finalize at 09:00 America/New_York on the fifth XNAS session after u."
        ),
    )


def _weekdays(start: date, count: int) -> list[date]:
    result = []
    current = start
    while len(result) < count:
        if current.weekday() < 5:
            result.append(current)
        current += timedelta(days=1)
    return result


def _condition(index: int, label: str) -> PublicConditionObservation:
    return PublicConditionObservation(
        session_index=index,
        session_date=f"2026-10-{(index % 28) + 1:02d}",
        eligible=True,
        condition=label,
        input_freeze_utc="2026-10-30T13:00:00+00:00",
        observation_commitment=f"commit-{index}-{label}",
    )


def test_compiler_only_represents_frozen_mechanics():
    plan = compile_execution_plan(_protocol())
    assert plan.sma_window_sessions == 20
    assert plan.match_search_sessions == 9
    assert plan.outcome_horizon_sessions == 10
    assert plan.terminal_finalization_lag_sessions == 5
    assert plan.collective_embargo is True


def test_custodian_emits_only_condition_labels_and_no_raw_prices(tmp_path):
    protocol = _protocol()
    dates = _weekdays(date(2026, 8, 17), 30)
    sessions = []
    for index, session_date in enumerate(dates):
        close = "100" if index < 20 else ("110" if index == 20 else "90")
        sessions.append(
            AuthoritativeSession(
                session_index=index,
                session_date=session_date.isoformat(),
                source_subject_id="equity:AMD",
                source_identity="NASDAQ_NOCP",
                nocp=close,
                mandatory_share_multiplier="1",
            )
        )
    conditions = build_public_condition_feed(
        protocol=protocol,
        sessions=sessions,
        as_of_utc="2026-10-15T20:00:00Z",
    )
    assert conditions
    assert all(item.condition in {"CANDIDATE", "COMPARISON"} for item in conditions)
    output = tmp_path / "public.json"
    save_public_condition_feed(
        output,
        protocol=protocol,
        as_of_utc="2026-10-15T20:00:00Z",
        conditions=conditions,
    )
    text = output.read_text()
    assert '"contains_raw_prices": false' in text
    assert '"contains_outcomes": false' in text
    assert '"nocp"' not in text
    assert '"return"' not in text
    assert load_public_condition_feed(output, protocol=protocol) == conditions


def test_serial_matching_uses_first_opposite_and_closes_gate_through_terminal():
    protocol = _protocol()
    conditions = (
        _condition(20, "CANDIDATE"),
        _condition(21, "CANDIDATE"),
        _condition(22, "COMPARISON"),
        _condition(23, "CANDIDATE"),
        _condition(31, "COMPARISON"),
        _condition(33, "COMPARISON"),
        _condition(34, "CANDIDATE"),
    )
    pairs = derive_pairs(protocol=protocol, conditions=conditions)
    assert len(pairs) == 2
    assert (pairs[0].candidate.session_index, pairs[0].comparison.session_index) == (20, 22)
    # First gate is closed through session 32; session 33 is therefore the next anchor.
    assert (pairs[1].candidate.session_index, pairs[1].comparison.session_index) == (34, 33)


def test_runtime_locks_trial_without_exposing_outcome(tmp_path):
    protocol = _protocol()
    hypothesis = PredictiveHypothesisRecord(
        hypothesis_id=protocol.hypothesis_id,
        statement=protocol.frozen_hypothesis_statement,
        success_definition=protocol.frozen_success_definition,
        minimum_required_trials=20,
    )
    package = ResearchPackage(
        rp_id="RP-AMD-005",
        subject_id="equity:AMD",
        campaign_id="amd-test",
        originating_question="Validate AMD-H001 prospectively.",
        originating_rationale="Frozen future-same-subject validation.",
        predictive_hypotheses=(hypothesis,),
    )
    rp_store = JsonResearchPackageStore(tmp_path / "rps")
    rp_store.create(package)
    state_path = tmp_path / "validation.json"
    validation_store = JsonProspectiveValidationStore(state_path)
    validation_store.save(protocol=protocol, frontier=ProspectiveValidationFrontier.arm(protocol))

    conditions = (_condition(20, "CANDIDATE"), _condition(22, "COMPARISON"))
    result = advance_matching_runtime(
        protocol_store=validation_store,
        research_package_store=rp_store,
        rp_id="RP-AMD-005",
        conditions=conditions,
    )
    assert result.newly_locked_trials == ("AMD-H001-T01",)
    assert result.next_trial_id == "AMD-H001-T02"
    stored_protocol, frontier = validation_store.load()
    assert stored_protocol.fingerprint == protocol.fingerprint
    assert len(frontier.trials) == 1
    assert frontier.trials[0].success is None
    assert frontier.trials[0].outcome_result_id is None
    stored_package = rp_store.load("RP-AMD-005")
    assert stored_package is not None
    stored_h = stored_package.predictive_hypotheses[0]
    assert len(stored_h.trials) == 1
    assert stored_h.success_count == 0
    assert stored_h.failure_count == 0
    assert stored_h.success_rate is None

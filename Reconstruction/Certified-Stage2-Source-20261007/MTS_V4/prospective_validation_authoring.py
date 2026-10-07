from __future__ import annotations

import json
from typing import Mapping

from .prospective_validation import (
    ProspectiveValidationError,
    ProspectiveValidationProtocol,
)
from .research_package import PredictiveHypothesisRecord
from .sol_batch_provider import SolBatchResearchDirector


def decode_prospective_validation_protocol(
    text: str,
    *,
    hypothesis: PredictiveHypothesisRecord,
    source_subject_id: str,
    last_historical_exposure_utc: str,
) -> ProspectiveValidationProtocol:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ProspectiveValidationError(f"invalid prospective protocol JSON: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise ProspectiveValidationError("prospective protocol response must be an object")
    document = dict(raw)
    document["last_historical_exposure_utc"] = last_historical_exposure_utc
    protocol = ProspectiveValidationProtocol(**document)
    if protocol.source_subject_id != source_subject_id:
        raise ProspectiveValidationError("protocol source_subject_id changed")
    protocol.validate_against_hypothesis(hypothesis)
    return protocol


def author_prospective_validation_protocol(
    *,
    rd: SolBatchResearchDirector,
    hypothesis: PredictiveHypothesisRecord,
    source_subject_id: str,
    validation_source_selection: Mapping[str, object],
    last_historical_exposure_utc: str,
) -> ProspectiveValidationProtocol:
    """Ask Sol to author the scientific prospective-validation mechanics.

    Deterministic code supplies the frozen hypothesis, the already accepted
    FUTURE_SAME_SUBJECT route, and the objective exposure cutoff. Sol owns the
    scientific protocol choices. The returned representation is then frozen and
    mechanically executable.
    """

    if validation_source_selection.get("hypothesis_id") != hypothesis.hypothesis_id:
        raise ProspectiveValidationError("validation source selection hypothesis_id mismatch")
    if validation_source_selection.get("route") != "FUTURE_SAME_SUBJECT":
        raise ProspectiveValidationError(
            "prospective protocol authoring requires FUTURE_SAME_SUBJECT selection"
        )

    system = (
        "You are the MTS v4 AI Research Director and scientific reasoning authority. "
        "Author the complete prospective blind-validation protocol for the already-frozen hypothesis and the already-accepted FUTURE_SAME_SUBJECT route. "
        "Do not revise the hypothesis, success definition, minimum trial count, or source subject. "
        "You own the scientific choices for authoritative close series, session calendar, corporate-action handling, missing/corrected-data handling, candidate/comparison representation, matching, eligibility, outcome horizon representation, non-overlap scope, tie handling, trial ordering, and outcome embargo/evaluability. "
        "The protocol must be fully specified before future validation outcomes are exposed. "
        "The collection start must be strictly after the supplied last historical exposure timestamp. "
        "Return exactly one JSON object and no prose."
    )
    user = {
        "operation": "AUTHOR_PROSPECTIVE_VALIDATION_PROTOCOL",
        "source_subject_id": source_subject_id,
        "last_historical_exposure_utc": last_historical_exposure_utc,
        "validation_source_selection": dict(validation_source_selection),
        "frozen_hypothesis": {
            "hypothesis_id": hypothesis.hypothesis_id,
            "statement": hypothesis.statement,
            "success_definition": hypothesis.success_definition,
            "minimum_required_trials": hypothesis.minimum_required_trials,
            "existing_trials": len(hypothesis.trials),
            "status": hypothesis.status,
        },
        "required_schema": {
            "protocol_id": "stable unique protocol identifier",
            "hypothesis_id": hypothesis.hypothesis_id,
            "source_subject_id": source_subject_id,
            "route": "FUTURE_SAME_SUBJECT",
            "frozen_hypothesis_statement": hypothesis.statement,
            "frozen_success_definition": hypothesis.success_definition,
            "minimum_required_trials": hypothesis.minimum_required_trials,
            "collection_start_utc": "ISO-8601 timestamp strictly after last_historical_exposure_utc",
            "authoritative_daily_close_series": "exact scientific data-series definition",
            "exchange_session_calendar": "exact authoritative session calendar",
            "corporate_action_adjustment_policy": "predeclared handling rule",
            "missing_or_corrected_data_policy": "predeclared handling rule",
            "candidate_condition": "mechanically implementable candidate condition consistent with frozen hypothesis",
            "comparison_condition": "mechanically implementable comparison condition consistent with frozen hypothesis",
            "matching_rule": "complete contemporaneous matching rule, frozen before outcome access",
            "observation_eligibility": "complete prospective observation eligibility rule",
            "outcome_horizon_sessions": "positive integer consistent with frozen success definition",
            "non_overlap_scope": "BETWEEN_TRIALS_ONLY or ALL_OBSERVATIONS",
            "tie_handling": "complete tie rule",
            "trial_ordering_rule": "rule that determines exactly the first minimum_required_trials trials without outcome access",
            "outcome_embargo_rule": "rule preventing access to terminal outcomes before lock/evaluability",
            "outcome_evaluable_rule": "exact rule for when each matched trial becomes evaluable",
            "authored_by": "AI_RESEARCH_DIRECTOR",
        },
    }
    content = rd._chat_completion(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, sort_keys=True, separators=(",", ":"))},
        ]
    )
    return decode_prospective_validation_protocol(
        content,
        hypothesis=hypothesis,
        source_subject_id=source_subject_id,
        last_historical_exposure_utc=last_historical_exposure_utc,
    )

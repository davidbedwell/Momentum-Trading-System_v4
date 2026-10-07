from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from typing import Mapping, Sequence

from .research_package import PredictiveHypothesisRecord
from .sol_batch_provider import SolBatchResearchDirector


class ValidationSourceSelectionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ValidationSourceSelection:
    hypothesis_id: str
    route: str
    rationale: str
    external_subject_criteria: str | None = None
    proposed_external_subject_id: str | None = None
    additional_information_required: tuple[str, ...] = ()

    def to_dict(self) -> Mapping[str, object]:
        return asdict(self)


def _nonblank(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationSourceSelectionError(f"{field} must be a nonblank string")
    return value.strip()


def decode_validation_source_selection(
    text: str,
    *,
    expected_hypothesis_id: str,
) -> ValidationSourceSelection:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValidationSourceSelectionError(f"invalid validation-source JSON: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise ValidationSourceSelectionError("validation-source response must be an object")

    hypothesis_id = _nonblank(raw.get("hypothesis_id"), "hypothesis_id")
    if hypothesis_id != expected_hypothesis_id:
        raise ValidationSourceSelectionError(
            f"hypothesis_id changed: expected {expected_hypothesis_id}, received {hypothesis_id}"
        )
    route = _nonblank(raw.get("route"), "route")
    if route not in {"FUTURE_SAME_SUBJECT", "EXTERNAL_UNSEEN_SUBJECT"}:
        raise ValidationSourceSelectionError(
            "route must be FUTURE_SAME_SUBJECT or EXTERNAL_UNSEEN_SUBJECT"
        )
    rationale = _nonblank(raw.get("rationale"), "rationale")

    criteria = raw.get("external_subject_criteria")
    if criteria is not None:
        criteria = _nonblank(criteria, "external_subject_criteria")
    proposed = raw.get("proposed_external_subject_id")
    if proposed is not None:
        proposed = _nonblank(proposed, "proposed_external_subject_id")
    required = raw.get("additional_information_required", [])
    if not isinstance(required, list) or not all(
        isinstance(item, str) and item.strip() for item in required
    ):
        raise ValidationSourceSelectionError(
            "additional_information_required must be a list of nonblank strings"
        )

    if route == "EXTERNAL_UNSEEN_SUBJECT" and criteria is None:
        raise ValidationSourceSelectionError(
            "EXTERNAL_UNSEEN_SUBJECT requires external_subject_criteria"
        )
    if route == "FUTURE_SAME_SUBJECT" and proposed is not None:
        raise ValidationSourceSelectionError(
            "FUTURE_SAME_SUBJECT cannot propose an external subject"
        )

    return ValidationSourceSelection(
        hypothesis_id=hypothesis_id,
        route=route,
        rationale=rationale,
        external_subject_criteria=criteria,
        proposed_external_subject_id=proposed,
        additional_information_required=tuple(item.strip() for item in required),
    )


def select_validation_source(
    *,
    rd: SolBatchResearchDirector,
    hypothesis: PredictiveHypothesisRecord,
    source_subject_id: str,
    historically_exposed_subject_ids: Sequence[str],
) -> ValidationSourceSelection:
    """Ask Sol to choose the scientific validation route for one frozen hypothesis.

    Deterministic code supplies objective exposure constraints and validates the
    representation only. It does not define "AMD-like", select an external
    comparison subject, or decide whether waiting for future same-subject data is
    scientifically preferable.
    """

    system = (
        "You are the MTS v4 AI Research Director and scientific reasoning authority. "
        "Choose the scientifically defensible blind-validation source for the already-frozen predictive hypothesis. "
        "Do not revise, broaden, narrow, or replace the hypothesis. Historical observations already exposed during "
        "discovery are not blind and cannot be reused as blind validation. You may choose either genuinely future "
        "observations on the same subject or a genuinely unseen external subject. If you choose an external subject, "
        "you own the scientific definition of what makes it appropriate for this hypothesis; deterministic code must "
        "not invent a similarity rule. Do not name a specific external subject unless the supplied context is enough to "
        "justify it. Return exactly one JSON object and no prose."
    )
    user = {
        "operation": "SELECT_PREDICTIVE_VALIDATION_SOURCE",
        "frozen_hypothesis": {
            "hypothesis_id": hypothesis.hypothesis_id,
            "statement": hypothesis.statement,
            "success_definition": hypothesis.success_definition,
            "minimum_required_trials": hypothesis.minimum_required_trials,
            "source_result_ids": list(hypothesis.source_result_ids),
            "status": hypothesis.status,
            "existing_trials": len(hypothesis.trials),
        },
        "source_subject_id": source_subject_id,
        "objective_exposure_constraints": {
            "source_subject_historical_discovery_data_exposed": True,
            "historically_exposed_subject_ids": sorted(set(historically_exposed_subject_ids)),
            "historical_exposed_data_may_not_be_relabelled_blind": True,
        },
        "required_schema": {
            "hypothesis_id": "exact unchanged frozen hypothesis_id",
            "route": "FUTURE_SAME_SUBJECT or EXTERNAL_UNSEEN_SUBJECT",
            "rationale": "scientific rationale",
            "external_subject_criteria": "scientific eligibility/similarity criteria when external route is chosen, otherwise null",
            "proposed_external_subject_id": "specific unseen subject only if justified by supplied context, otherwise null",
            "additional_information_required": ["information needed before a specific external subject can be selected or trial mechanics finalized"],
        },
    }
    content = rd._chat_completion(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, sort_keys=True, separators=(",", ":"))},
        ]
    )
    return decode_validation_source_selection(
        content,
        expected_hypothesis_id=hypothesis.hypothesis_id,
    )

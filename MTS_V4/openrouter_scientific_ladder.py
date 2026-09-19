from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping


EXPECTED_CONTROLS = frozenset(
    {
        "cross_sectional_medium_term_momentum",
        "deterministic_negative_control",
        "medium_term_trend_persistence",
        "post_earnings_behavior",
        "short_horizon_reversal",
    }
)
ALLOWED_GRADES = frozenset({"PASS", "PARTIAL", "FAIL"})


@dataclass(frozen=True)
class OpenRouterCandidate:
    model: str
    label: str
    maximum_prompt_usd_per_token: float
    maximum_completion_usd_per_token: float
    reasoning_effort: str = "high"


# Ordered by the maximum published prompt/completion price at implementation time.
# Runtime preflight records the live OpenRouter catalog entry and refuses a price
# above these ceilings unless the human explicitly updates the governed policy.
MODEL_LADDER = (
    OpenRouterCandidate(
        model="deepseek/deepseek-v4.1-flash",
        label="DeepSeek V4.1 Flash",
        maximum_prompt_usd_per_token=0.00000030,
        maximum_completion_usd_per_token=0.00000120,
    ),
    OpenRouterCandidate(
        model="google/gemini-3.7-flash",
        label="Gemini 3.7 Flash",
        maximum_prompt_usd_per_token=0.00000075,
        maximum_completion_usd_per_token=0.00000375,
    ),
    OpenRouterCandidate(
        model="openai/gpt-5.6-terra",
        label="GPT-5.6 Terra",
        maximum_prompt_usd_per_token=0.00000200,
        maximum_completion_usd_per_token=0.00000900,
    ),
    OpenRouterCandidate(
        model="anthropic/claude-sonnet-5",
        label="Claude Sonnet 5",
        maximum_prompt_usd_per_token=0.00000200,
        maximum_completion_usd_per_token=0.00001000,
    ),
)

INDEPENDENT_JUDGE = OpenRouterCandidate(
    model="openai/gpt-5.6-sol",
    label="GPT-5.6 Sol independent adjudicator",
    maximum_prompt_usd_per_token=0.00000400,
    maximum_completion_usd_per_token=0.00001500,
    reasoning_effort="high",
)


class LadderPolicyError(RuntimeError):
    pass


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_by_model(model: str) -> OpenRouterCandidate:
    for candidate in MODEL_LADDER:
        if candidate.model == model:
            return candidate
    raise LadderPolicyError(f"model is not in the governed ladder: {model}")


def ladder_policy_document() -> dict[str, object]:
    return {
        "format": "MTS_V4_OPENROUTER_SCIENTIFIC_LADDER_POLICY_V1",
        "success_rule": "PASS_ON_ALL_FIVE_CONTROLS",
        "candidate_self_grading_allowed": False,
        "deterministic_semantic_grading_allowed": False,
        "sol_fallback_allowed": False,
        "automated_independent_adjudication": {
            "allowed": True,
            "model": INDEPENDENT_JUDGE.model,
            "candidate_outputs_are_untrusted_evidence": True,
            "hidden_benchmark_exposed_to_candidates": False,
            "manual_final_review_required_before_production_authorization": True,
        },
        "models": [asdict(candidate) for candidate in MODEL_LADDER],
        "controls": sorted(EXPECTED_CONTROLS),
    }


def validate_live_catalog_entry(
    candidate: OpenRouterCandidate, entry: Mapping[str, object]
) -> dict[str, object]:
    if entry.get("id") != candidate.model:
        raise LadderPolicyError(f"catalog identity mismatch for {candidate.model}")
    pricing = entry.get("pricing")
    if not isinstance(pricing, Mapping):
        raise LadderPolicyError(f"catalog pricing missing for {candidate.model}")
    try:
        prompt = float(pricing["prompt"])
        completion = float(pricing["completion"])
    except (KeyError, TypeError, ValueError) as exc:
        raise LadderPolicyError(f"invalid catalog pricing for {candidate.model}") from exc
    if prompt < 0 or completion < 0:
        raise LadderPolicyError(f"negative catalog pricing for {candidate.model}")
    if prompt > candidate.maximum_prompt_usd_per_token:
        raise LadderPolicyError(
            f"live prompt price exceeds governed ceiling for {candidate.model}: "
            f"{prompt} > {candidate.maximum_prompt_usd_per_token}"
        )
    if completion > candidate.maximum_completion_usd_per_token:
        raise LadderPolicyError(
            f"live completion price exceeds governed ceiling for {candidate.model}: "
            f"{completion} > {candidate.maximum_completion_usd_per_token}"
        )
    supported = entry.get("supported_parameters")
    supported_set = set(supported) if isinstance(supported, list) else set()
    required = {"response_format", "structured_outputs"}
    if not required.issubset(supported_set):
        raise LadderPolicyError(
            f"model lacks governed structured-output support: {candidate.model}"
        )
    context_length = entry.get("context_length")
    if not isinstance(context_length, int) or context_length < 100_000:
        raise LadderPolicyError(f"model context is inadequate: {candidate.model}")
    return {
        "id": candidate.model,
        "canonical_slug": entry.get("canonical_slug"),
        "context_length": context_length,
        "pricing": {"prompt": prompt, "completion": completion},
        "supported_parameters": sorted(supported_set),
    }


def usage_cost_usd(
    usage: Mapping[str, object] | None, candidate: OpenRouterCandidate
) -> float:
    if not usage:
        raise LadderPolicyError("provider response omitted token usage")
    direct = usage.get("cost")
    if isinstance(direct, (int, float)) and float(direct) >= 0:
        return float(direct)
    try:
        prompt_tokens = int(usage["prompt_tokens"])
        completion_tokens = int(usage["completion_tokens"])
    except (KeyError, TypeError, ValueError) as exc:
        raise LadderPolicyError("provider usage lacks token counts") from exc
    if prompt_tokens < 0 or completion_tokens < 0:
        raise LadderPolicyError("provider returned negative token usage")
    return (
        prompt_tokens * candidate.maximum_prompt_usd_per_token
        + completion_tokens * candidate.maximum_completion_usd_per_token
    )


def validate_independent_assessment(
    document: Mapping[str, object],
    *,
    expected_model: str,
    expected_review_sha256: str,
) -> dict[str, object]:
    if document.get("format") != "MTS_V4_INDEPENDENT_FIVE_CONTROL_ASSESSMENT_V1":
        raise LadderPolicyError("unsupported independent assessment format")
    if document.get("model") != expected_model:
        raise LadderPolicyError("assessment model does not match candidate")
    if document.get("review_artifact_sha256") != expected_review_sha256:
        raise LadderPolicyError("assessment is not bound to the exact review artifact")
    if document.get("candidate_self_assessment") is not False:
        raise LadderPolicyError("candidate self-assessment is prohibited")
    if document.get("independent_assessor") in (None, "", expected_model):
        raise LadderPolicyError("an independent assessor identity is required")
    grades = document.get("grades")
    if not isinstance(grades, list) or len(grades) != len(EXPECTED_CONTROLS):
        raise LadderPolicyError("assessment requires exactly five grades")
    normalized: dict[str, str] = {}
    for item in grades:
        if not isinstance(item, Mapping):
            raise LadderPolicyError("assessment grade entry must be an object")
        control = item.get("control_id")
        grade = str(item.get("grade", "")).upper()
        if control not in EXPECTED_CONTROLS or grade not in ALLOWED_GRADES:
            raise LadderPolicyError("assessment contains an invalid control or grade")
        if control in normalized:
            raise LadderPolicyError(f"duplicate assessment grade: {control}")
        normalized[str(control)] = grade
    if set(normalized) != EXPECTED_CONTROLS:
        raise LadderPolicyError("assessment does not cover the exact five controls")
    passed = all(grade == "PASS" for grade in normalized.values())
    return {
        "model": expected_model,
        "grades": [
            {"control_id": control, "grade": normalized[control]}
            for control in sorted(normalized)
        ],
        "all_five_pass": passed,
        "review_artifact_sha256": expected_review_sha256,
        "independent_assessor": document["independent_assessor"],
    }


def next_model(completed_assessments: Iterable[Mapping[str, object]]) -> str | None:
    completed = list(completed_assessments)
    for index, assessment in enumerate(completed):
        if index >= len(MODEL_LADDER):
            raise LadderPolicyError("more assessments than governed candidates")
        if assessment.get("model") != MODEL_LADDER[index].model:
            raise LadderPolicyError("assessment order does not match governed ladder")
        if assessment.get("all_five_pass") is True:
            return None
    if len(completed) == len(MODEL_LADDER):
        return None
    return MODEL_LADDER[len(completed)].model

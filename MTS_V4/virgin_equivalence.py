from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


class EquivalenceProtocolError(RuntimeError):
    """Fail-closed violation of the frozen virgin-equivalence protocol."""


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class VirginCandidate:
    subject_id: str
    partition: str
    prior_sol_exposure: bool
    prior_gemini_exposure: bool
    prior_campaign_exposure: bool
    starting_data_available: bool

    @property
    def eligible(self) -> bool:
        return (
            self.partition == "DISCOVERY"
            and not self.prior_sol_exposure
            and not self.prior_gemini_exposure
            and not self.prior_campaign_exposure
            and self.starting_data_available
        )


def deterministic_select_virgins(
    candidates: Iterable[VirginCandidate], *, count: int = 3, protocol_seed: str
) -> dict[str, object]:
    if count != 3:
        raise EquivalenceProtocolError("frozen protocol requires exactly three tickers")
    eligible = sorted((c for c in candidates if c.eligible), key=lambda c: c.subject_id)
    if len(eligible) < count:
        raise EquivalenceProtocolError("fewer than three machine-proven virgin DISCOVERY tickers")
    eligible_ids = [c.subject_id for c in eligible]
    eligible_hash = canonical_sha256(eligible_ids)
    ranked = sorted(
        eligible_ids,
        key=lambda subject_id: hashlib.sha256(
            f"{protocol_seed}:{eligible_hash}:{subject_id}".encode("utf-8")
        ).hexdigest(),
    )
    selected = ranked[:count]
    manifest = {
        "format": "MTS_V4_VIRGIN_SELECTION_V1",
        "selection_rule": "sha256(protocol_seed:eligible_set_sha256:subject_id)",
        "protocol_seed": protocol_seed,
        "eligible_set_sha256": eligible_hash,
        "eligible_count": len(eligible_ids),
        "selected_subject_ids": selected,
        "eligibility": {
            c.subject_id: {
                "partition": c.partition,
                "prior_sol_exposure": c.prior_sol_exposure,
                "prior_gemini_exposure": c.prior_gemini_exposure,
                "prior_campaign_exposure": c.prior_campaign_exposure,
                "starting_data_available": c.starting_data_available,
            }
            for c in eligible
        },
    }
    manifest["freeze_sha256"] = canonical_sha256(manifest)
    return manifest


def freeze_starting_package(subject_id: str, package: Mapping[str, object]) -> dict[str, object]:
    required = {"mission", "subject", "evidence", "available_analysis_methods", "starting_state"}
    missing = required - set(package)
    if missing:
        raise EquivalenceProtocolError(f"starting package missing fields: {sorted(missing)}")
    frozen = {
        "format": "MTS_V4_EQUIVALENCE_STARTING_PACKAGE_V1",
        "subject_id": subject_id,
        "package": dict(package),
    }
    frozen["sha256"] = canonical_sha256(frozen)
    return frozen


def verify_identical_start(start_a: Mapping[str, object], start_b: Mapping[str, object]) -> str:
    if start_a.get("sha256") != start_b.get("sha256"):
        raise EquivalenceProtocolError("arm starting-package hash mismatch")
    if canonical_sha256({k: v for k, v in start_a.items() if k != "sha256"}) != start_a.get("sha256"):
        raise EquivalenceProtocolError("Arm A starting package failed integrity check")
    if canonical_sha256({k: v for k, v in start_b.items() if k != "sha256"}) != start_b.get("sha256"):
        raise EquivalenceProtocolError("Arm B starting package failed integrity check")
    return str(start_a["sha256"])


def freeze_arm_manifest(
    *, subject_id: str, arm: str, starting_sha256: str, artifacts: Sequence[Mapping[str, object]],
    usage: Sequence[Mapping[str, object]], complete: bool,
    terminal_state: str = "CLOSED",
    scientific_record: Mapping[str, object] | None = None,
) -> dict[str, object]:
    if arm not in {"DIRECT_SOL", "GEMINI_SOL_HYBRID"}:
        raise EquivalenceProtocolError("invalid experiment arm")
    if not complete:
        raise EquivalenceProtocolError("cannot freeze incomplete arm")
    if not artifacts:
        raise EquivalenceProtocolError("complete arm must contain scientific artifacts")
    if not usage:
        raise EquivalenceProtocolError("complete arm must contain usage telemetry")
    if terminal_state not in {"CLOSED", "WAITING_FOR_FUTURE_COHORTS"}:
        raise EquivalenceProtocolError(f"invalid complete-arm terminal state: {terminal_state}")
    manifest = {
        "format": "MTS_V4_EQUIVALENCE_ARM_MANIFEST_V2",
        "subject_id": subject_id,
        "arm": arm,
        "starting_package_sha256": starting_sha256,
        "artifacts": list(artifacts),
        "usage": list(usage),
        "complete": True,
        "terminal_state": terminal_state,
        "scientific_record": dict(scientific_record or {}),
    }
    manifest["freeze_sha256"] = canonical_sha256(manifest)
    return manifest


def build_hybrid_appeal_context(
    *, starting_package: Mapping[str, object], gemini_work: Sequence[Mapping[str, object]],
    analysis_results: Sequence[Mapping[str, object]], max_sol_calls: int, max_sol_spend_usd: float
) -> dict[str, object]:
    if max_sol_calls < 1 or max_sol_spend_usd <= 0:
        raise EquivalenceProtocolError("Sol appeal must have positive explicit bounds")
    if not gemini_work:
        raise EquivalenceProtocolError("Sol appeal requires Gemini's complete work product")
    return {
        "format": "MTS_V4_GEMINI_SOL_BOUNDED_APPEAL_V1",
        "starting_package": dict(starting_package),
        "gemini_complete_work_product": list(gemini_work),
        "all_hybrid_analysis_results": list(analysis_results),
        "authority": {
            "may_challenge_reasoning": True,
            "may_identify_omissions": True,
            "may_reject_promotions": True,
            "may_reinterpret_results": True,
            "may_request_bounded_corrective_analysis": True,
            "may_restart_unrestricted_direct_sol_workflow": False,
        },
        "bounds": {"max_sol_calls": max_sol_calls, "max_sol_spend_usd": max_sol_spend_usd},
    }


def blinded_pair(arm_a: Mapping[str, object], arm_b: Mapping[str, object], *, salt: str) -> dict[str, object]:
    for arm in (arm_a, arm_b):
        if not arm.get("complete") or not arm.get("freeze_sha256"):
            raise EquivalenceProtocolError("comparison requires two frozen complete arms")
    if arm_a.get("subject_id") != arm_b.get("subject_id"):
        raise EquivalenceProtocolError("comparison arms are from different subjects")
    if arm_a.get("starting_package_sha256") != arm_b.get("starting_package_sha256"):
        raise EquivalenceProtocolError("comparison arms did not share identical starting state")
    ordered = sorted(
        (arm_a, arm_b),
        key=lambda arm: hashlib.sha256(f"{salt}:{arm['freeze_sha256']}".encode()).hexdigest(),
    )
    def strip_identity(arm: Mapping[str, object]) -> dict[str, object]:
        # The comparator receives scientific content and terminal semantics, but
        # never provider identity, usage/cost, filesystem paths, or artifact names
        # that can reveal which arm produced the record.
        return {
            "format": arm.get("format"),
            "subject_id": arm.get("subject_id"),
            "starting_package_sha256": arm.get("starting_package_sha256"),
            "complete": arm.get("complete"),
            "terminal_state": arm.get("terminal_state"),
            "scientific_record": arm.get("scientific_record", {}),
            "freeze_sha256": arm.get("freeze_sha256"),
        }
    return {
        "format": "MTS_V4_BLINDED_EQUIVALENCE_PAIR_V1",
        "subject_id": arm_a["subject_id"],
        "ARM_X": strip_identity(ordered[0]),
        "ARM_Y": strip_identity(ordered[1]),
        "identity_commitment_sha256": canonical_sha256(
            {"salt": salt, "X": ordered[0]["arm"], "Y": ordered[1]["arm"]}
        ),
    }


def qualify_experiment(
    comparisons: Sequence[Mapping[str, object]], *, direct_cost_usd: float, hybrid_cost_usd: float
) -> dict[str, object]:
    if len(comparisons) != 3:
        raise EquivalenceProtocolError("qualification requires exactly three ticker comparisons")
    if direct_cost_usd <= 0 or hybrid_cost_usd < 0:
        raise EquivalenceProtocolError("invalid experiment costs")
    missed = any(bool(c.get("material_direct_sol_finding_missed")) for c in comparisons)
    equivalent = all(bool(c.get("materially_equivalent")) for c in comparisons)
    false_promotion = any(bool(c.get("disqualifying_false_hybrid_promotion")) for c in comparisons)
    saving = (direct_cost_usd - hybrid_cost_usd) / direct_cost_usd
    qualified = equivalent and not missed and not false_promotion and saving >= 0.35
    return {
        "format": "MTS_V4_GEMINI_SOL_EQUIVALENCE_QUALIFICATION_V1",
        "ticker_count": 3,
        "material_direct_sol_finding_missed": missed,
        "all_tickers_materially_equivalent": equivalent,
        "disqualifying_false_hybrid_promotion": false_promotion,
        "direct_cost_usd": direct_cost_usd,
        "hybrid_cost_usd": hybrid_cost_usd,
        "cost_saving_fraction": saving,
        "minimum_cost_saving_fraction": 0.35,
        "qualified": qualified,
    }


def write_frozen_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise EquivalenceProtocolError(f"refusing to overwrite frozen artifact: {path}")
    payload = canonical_json(value) + "\n"
    path.write_text(payload, encoding="utf-8")

from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Mapping, Sequence

from .contracts import EvidenceDescriptor, SubjectMetadata
from .sol_batch_provider import SolBatchResearchDirector


RETROSPECTIVE_RECOVERY_POLICY = {
    "historical_exposure_status": "EXPOSED",
    "research_phase": "EXPLORATION",
    "blind_validation_claim_allowed": False,
    "historical_results_may_support_discovery": True,
    "historical_results_may_not_count_as_blind_validation": True,
    "scientific_authority": (
        "AI Research Director retains authority to continue exploration, open or close Research Packages, "
        "author as many presently justified Analysis Specifications as warranted, freeze a tentative predictive "
        "hypothesis when evidence is sufficient, or conclude that further work is not scientifically useful."
    ),
    "batch_execution_rule": (
        "At each decision point, send every analysis whose scientific justification is already available as one "
        "batch. Receive and interpret the consolidated batch report before authoring work that genuinely depends "
        "on unknown results from that batch."
    ),
}


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[object]:
    rows: list[object] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_retrospective_subject_context(subject_dir: str | Path) -> dict[str, object]:
    """Load preserved prior subject state as exposed scientific context only.

    Historical RP identifiers and result records are not imported into the new active
    campaign package store. They remain provenance/context so the recovery campaign
    cannot accidentally treat old execution objects as fresh active lineage.
    """

    root = Path(subject_dir)
    if not root.is_dir():
        raise RuntimeError(f"retrospective subject directory does not exist: {root}")

    context: dict[str, object] = {
        "source_directory": str(root),
        "policy": dict(RETROSPECTIVE_RECOVERY_POLICY),
        "preserved_state": {},
    }
    state = context["preserved_state"]
    assert isinstance(state, dict)

    decisions = root / "rd_decisions.jsonl"
    if decisions.is_file():
        state["rd_decisions"] = _load_jsonl(decisions)

    nexus = root / "research_nexus.json"
    if nexus.is_file():
        state["research_nexus"] = _load_json(nexus)

    ledger = root / "subject_ledger.json"
    if ledger.is_file():
        state["subject_ledger"] = _load_json(ledger)

    checkpoint = root / "checkpoint.json"
    if checkpoint.is_file():
        state["checkpoint"] = _load_json(checkpoint)

    rp_dir = root / "research_packages"
    if rp_dir.is_dir():
        state["research_packages"] = {
            path.name: _load_json(path)
            for path in sorted(rp_dir.glob("*.json"))
        }

    if not state:
        raise RuntimeError(f"no preserved retrospective subject state found in: {root}")
    return context


class SolRetrospectiveRecoveryResearchDirector(SolBatchResearchDirector):
    """Batched Sol RD that can continue exploration from exposed legacy subject work.

    The prior record is injected as scientific context at every decision boundary.
    New work still uses the ordinary batched Analysis compiler/executor and a fresh
    active Research Package store. This preserves the corrected batch authority model
    while preventing old exposed work from being mislabeled as blind validation.
    """

    def __init__(
        self,
        *args,
        retrospective_context: Mapping[str, object],
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._retrospective_context = dict(retrospective_context)

    def _batch_common_payload(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> dict[str, object]:
        payload = super()._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload["retrospective_recovery_context"] = self._retrospective_context
        return payload

    @classmethod
    def _batch_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
        messages = super()._batch_messages(
            operation=operation,
            mission=mission,
            payload=payload,
        )
        system = messages[0]["content"] + (
            " This is a RETROSPECTIVE RECOVERY exploration campaign. The preserved historical subject record in "
            "retrospective_recovery_context was already exposed to prior Research Director logic and therefore may "
            "be used as discovery context but MUST NEVER be described or counted as blind validation. Re-evaluate the "
            "subject under the current corrected scientific-authority model. Do not merely classify the old work. If "
            "additional analysis is scientifically warranted, author all analyses that are justified now in the same "
            "batch, receive the consolidated batch report, and continue iteratively. If preserved evidence is already "
            "sufficient, you may freeze a tentative predictive hypothesis without unnecessary re-analysis. If a hypothesis "
            "is frozen, its later validation must use genuinely unexposed evidence. Historical RP identifiers in the "
            "retrospective context are provenance only; do not use them as active parent_rp_id values unless they also "
            "exist independently in the current active research_packages context."
        )
        return [{"role": "system", "content": system}, *messages[1:]]

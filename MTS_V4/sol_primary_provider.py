from __future__ import annotations

from typing import Mapping

from .contracts import ResearchDecision, ResearchPhase
from .research_package_store import JsonResearchPackageStore
from .sol_provider import SolResearchPackageAwareResearchDirector


class SolPrimaryResearchDirector(SolResearchPackageAwareResearchDirector):
    """Primary Sol RD with cross-subject context and objective closure guardrails."""

    def __init__(
        self,
        *,
        research_package_store: JsonResearchPackageStore,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 180,
        required_subject_id: str | None = None,
        required_research_phase: ResearchPhase | None = None,
    ) -> None:
        super().__init__(
            research_package_store=research_package_store,
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self._required_subject_id = required_subject_id
        self._required_research_phase = required_research_phase

    @classmethod
    def _decision_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ):
        messages = super()._decision_messages(operation=operation, mission=mission, payload=payload)
        system = messages[0]["content"] + (
            " When nexus_context.cross_subject_scientific_memory is present, treat it as compact prior-subject "
            "scientific experience, not as a mandatory agenda. You retain scientific authority to test, challenge, "
            "reformulate, condition, defer, or ignore prior-subject records. Use the Research Frontier when useful "
            "to accumulate knowledge across subjects, but do not assume that a relationship observed on one subject "
            "generalizes. Generalization itself must remain falsifiable. During EXPLORATION, prior records, hypotheses, "
            "and the Research Frontier are scientific context only and must never delimit the discovery space. You retain "
            "authority to choose scientifically justified lookback windows, forward horizons, thresholds, continuous or "
            "normalized representations, outcome definitions, direction/magnitude/timing/path targets, evidence streams, "
            "interactions, regime conditions, and entirely different research propositions. Do not inherit a prior numeric "
            "threshold, lookback, forward horizon, method, or target merely for consistency or comparability. Continue or "
            "replicate a prior formulation only when you judge that choice scientifically useful, and state that scientific "
            "reason in the question/rationale. A negative result for one formulation does not establish that the subject "
            "lacks predictive structure under other scientifically justified formulations, and a positive result does not "
            "make that formulation the default research agenda for later subjects. Historical rp_id values appearing only in "
            "cross-subject scientific memory are provenance references, not active local Research Packages. Set "
            "next_request.parent_rp_id only when that exact parent RP already exists in the active campaign's "
            "research_package_context/package store for the current subject; otherwise parent_rp_id must be null. "
            "Do not copy a historical seed-memory rp_id into parent_rp_id merely to express conceptual continuity. "
            "If the current subject was selected first for blind validation of a prior hypothesis, preserve the "
            "no-look-ahead validation boundary and complete the validation trial before unrestricted exploratory use "
            "of that subject. When subject_phase_contract is present, it is the already-accepted objective phase "
            "contract for this run. Do not switch the subject from EXPLORATION to VALIDATION or from VALIDATION to "
            "EXPLORATION inside an ordinary decision. A new predictive hypothesis may be scientifically authored "
            "during exploration, but its research package must already exist durably before "
            "predictive_hypothesis_updates are emitted. Establish a new RP through an accepted Analysis request "
            "first, then emit the hypothesis update in a later decision."
        )
        return [{"role": "system", "content": system}, messages[1]]

    def _request_decision(
        self,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> ResearchDecision:
        enriched = dict(payload)
        if self._required_research_phase is not None:
            enriched["subject_phase_contract"] = {
                "subject_id": self._required_subject_id,
                "required_research_phase": self._required_research_phase.value,
                "authority": (
                    "Accepted subject-selection/validation-first program state. Deterministic code enforces "
                    "phase ordering only and does not choose scientific questions, hypotheses, methods, or parameters."
                ),
            }
        return super()._request_decision(
            operation=operation,
            mission=mission,
            payload=enriched,
        )

    def _decision_representation_defect(
        self,
        operation: str,
        decision: ResearchDecision,
        payload: Mapping[str, object],
    ) -> str | None:
        defect = super()._decision_representation_defect(operation, decision, payload)
        if defect is not None:
            return defect

        if decision.continue_research and decision.next_request is not None:
            request = decision.next_request
            if (
                self._required_subject_id is not None
                and request.subject_id == self._required_subject_id
                and self._required_research_phase is not None
                and request.research_phase is not self._required_research_phase
            ):
                return (
                    "next_request.research_phase violates the accepted subject phase contract: "
                    f"subject {self._required_subject_id} requires "
                    f"{self._required_research_phase.value}, received {request.research_phase.value}. "
                    "Deterministic code will not change the phase; RD must return a scientifically valid "
                    "decision within the accepted phase."
                )

            if request.parent_rp_id is not None:
                parent = self._research_package_store.load(request.parent_rp_id)
                if parent is None:
                    return (
                        "next_request.parent_rp_id references a Research Package that is not present in the active "
                        f"campaign package store: {request.parent_rp_id}. Historical rp_id values supplied through "
                        "cross-subject scientific memory are provenance/context only and are not local parent objects. "
                        "Return parent_rp_id=null unless the exact parent RP already exists durably in this active "
                        "campaign. Deterministic code will not invent, materialize, or silently rewrite RP lineage."
                    )
                if parent.subject_id != request.subject_id:
                    return (
                        "next_request.parent_rp_id references an active RP for a different subject: "
                        f"parent={request.parent_rp_id} parent_subject={parent.subject_id} "
                        f"request_subject={request.subject_id}. Parent/child RP lineage must remain within one subject."
                    )

        raw_updates = decision.research_state.get("predictive_hypothesis_updates", [])
        if raw_updates not in (None, []):
            if not isinstance(raw_updates, list):
                return "research_state.predictive_hypothesis_updates must be a list"
            if decision.rp_id and self._research_package_store.load(decision.rp_id) is None:
                return (
                    "predictive_hypothesis_updates reference an RP that is not yet durable: "
                    f"{decision.rp_id}. Establish that RP first through an objectively valid accepted Analysis "
                    "request, then author the predictive hypothesis update in a subsequent decision. "
                    "Deterministic code will not auto-create the RP or move the hypothesis between RPs."
                )

        if not decision.continue_research:
            reason = decision.close_reason
            if not isinstance(reason, str) or not reason.strip():
                return (
                    "continue_research is false but close_reason is blank; RD must explicitly state its scientific "
                    "reason for closure. Deterministic code will not author or infer that reason."
                )
        return None

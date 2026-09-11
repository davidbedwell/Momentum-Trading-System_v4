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
            "generalizes. Generalization itself must remain falsifiable. If the current subject was selected first "
            "for blind validation of a prior hypothesis, preserve the no-look-ahead validation boundary and complete "
            "the validation trial before unrestricted exploratory use of that subject. When subject_phase_contract "
            "is present, it is the already-accepted objective phase contract for this run. Do not switch the subject "
            "from EXPLORATION to VALIDATION or from VALIDATION to EXPLORATION inside an ordinary decision. A new "
            "predictive hypothesis may be scientifically authored during exploration, but its research package must "
            "already exist durably before predictive_hypothesis_updates are emitted. Establish a new RP through an "
            "accepted Analysis request first, then emit the hypothesis update in a later decision."
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

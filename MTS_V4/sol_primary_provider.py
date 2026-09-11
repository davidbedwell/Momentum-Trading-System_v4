from __future__ import annotations

from typing import Mapping

from .contracts import ResearchDecision
from .sol_provider import SolResearchPackageAwareResearchDirector


class SolPrimaryResearchDirector(SolResearchPackageAwareResearchDirector):
    """Primary Sol RD with cross-subject context and objective closure guardrails."""

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
            "the validation trial before unrestricted exploratory use of that subject."
        )
        return [{"role": "system", "content": system}, messages[1]]

    def _decision_representation_defect(
        self,
        operation: str,
        decision: ResearchDecision,
        payload: Mapping[str, object],
    ) -> str | None:
        defect = super()._decision_representation_defect(operation, decision, payload)
        if defect is not None:
            return defect
        if not decision.continue_research:
            reason = decision.close_reason
            if not isinstance(reason, str) or not reason.strip():
                return (
                    "continue_research is false but close_reason is blank; RD must explicitly state its scientific "
                    "reason for closure. Deterministic code will not author or infer that reason."
                )
        return None

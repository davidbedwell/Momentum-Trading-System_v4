from __future__ import annotations

from typing import Mapping

from .contracts import ResearchDecision
from .research_package_provider import ResearchPackageAwareResearchDirector


class RPRepresentationAppellateResearchDirector(ResearchPackageAwareResearchDirector):
    """Primary RD that escalates exhausted RP-representation repair to an appellate AI.

    The primary AI retains three opportunities to repair its own research-package
    representation. Deterministic code detects only representation defects. If the
    primary exhausts that budget, the appellate AI receives the exact exhaustion
    defect and governed context and authors the scientific disposition itself.
    """

    _RP_REPAIR_EXHAUSTED_PREFIX = "research package representation repair budget exhausted: "

    def __init__(
        self,
        *,
        appeal: ResearchPackageAwareResearchDirector,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self._rp_representation_appeal = appeal

    def _request_decision(
        self,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> ResearchDecision:
        try:
            return super()._request_decision(
                operation=operation,
                mission=mission,
                payload=payload,
            )
        except ValueError as exc:
            message = str(exc)
            if not message.startswith(self._RP_REPAIR_EXHAUSTED_PREFIX):
                raise

            defect = message[len(self._RP_REPAIR_EXHAUSTED_PREFIX) :]
            appeal_payload = dict(payload)
            nexus_context = appeal_payload.get("nexus_context")
            governed_context = (
                dict(nexus_context) if isinstance(nexus_context, Mapping) else {}
            )
            governed_context["ai_appeal"] = {
                "authority": "AUTHORIZED_AI_SCIENTIFIC_APPEAL",
                "failure_layer": "RESEARCH_PACKAGE_REPRESENTATION",
                "primary_representation_repairs_exhausted": self._MAX_RP_REPRESENTATION_REPAIRS,
                "objective_representation_defect": defect,
                "instruction": (
                    "The local AI exhausted its authorized research-package representation repair "
                    "attempts. You are the superior AI scientific authority for this appeal scope. "
                    "Author a complete scientific disposition and valid RP/question lineage. You may "
                    "affirm, revise, replace, branch, or close the research direction. Deterministic "
                    "code may validate objective representation but must not choose scientific lineage "
                    "or substitute scientific judgment."
                ),
            }
            appeal_payload["nexus_context"] = governed_context
            return self._rp_representation_appeal._request_decision(
                operation=operation,
                mission=mission,
                payload=appeal_payload,
            )

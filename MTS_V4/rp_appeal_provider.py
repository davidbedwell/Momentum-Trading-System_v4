from __future__ import annotations

import json
from typing import Mapping

from .contracts import ResearchDecision
from .rd_codec import ResearchDecisionCodec, ResearchDecisionDecodeError
from .research_package_provider import ResearchPackageAwareResearchDirector


class RPRepresentationAppellateResearchDirector(ResearchPackageAwareResearchDirector):
    """Primary RD with superior-AI appeal for exhausted representation repair.

    Research-package representation keeps its existing three-repair budget. Base
    decision representation also receives three local-AI repair opportunities in
    total: the inherited provider performs the first repair, this wrapper performs
    repairs two and three, and only then routes the exact final representation
    defect to the authorized appellate AI. Deterministic code detects, counts,
    validates, and routes representation defects; it does not author scientific
    fields, lineage, or disposition.
    """

    _RP_REPAIR_EXHAUSTED_PREFIX = "research package representation repair budget exhausted: "
    _MAX_DECISION_REPRESENTATION_REPAIRS = 3

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
        primary_payload = self._with_decision_representation_policy(payload)
        try:
            return super()._request_decision(
                operation=operation,
                mission=mission,
                payload=primary_payload,
            )
        except ResearchDecisionDecodeError as exc:
            return self._repair_or_appeal_decision_representation(
                operation=operation,
                mission=mission,
                payload=primary_payload,
                first_failed_repair_defect=str(exc),
            )
        except ValueError as exc:
            message = str(exc)
            if not message.startswith(self._RP_REPAIR_EXHAUSTED_PREFIX):
                raise

            defect = message[len(self._RP_REPAIR_EXHAUSTED_PREFIX) :]
            return self._route_representation_appeal(
                operation=operation,
                mission=mission,
                payload=primary_payload,
                failure_layer="RESEARCH_PACKAGE_REPRESENTATION",
                repairs_exhausted=self._MAX_RP_REPRESENTATION_REPAIRS,
                defect=defect,
                instruction=(
                    "The local AI exhausted its authorized research-package representation repair "
                    "attempts. You are the superior AI scientific authority for this appeal scope. "
                    "Author a complete scientific disposition and valid RP/question lineage. You may "
                    "affirm, revise, replace, branch, or close the research direction. Deterministic "
                    "code may validate objective representation but must not choose scientific lineage "
                    "or substitute scientific judgment."
                ),
            )

    def _repair_or_appeal_decision_representation(
        self,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
        first_failed_repair_defect: str,
    ) -> ResearchDecision:
        messages = self._decision_messages(
            operation=operation,
            mission=mission,
            payload=payload,
        )
        defect = first_failed_repair_defect

        for repair_attempt in range(2, self._MAX_DECISION_REPRESENTATION_REPAIRS + 1):
            repair_instruction = {
                "operation": "REPAIR_DECISION_REPRESENTATION",
                "repair_attempt": repair_attempt,
                "maximum_primary_representation_repairs": self._MAX_DECISION_REPRESENTATION_REPAIRS,
                "decode_defect": defect,
                "instruction": (
                    "Return one complete corrected decision JSON object. Preserve or revise your own "
                    "scientific choices as you judge appropriate, but satisfy the required decision "
                    "representation. Deterministic code will not fill missing scientific fields. If "
                    "continue_research is true, next_request must contain every required field in the "
                    "disclosed required_decision_schema, including subject_id, evidence_ids, and "
                    "analysis_inputs."
                ),
            }
            repaired_content = self._chat_completion(
                messages
                + [
                    {
                        "role": "user",
                        "content": json.dumps(
                            repair_instruction,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    }
                ]
            )
            try:
                return ResearchDecisionCodec.decode(repaired_content)
            except ResearchDecisionDecodeError as exc:
                defect = str(exc)

        return self._route_representation_appeal(
            operation=operation,
            mission=mission,
            payload=payload,
            failure_layer="DECISION_REPRESENTATION",
            repairs_exhausted=self._MAX_DECISION_REPRESENTATION_REPAIRS,
            defect=defect,
            instruction=(
                "The local AI exhausted its authorized decision-representation repair attempts. "
                "You are the superior AI scientific authority for this appeal scope. Author one "
                "complete scientific decision satisfying the disclosed decision schema. You may "
                "affirm, revise, replace, or close the research direction. Deterministic code may "
                "validate representation but must not fill missing scientific fields or substitute "
                "scientific judgment."
            ),
        )

    def _route_representation_appeal(
        self,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
        failure_layer: str,
        repairs_exhausted: int,
        defect: str,
        instruction: str,
    ) -> ResearchDecision:
        appeal_payload = dict(payload)
        nexus_context = appeal_payload.get("nexus_context")
        governed_context = (
            dict(nexus_context) if isinstance(nexus_context, Mapping) else {}
        )
        governed_context["ai_appeal"] = {
            "authority": "AUTHORIZED_AI_SCIENTIFIC_APPEAL",
            "failure_layer": failure_layer,
            "primary_representation_repairs_exhausted": repairs_exhausted,
            "objective_representation_defect": defect,
            "instruction": instruction,
        }
        appeal_payload["nexus_context"] = governed_context
        return self._rp_representation_appeal._request_decision(
            operation=operation,
            mission=mission,
            payload=appeal_payload,
        )

    @classmethod
    def _with_decision_representation_policy(
        cls,
        payload: Mapping[str, object],
    ) -> dict[str, object]:
        governed_payload = dict(payload)
        requirements = governed_payload.get("objective_execution_requirements")
        if isinstance(requirements, Mapping):
            governed_requirements = dict(requirements)
            governed_requirements["decision_representation_repair_policy"] = (
                "Return each exact decode defect to the local AI for up to three representation "
                "repairs; deterministic code does not fill scientific fields; after exhaustion, "
                "route the exact final defect to the authorized superior AI appeal provider."
            )
            governed_payload["objective_execution_requirements"] = governed_requirements
        return governed_payload

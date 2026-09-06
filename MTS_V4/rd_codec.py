from __future__ import annotations

import json
from typing import Any, Mapping

from .contracts import AnalysisRequest, Finding, ResearchDecision, ResearchPhase


class ResearchDecisionDecodeError(ValueError):
    pass


class ResearchDecisionCodec:
    """Strict representation codec for AI-authored scientific decisions.

    Parsing and schema enforcement are deterministic representation duties.
    The codec does not supply missing scientific content and does not restrict
    the open scientific metadata namespace of a finding.
    """

    @staticmethod
    def decode(text: str) -> ResearchDecision:
        raw = ResearchDecisionCodec._extract_json(text)
        if not isinstance(raw, Mapping):
            raise ResearchDecisionDecodeError("RD response must be a JSON object")

        continue_research = raw.get("continue_research")
        if not isinstance(continue_research, bool):
            raise ResearchDecisionDecodeError("continue_research must be boolean")

        next_request = None
        request_raw = raw.get("next_request")
        if request_raw is not None:
            if not isinstance(request_raw, Mapping):
                raise ResearchDecisionDecodeError("next_request must be an object or null")
            next_request = ResearchDecisionCodec._decode_request(request_raw)

        findings_raw = raw.get("promote_findings", [])
        if not isinstance(findings_raw, list):
            raise ResearchDecisionDecodeError("promote_findings must be a list")
        findings = tuple(ResearchDecisionCodec._decode_finding(item) for item in findings_raw)

        research_state = raw.get("research_state", {})
        if not isinstance(research_state, Mapping):
            raise ResearchDecisionDecodeError("research_state must be an object")

        close_reason = raw.get("close_reason")
        if close_reason is not None and not isinstance(close_reason, str):
            raise ResearchDecisionDecodeError("close_reason must be string or null")

        if continue_research and next_request is None:
            raise ResearchDecisionDecodeError(
                "continuing research requires an AI-authored next_request"
            )

        return ResearchDecision(
            continue_research=continue_research,
            next_request=next_request,
            promote_findings=findings,
            research_state=dict(research_state),
            close_reason=close_reason,
        )

    @staticmethod
    def _decode_request(raw: Mapping[str, Any]) -> AnalysisRequest:
        required = (
            "request_id",
            "subject_id",
            "question",
            "method_id",
            "evidence_ids",
            "parameters",
            "research_phase",
        )
        missing = [key for key in required if key not in raw]
        if missing:
            raise ResearchDecisionDecodeError(
                f"next_request missing required fields: {missing}"
            )
        evidence_ids = raw["evidence_ids"]
        parameters = raw["parameters"]
        if not isinstance(evidence_ids, list) or not all(isinstance(x, str) for x in evidence_ids):
            raise ResearchDecisionDecodeError("evidence_ids must be a list of strings")
        if not isinstance(parameters, Mapping):
            raise ResearchDecisionDecodeError("parameters must be an object")
        try:
            phase = ResearchPhase(str(raw["research_phase"]))
        except ValueError as exc:
            raise ResearchDecisionDecodeError(
                "research_phase must be EXPLORATION or VALIDATION"
            ) from exc
        return AnalysisRequest(
            request_id=str(raw["request_id"]),
            subject_id=str(raw["subject_id"]),
            question=str(raw["question"]),
            method_id=str(raw["method_id"]),
            evidence_ids=tuple(evidence_ids),
            parameters=dict(parameters),
            research_phase=phase,
            rationale=str(raw.get("rationale", "")),
        )

    @staticmethod
    def _decode_finding(raw: Any) -> Finding:
        if not isinstance(raw, Mapping):
            raise ResearchDecisionDecodeError("each promoted finding must be an object")
        required = (
            "finding_id",
            "subject_id",
            "statement",
            "supporting_result_ids",
            "evidence_ids",
        )
        missing = [key for key in required if key not in raw]
        if missing:
            raise ResearchDecisionDecodeError(
                f"finding missing required envelope fields: {missing}"
            )

        supporting_result_ids = raw["supporting_result_ids"]
        evidence_ids = raw["evidence_ids"]
        metadata = raw.get("metadata", {})
        if not isinstance(supporting_result_ids, list) or not all(
            isinstance(value, str) for value in supporting_result_ids
        ):
            raise ResearchDecisionDecodeError("supporting_result_ids must be a list of strings")
        if not isinstance(evidence_ids, list) or not all(
            isinstance(value, str) for value in evidence_ids
        ):
            raise ResearchDecisionDecodeError("finding evidence_ids must be a list of strings")
        if not isinstance(metadata, Mapping):
            raise ResearchDecisionDecodeError("finding metadata must be an object")

        return Finding(
            finding_id=str(raw["finding_id"]),
            subject_id=str(raw["subject_id"]),
            statement=str(raw["statement"]),
            supporting_result_ids=tuple(supporting_result_ids),
            evidence_ids=tuple(evidence_ids),
            metadata=dict(metadata),
        )

    @staticmethod
    def _extract_json(text: str) -> Any:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as exc:
            start = stripped.find("{")
            end = stripped.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(stripped[start : end + 1])
                except json.JSONDecodeError:
                    pass
            raise ResearchDecisionDecodeError(
                f"RD response is not valid JSON: {exc}"
            ) from exc

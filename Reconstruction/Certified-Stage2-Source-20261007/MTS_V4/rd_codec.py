from __future__ import annotations

import json
from typing import Any, Mapping

from .contracts import AnalysisRequest, AnalysisResultInput, Finding, ResearchDecision, ResearchPhase


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

        rp_id = raw.get("rp_id")
        if rp_id is not None and (not isinstance(rp_id, str) or not rp_id.strip()):
            raise ResearchDecisionDecodeError("rp_id must be a nonblank string or null")

        analysis_interpretation = raw.get("analysis_interpretation")
        if analysis_interpretation is not None and not isinstance(analysis_interpretation, str):
            raise ResearchDecisionDecodeError(
                "analysis_interpretation must be string or null"
            )

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
            rp_id=rp_id,
            analysis_interpretation=analysis_interpretation,
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
        analysis_inputs_raw = raw.get("analysis_inputs", [])
        if not isinstance(analysis_inputs_raw, list):
            raise ResearchDecisionDecodeError("analysis_inputs must be a list")
        analysis_inputs = tuple(
            ResearchDecisionCodec._decode_analysis_input(item)
            for item in analysis_inputs_raw
        )
        try:
            phase = ResearchPhase(str(raw["research_phase"]))
        except ValueError as exc:
            raise ResearchDecisionDecodeError(
                "research_phase must be EXPLORATION or VALIDATION"
            ) from exc

        lineage: dict[str, str | None] = {}
        for key in ("rp_id", "question_id", "parent_question_id", "parent_rp_id"):
            value = raw.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ResearchDecisionDecodeError(
                    f"next_request {key} must be a nonblank string or null"
                )
            lineage[key] = value

        return AnalysisRequest(
            request_id=str(raw["request_id"]),
            subject_id=str(raw["subject_id"]),
            question=str(raw["question"]),
            method_id=str(raw["method_id"]),
            evidence_ids=tuple(evidence_ids),
            parameters=dict(parameters),
            research_phase=phase,
            rationale=str(raw.get("rationale", "")),
            analysis_inputs=analysis_inputs,
            rp_id=lineage["rp_id"],
            question_id=lineage["question_id"],
            parent_question_id=lineage["parent_question_id"],
            parent_rp_id=lineage["parent_rp_id"],
        )

    @staticmethod
    def _decode_analysis_input(raw: Any) -> AnalysisResultInput:
        if not isinstance(raw, Mapping):
            raise ResearchDecisionDecodeError("each analysis_inputs entry must be an object")
        required = ("result_id", "output_path", "input_name")
        missing = [key for key in required if key not in raw]
        if missing:
            raise ResearchDecisionDecodeError(
                f"analysis input missing required fields: {missing}"
            )
        output_path = raw["output_path"]
        if not isinstance(output_path, list) or not all(
            isinstance(value, (str, int)) and not isinstance(value, bool)
            for value in output_path
        ):
            raise ResearchDecisionDecodeError(
                "analysis input output_path must be a list of string/integer path components"
            )
        result_id = raw["result_id"]
        input_name = raw["input_name"]
        if not isinstance(result_id, str) or not result_id.strip():
            raise ResearchDecisionDecodeError("analysis input result_id must be a nonblank string")
        if not isinstance(input_name, str) or not input_name.strip():
            raise ResearchDecisionDecodeError("analysis input input_name must be a nonblank string")
        return AnalysisResultInput(
            result_id=result_id,
            output_path=tuple(output_path),
            input_name=input_name,
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
        allowed = set(required) | {"metadata"}
        missing = [key for key in required if key not in raw]
        if missing:
            raise ResearchDecisionDecodeError(
                f"finding missing required envelope fields: {missing}"
            )
        unexpected = sorted(str(key) for key in raw if key not in allowed)
        if unexpected:
            raise ResearchDecisionDecodeError(
                "finding has fields outside the closed envelope: "
                f"{unexpected}; place additional scientific labels under metadata"
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

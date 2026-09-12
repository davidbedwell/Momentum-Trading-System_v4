from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from .batch_contracts import BatchAnalysisRecord, BatchExecutionReport, BatchResearchDecision
from .batch_rd_codec import BatchResearchDecisionCodec
from .batch_research_recording import BatchCampaignResearchRecorder
from .contracts import AnalysisRequest, AnalysisResult, AnalysisResultInput, ResearchPhase, SubjectMetadata
from .nexus_json import JsonResearchNexus
from .research_package_store import JsonResearchPackageStore


class BatchCampaignReconstructionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ReconstructedBatchCampaign:
    campaign_id: str
    subject: SubjectMetadata
    decisions: tuple[BatchResearchDecision, ...]
    reports: tuple[BatchExecutionReport, ...]
    results_by_analysis_id: Mapping[str, AnalysisResult]
    analyses_executed: int
    findings_promoted: int

    @property
    def latest_decision(self) -> BatchResearchDecision:
        return self.decisions[-1]

    @property
    def latest_report(self) -> BatchExecutionReport:
        return self.reports[-1]


def _require_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BatchCampaignReconstructionError(f"{label} must be an object")
    return value


def _require_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise BatchCampaignReconstructionError(f"{label} must be a list")
    return value


def _decode_analysis_request(raw: Mapping[str, Any]) -> AnalysisRequest:
    inputs = tuple(
        AnalysisResultInput(
            result_id=str(item["result_id"]),
            output_path=tuple(item.get("output_path", ())),
            input_name=str(item["input_name"]),
        )
        for item in _require_list(raw.get("analysis_inputs", []), "analysis_inputs")
    )
    try:
        phase = ResearchPhase(str(raw["research_phase"]))
    except (KeyError, ValueError) as exc:
        raise BatchCampaignReconstructionError("compiled request has invalid research_phase") from exc
    return AnalysisRequest(
        request_id=str(raw["request_id"]),
        subject_id=str(raw["subject_id"]),
        question=str(raw["question"]),
        method_id=str(raw["method_id"]),
        evidence_ids=tuple(str(value) for value in raw.get("evidence_ids", ())),
        parameters=dict(_require_mapping(raw.get("parameters", {}), "request.parameters")),
        research_phase=phase,
        rationale=str(raw.get("rationale", "")),
        analysis_inputs=inputs,
        rp_id=None if raw.get("rp_id") is None else str(raw["rp_id"]),
        question_id=None if raw.get("question_id") is None else str(raw["question_id"]),
        parent_question_id=(
            None if raw.get("parent_question_id") is None else str(raw["parent_question_id"])
        ),
        parent_rp_id=None if raw.get("parent_rp_id") is None else str(raw["parent_rp_id"]),
    )


def _decode_analysis_result(raw: Mapping[str, Any]) -> AnalysisResult:
    return AnalysisResult(
        result_id=str(raw["result_id"]),
        request_id=str(raw["request_id"]),
        subject_id=str(raw["subject_id"]),
        method_id=str(raw["method_id"]),
        outputs=dict(_require_mapping(raw.get("outputs", {}), "result.outputs")),
        evidence_ids=tuple(str(value) for value in raw.get("evidence_ids", ())),
        limitations=tuple(str(value) for value in raw.get("limitations", ())),
        execution_metadata=dict(
            _require_mapping(raw.get("execution_metadata", {}), "result.execution_metadata")
        ),
    )


def decode_batch_execution_report(raw: Mapping[str, Any]) -> BatchExecutionReport:
    records: list[BatchAnalysisRecord] = []
    for index, item in enumerate(_require_list(raw.get("records"), "report.records")):
        record = _require_mapping(item, f"report.records[{index}]")
        compiled_raw = record.get("compiled_request")
        result_raw = record.get("result")
        compiled = (
            None
            if compiled_raw is None
            else _decode_analysis_request(_require_mapping(compiled_raw, "compiled_request"))
        )
        result = (
            None
            if result_raw is None
            else _decode_analysis_result(_require_mapping(result_raw, "result"))
        )
        if compiled is not None and result is not None:
            if result.request_id != compiled.request_id:
                raise BatchCampaignReconstructionError(
                    f"report record {record.get('analysis_id')} result/request lineage mismatch"
                )
            if result.subject_id != compiled.subject_id or result.method_id != compiled.method_id:
                raise BatchCampaignReconstructionError(
                    f"report record {record.get('analysis_id')} result contract mismatch"
                )
        records.append(
            BatchAnalysisRecord(
                analysis_id=str(record["analysis_id"]),
                rp_id=str(record["rp_id"]),
                status=str(record["status"]),
                compiled_request=compiled,
                result=result,
                objective_defect=(
                    None if record.get("objective_defect") is None else str(record["objective_defect"])
                ),
                binding_map=dict(_require_mapping(record.get("binding_map", {}), "binding_map")),
                mechanical_repairs=tuple(str(value) for value in record.get("mechanical_repairs", ())),
            )
        )
    return BatchExecutionReport(records=tuple(records))


def _load_jsonl(path: str | Path) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BatchCampaignReconstructionError(
                f"invalid JSONL at {path}:{line_number}: {exc}"
            ) from exc
        result.append(_require_mapping(value, f"{path}:{line_number}"))
    return result


def _decision_from_row(row: Mapping[str, Any]) -> BatchResearchDecision:
    raw = _require_mapping(row.get("decision"), "decision row.decision")
    return BatchResearchDecisionCodec.decode(json.dumps(raw, sort_keys=True, default=str))


def _report_from_row(row: Mapping[str, Any]) -> BatchExecutionReport:
    return decode_batch_execution_report(_require_mapping(row.get("report"), "report row.report"))


def _analysis_ids(decision: BatchResearchDecision) -> tuple[str, ...]:
    return tuple(
        analysis.analysis_id
        for package in decision.research_packages
        for analysis in package.analyses
    )


def reconstruct_batched_campaign(
    *,
    decisions_jsonl: str | Path,
    reports_jsonl: str | Path,
    nexus_json: str | Path,
    package_store_dir: str | Path,
    campaign_id: str,
    subject_id: str,
) -> ReconstructedBatchCampaign:
    if not campaign_id.strip():
        raise BatchCampaignReconstructionError("campaign_id cannot be blank")
    decision_rows = _load_jsonl(decisions_jsonl)
    report_rows = _load_jsonl(reports_jsonl)
    if not decision_rows or not report_rows:
        raise BatchCampaignReconstructionError("reconstruction requires at least one decision and report")
    if len(decision_rows) != len(report_rows):
        raise BatchCampaignReconstructionError(
            f"decision/report count mismatch: {len(decision_rows)} decisions vs {len(report_rows)} reports"
        )

    nexus = JsonResearchNexus(nexus_json)
    subject = nexus.get_subject(subject_id)
    if subject is None:
        raise BatchCampaignReconstructionError(f"Nexus does not contain subject: {subject_id}")

    store_path = Path(package_store_dir)
    if store_path.exists() and any(store_path.iterdir()):
        raise BatchCampaignReconstructionError(
            f"package_store_dir must be absent or empty for deterministic reconstruction: {store_path}"
        )
    store = JsonResearchPackageStore(store_path)
    recorder = BatchCampaignResearchRecorder(package_store=store)

    decisions: list[BatchResearchDecision] = []
    reports: list[BatchExecutionReport] = []
    results_by_analysis_id: dict[str, AnalysisResult] = {}
    prior_report: BatchExecutionReport | None = None
    prior_analyses_executed = 0
    promoted_ids: list[str] = []

    for sequence, (decision_row, report_row) in enumerate(zip(decision_rows, report_rows), start=1):
        recorded_sequence = decision_row.get("decision_sequence")
        if recorded_sequence is not None and int(recorded_sequence) != sequence:
            raise BatchCampaignReconstructionError(
                f"noncontiguous decision_sequence at {sequence}: {recorded_sequence}"
            )
        recorded_report_decisions = report_row.get("decisions")
        if recorded_report_decisions is not None and int(recorded_report_decisions) != sequence:
            raise BatchCampaignReconstructionError(
                f"report decision counter mismatch at {sequence}: {recorded_report_decisions}"
            )

        decision = _decision_from_row(decision_row)
        report = _report_from_row(report_row)
        planned_ids = _analysis_ids(decision)
        report_ids = tuple(record.analysis_id for record in report.records)
        if len(report_ids) != len(planned_ids) or set(report_ids) != set(planned_ids):
            raise BatchCampaignReconstructionError(
                f"decision/report analysis membership mismatch at batch {sequence}"
            )

        recorder.record_plan(campaign_id=campaign_id, subject=subject, decision=decision)
        recorder.record_predictive_hypothesis_updates(decision, current_report=prior_report)
        recorder.record_closures(decision)

        for record in report.records:
            if record.compiled_request is not None and record.result is not None:
                recorder.record_accepted_request(
                    campaign_id=campaign_id,
                    subject=subject,
                    request=record.compiled_request,
                )
            if record.result is not None:
                prior = results_by_analysis_id.get(record.analysis_id)
                if prior is not None and prior != record.result:
                    raise BatchCampaignReconstructionError(
                        f"analysis_id reused with different result: {record.analysis_id}"
                    )
                results_by_analysis_id[record.analysis_id] = record.result
        recorder.record_report(report)

        for finding in decision.promote_findings:
            durable = nexus.get_finding(finding.finding_id)
            if durable != finding:
                raise BatchCampaignReconstructionError(
                    f"Nexus finding does not match recorded promoted finding: {finding.finding_id}"
                )
            promoted_ids.append(finding.finding_id)

        cumulative = report_row.get("analyses_executed")
        executed_this_report = sum(1 for record in report.records if record.result is not None)
        expected_cumulative = prior_analyses_executed + executed_this_report
        if cumulative is not None and int(cumulative) != expected_cumulative:
            raise BatchCampaignReconstructionError(
                f"analysis execution counter mismatch at batch {sequence}: "
                f"recorded {cumulative}, reconstructed {expected_cumulative}"
            )
        prior_analyses_executed = expected_cumulative
        decisions.append(decision)
        reports.append(report)
        prior_report = report

    if not decisions[-1].continue_research:
        raise BatchCampaignReconstructionError(
            "latest accepted decision is already closed; there is no broken interpretation boundary to resume"
        )

    nexus_result_ids = {
        item.result_id for item in nexus.analysis_result_metadata_for_subject(subject.subject_id)
    }
    reconstructed_result_ids = {result.result_id for result in results_by_analysis_id.values()}
    if nexus_result_ids != reconstructed_result_ids:
        missing = sorted(reconstructed_result_ids - nexus_result_ids)
        extra = sorted(nexus_result_ids - reconstructed_result_ids)
        raise BatchCampaignReconstructionError(
            f"Nexus/result replay mismatch; missing_in_nexus={missing}, extra_in_nexus={extra}"
        )

    return ReconstructedBatchCampaign(
        campaign_id=campaign_id,
        subject=subject,
        decisions=tuple(decisions),
        reports=tuple(reports),
        results_by_analysis_id=dict(results_by_analysis_id),
        analyses_executed=prior_analyses_executed,
        findings_promoted=len(promoted_ids),
    )

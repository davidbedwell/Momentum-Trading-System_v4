from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from MTS_V4.batch_rd_codec import (
    BatchResearchDecisionCodec,
    BatchResearchDecisionDecodeError,
)
from MTS_V4.qwen_current_capability import (
    blinded_cases_from_state_dirs,
    discover_control_state_dirs,
    mechanical_capability_report,
)
from MTS_V4.qwen_prompt_compaction import compact_qwen_messages
from scripts.run_qwen_shadow_replay import _objective_contract_valid


MAX_QWEN_REPRESENTATION_REPAIRS = 2
SCIENTIFIC_SENTINEL_MAX_OUTPUT_TOKENS = 8_000


def _model(base_url: str, configured: str | None) -> str:
    if configured and configured.strip():
        return configured.strip()
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/v1/models", timeout=30) as response:
        document = json.loads(response.read().decode("utf-8"))
    data = document.get("data", [])
    if not data or not isinstance(data[0].get("id"), str):
        raise RuntimeError("Qwen /v1/models did not expose a model id")
    return data[0]["id"]


def _decision_json_schema():
    nonblank = {"type": "string", "minLength": 1}
    nullable_nonblank = {"anyOf": [nonblank, {"type": "null"}]}
    input_required = ["role", "evidence_id", "analysis_id", "dataset_name"]
    input_reference = {
        "type": "object",
        "required": input_required,
        "properties": {
            "role": nonblank,
            "evidence_id": nullable_nonblank,
            "analysis_id": nullable_nonblank,
            "dataset_name": nullable_nonblank,
        },
        "oneOf": [
            {
                "required": input_required,
                "properties": {
                    "role": nonblank,
                    "evidence_id": nonblank,
                    "analysis_id": {"type": "null"},
                    "dataset_name": {"type": "null"},
                },
                "additionalProperties": False,
            },
            {
                "required": input_required,
                "properties": {
                    "role": nonblank,
                    "evidence_id": {"type": "null"},
                    "analysis_id": nonblank,
                    "dataset_name": nullable_nonblank,
                },
                "additionalProperties": False,
            },
        ],
        "additionalProperties": False,
    }
    analysis = {
        "type": "object",
        "required": [
            "analysis_id", "rp_id", "question_id", "subject_id", "question",
            "method_id", "inputs", "parameters", "research_phase",
        ],
        "properties": {
            "analysis_id": nonblank,
            "rp_id": nonblank,
            "question_id": nonblank,
            "subject_id": nonblank,
            "question": nonblank,
            "method_id": nonblank,
            "inputs": {"type": "array", "items": input_reference},
            "parameters": {"type": "object"},
            "research_phase": {"enum": ["EXPLORATION", "VALIDATION"]},
            "rationale": {"type": "string"},
            "parent_question_id": nullable_nonblank,
            "parent_rp_id": nullable_nonblank,
        },
        "additionalProperties": False,
    }
    package = {
        "type": "object",
        "required": ["rp_id", "objective", "analyses"],
        "properties": {
            "rp_id": nonblank,
            "objective": nonblank,
            "analyses": {"type": "array", "minItems": 1, "items": analysis},
            "parent_rp_id": nullable_nonblank,
            "decision_boundary": nullable_nonblank,
        },
        "additionalProperties": False,
    }
    closure = {
        "type": "object",
        "required": ["rp_id", "close_reason"],
        "properties": {
            "rp_id": nonblank,
            "close_reason": nonblank,
            "final_assessment": nullable_nonblank,
        },
        "additionalProperties": False,
    }
    finding = {
        "type": "object",
        "required": [
            "finding_id", "subject_id", "statement", "supporting_result_ids", "evidence_ids",
        ],
        "properties": {
            "finding_id": nonblank,
            "subject_id": nonblank,
            "statement": nonblank,
            "supporting_result_ids": {"type": "array", "items": nonblank},
            "evidence_ids": {"type": "array", "items": nonblank},
            "metadata": {"type": "object"},
        },
        "additionalProperties": False,
    }
    progress = {
        "type": "object",
        "required": [
            "estimated_percent_complete", "estimated_remaining_batches",
            "estimated_remaining_sol_calls", "estimate_confidence", "estimate_rationale",
        ],
        "properties": {
            "estimated_percent_complete": {"type": "number", "minimum": 0, "maximum": 100},
            "estimated_remaining_batches": {"type": "integer", "minimum": 0},
            "estimated_remaining_sol_calls": {"type": "integer", "minimum": 0},
            "estimate_confidence": nonblank,
            "estimate_rationale": nonblank,
        },
        "additionalProperties": False,
    }
    schema = {
        "type": "object",
        "required": [
            "continue_research", "waiting_for_future_cohorts", "research_packages",
            "rp_closures", "promote_findings", "research_state", "close_reason",
            "batch_interpretation", "research_progress",
        ],
        "properties": {
            "continue_research": {"type": "boolean"},
            "waiting_for_future_cohorts": {"type": "boolean"},
            "research_packages": {"type": "array", "items": package},
            "rp_closures": {"type": "array", "items": closure},
            "promote_findings": {"type": "array", "items": finding},
            "research_state": {"type": "object"},
            "close_reason": nullable_nonblank,
            "batch_interpretation": nullable_nonblank,
            "research_progress": {"anyOf": [progress, {"type": "null"}]},
        },
        "additionalProperties": False,
    }
    schema["oneOf"] = [
        {
            "properties": {
                "continue_research": {"const": True},
                "waiting_for_future_cohorts": {"const": False},
                "research_packages": {"type": "array", "minItems": 1, "items": package},
                "close_reason": {"type": "null"},
            }
        },
        {
            "properties": {
                "continue_research": {"const": True},
                "waiting_for_future_cohorts": {"const": True},
                "research_packages": {"type": "array", "maxItems": 0, "items": package},
                "close_reason": {"type": "null"},
            }
        },
        {
            "properties": {
                "continue_research": {"const": False},
                "waiting_for_future_cohorts": {"const": False},
                "research_packages": {"type": "array", "maxItems": 0, "items": package},
                "close_reason": nonblank,
            }
        },
    ]
    return schema


def _token_count(base_url: str, model: str, messages, timeout: int) -> int:
    body = json.dumps(
        {"model": model, "messages": messages, "add_generation_prompt": True},
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/tokenize",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        document = json.loads(response.read().decode("utf-8"))
    count = document.get("count")
    if not isinstance(count, int):
        tokens = document.get("tokens")
        if not isinstance(tokens, list):
            raise RuntimeError("Qwen /tokenize response contains neither count nor tokens")
        count = len(tokens)
    return count


def _chat(
    base_url: str,
    model: str,
    messages,
    timeout: int,
    max_output_tokens: int,
    *,
    enable_thinking: bool,
) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": max_output_tokens,
            "chat_template_kwargs": {"enable_thinking": enable_thinking},
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "mts_v4_batch_research_decision",
                    "strict": True,
                    "schema": _decision_json_schema(),
                },
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        document = json.loads(response.read().decode("utf-8"))
    message = document["choices"][0]["message"]
    content = message.get("content") or message.get("reasoning_content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Qwen returned no textual decision")
    return content


def _schema_smoke_messages(requested_state: str):
    return [
        {
            "role": "system",
            "content": (
                "Return one concise MTS V4 BatchResearchDecision matching the requested_state "
                "exactly. This is a representation test, not scientific research."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "requested_state": requested_state,
                    "subject_id": "universe:schema-smoke",
                    "available_evidence_id": "evidence:schema-smoke",
                    "available_method_id": "analysis.descriptive.statistics",
                    "available_input_role": "dataset",
                    "requirements": {
                        "EXECUTE": (
                            "continue=true, waiting=false, exactly one Research Package with "
                            "one Analysis using the available evidence_id; its input object must "
                            "include role='dataset' exactly and must not omit role"
                        ),
                        "WAIT": (
                            "continue=true, waiting=true, no Research Packages, close_reason=null"
                        ),
                        "CLOSE": (
                            "continue=false, waiting=false, no Research Packages, and a nonblank "
                            "close_reason"
                        ),
                    },
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        },
    ]


def _schema_smoke_state_valid(decision, requested_state: str) -> bool:
    if requested_state == "EXECUTE":
        if not (
            decision.continue_research
            and not decision.waiting_for_future_cohorts
            and len(decision.research_packages) == 1
            and len(decision.research_packages[0].analyses) == 1
        ):
            return False
        inputs = decision.research_packages[0].analyses[0].inputs
        return (
            len(inputs) == 1
            and inputs[0].role == "dataset"
            and inputs[0].evidence_id == "evidence:schema-smoke"
            and inputs[0].analysis_id is None
            and inputs[0].dataset_name is None
        )
    if requested_state == "WAIT":
        return (
            decision.continue_research
            and decision.waiting_for_future_cohorts
            and not decision.research_packages
        )
    if requested_state == "CLOSE":
        return (
            not decision.continue_research
            and not decision.waiting_for_future_cohorts
            and not decision.research_packages
            and bool(decision.close_reason and decision.close_reason.strip())
        )
    raise ValueError(f"unknown schema smoke state: {requested_state}")


def _representation_repair_messages(
    messages,
    *,
    raw_response: str,
    decode_defect: str,
    requested_state: str | None = None,
):
    instruction = {
        "operation": "REPAIR_BATCH_DECISION_REPRESENTATION",
        "decode_defect": decode_defect,
        "instruction": (
            "Return one complete, concise corrected decision JSON object. Correct the exact "
            "representation defect while preserving the selected method, evidence identity, "
            "scientific interpretation, and all scientific choices. Do not omit required input "
            "roles. Deterministic code will validate but will not invent or replace scientific "
            "content."
        ),
    }
    if requested_state is not None:
        instruction["requested_state"] = requested_state
    return list(messages) + [
        {"role": "assistant", "content": raw_response},
        {
            "role": "user",
            "content": json.dumps(instruction, sort_keys=True, separators=(",", ":")),
        },
    ]


def _write_jsonl(path: Path, items) -> None:
    with path.open("x", encoding="utf-8") as handle:
        for item in items:
            handle.write(
                json.dumps(item, sort_keys=True, default=str, separators=(",", ":"))
                + "\n"
            )


def _append_jsonl(path: Path, item) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(item, sort_keys=True, default=str, separators=(",", ":"))
            + "\n"
        )
        handle.flush()
        os.fsync(handle.fileno())


def _read_jsonl(path: Path):
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _select_cases(cases, *, case_ids, scientific_sentinel: bool):
    selected = tuple(cases)
    if case_ids:
        requested = list(case_ids)
        if len(requested) != len(set(requested)):
            raise RuntimeError("--case-id values must be unique")
        by_id = {case.case_id: case for case in selected}
        missing = [case_id for case_id in requested if case_id not in by_id]
        if missing:
            raise RuntimeError(f"requested Qwen capability case_id values are missing: {missing}")
        selected = tuple(by_id[case_id] for case_id in requested)
    if scientific_sentinel:
        if case_ids:
            raise RuntimeError("--scientific-sentinel cannot be combined with --case-id")
        by_control = {}
        for case in selected:
            if case.operation == "INTERPRET_BATCH_RESULTS":
                by_control[case.control_id] = case
        controls = sorted({case.control_id for case in selected})
        missing = [control for control in controls if control not in by_control]
        if missing:
            raise RuntimeError(
                f"scientific sentinel controls lack an interpretation case: {missing}"
            )
        selected = tuple(by_control[control] for control in controls)
    return selected


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Measure current local-Qwen planning and interpretation capability on blinded "
            "exact Sol prompt envelopes. Never sends Sol responses or hidden answers."
        )
    )
    parser.add_argument("--campaign-root", action="append", default=[])
    parser.add_argument("--state-dir", action="append", default=[])
    parser.add_argument("--exclude-control-id", action="append", default=[])
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--base-url",
        default=os.getenv("MTS_RD_AI_BASE_URL", "http://127.0.0.1:8000"),
    )
    parser.add_argument("--model", default=os.getenv("MTS_RD_AI_MODEL"))
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=int(os.getenv("MTS_RD_AI_TIMEOUT_SECONDS", "600")),
    )
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--schema-smoke-only", action="store_true")
    parser.add_argument("--scientific-sentinel", action="store_true")
    parser.add_argument("--disable-thinking", action="store_true")
    parser.add_argument("--input-token-budget", type=int, default=48_000)
    parser.add_argument("--max-output-tokens", type=int, default=8_000)
    parser.add_argument(
        "--retry-failed-from-output-dir",
        help=(
            "Carry forward only fingerprint-matching contract-valid cases from a prior "
            "capability output and rerun every failed or incomplete case."
        ),
    )
    args = parser.parse_args(argv)

    if args.scientific_sentinel and args.disable_thinking:
        raise RuntimeError(
            "--scientific-sentinel requires Qwen thinking; remove --disable-thinking"
        )
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    model = _model(args.base_url, args.model)

    if args.schema_smoke_only:
        if args.preflight_only or args.scientific_sentinel or args.case_id:
            raise RuntimeError(
                "--schema-smoke-only cannot be combined with replay selection modes"
            )
        result_path = output_dir / "qwen_schema_smoke_results.jsonl"
        _write_jsonl(result_path, [])
        smoke_results = []
        for requested_state in ("EXECUTE", "WAIT", "CLOSE"):
            print(f"QWEN_SCHEMA_SMOKE_STATE={requested_state}", flush=True)
            raw_response = None
            initial_raw_response = None
            decoded_decision = None
            valid = False
            failure = None
            repair_attempted = False
            generation_calls = 0
            messages = _schema_smoke_messages(requested_state)
            try:
                raw_response = _chat(
                    args.base_url,
                    model,
                    messages,
                    args.timeout_seconds,
                    min(args.max_output_tokens, 1_500),
                    enable_thinking=False,
                )
                generation_calls += 1
                try:
                    decision = BatchResearchDecisionCodec.decode(raw_response)
                except BatchResearchDecisionDecodeError as exc:
                    initial_raw_response = raw_response
                    repair_attempted = True
                    raw_response = _chat(
                        args.base_url,
                        model,
                        _representation_repair_messages(
                            messages,
                            raw_response=initial_raw_response,
                            decode_defect=str(exc),
                            requested_state=requested_state,
                        ),
                        args.timeout_seconds,
                        min(args.max_output_tokens, 1_500),
                        enable_thinking=False,
                    )
                    generation_calls += 1
                    decision = BatchResearchDecisionCodec.decode(raw_response)
                valid = _schema_smoke_state_valid(decision, requested_state)
                decoded_decision = asdict(decision)
                if not valid:
                    failure = "decoded decision did not match requested smoke state"
            except Exception as exc:
                failure = f"{type(exc).__name__}: {exc}"
            result = {
                "requested_state": requested_state,
                "valid": valid,
                "failure": failure,
                "repair_attempted": repair_attempted,
                "generation_calls": generation_calls,
                "initial_qwen_raw_response": initial_raw_response,
                "qwen_raw_response": raw_response,
                "qwen_decision": decoded_decision,
            }
            smoke_results.append(result)
            _append_jsonl(result_path, result)
        passed = all(item["valid"] for item in smoke_results)
        report = {
            "format": "MTS_V4_QWEN_SCHEMA_SMOKE_REPORT_V1",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "qwen_model": model,
            "states_tested": 3,
            "states_valid": sum(bool(item["valid"]) for item in smoke_results),
            "generation_calls": sum(int(item["generation_calls"]) for item in smoke_results),
            "representation_repairs_attempted": sum(
                bool(item["repair_attempted"]) for item in smoke_results
            ),
            "status": "PASS" if passed else "FAIL",
            "thinking_enabled": False,
            "sol_fallback_used": False,
        }
        (output_dir / "qwen_schema_smoke_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"QWEN_SCHEMA_SMOKE_STATUS={report['status']}")
        print(f"QWEN_SCHEMA_SMOKE_GENERATION_CALLS={report['generation_calls']}")
        print(
            "QWEN_SCHEMA_SMOKE_REPAIRS_ATTEMPTED="
            f"{report['representation_repairs_attempted']}"
        )
        print(f"OUTPUT_DIR={output_dir}")
        return 0 if passed else 2

    state_dirs = discover_control_state_dirs(
        campaign_roots=args.campaign_root,
        state_dirs=args.state_dir,
        excluded_control_ids=args.exclude_control_id,
    )
    all_cases = blinded_cases_from_state_dirs(state_dirs)
    if args.max_cases:
        all_cases = all_cases[: args.max_cases]
    all_cases = _select_cases(
        all_cases,
        case_ids=args.case_id,
        scientific_sentinel=args.scientific_sentinel,
    )
    effective_max_output_tokens = (
        min(args.max_output_tokens, SCIENTIFIC_SENTINEL_MAX_OUTPUT_TOKENS)
        if args.scientific_sentinel
        else args.max_output_tokens
    )

    if args.preflight_only:
        if args.retry_failed_from_output_dir:
            raise RuntimeError(
                "--preflight-only cannot be combined with --retry-failed-from-output-dir"
            )
        _write_jsonl(
            output_dir / "blinded_qwen_cases.jsonl",
            (case.to_mapping() for case in all_cases),
        )
        preflight_path = output_dir / "qwen_prompt_preflight.jsonl"
        compacted_path = output_dir / "compacted_qwen_cases.jsonl"
        manifest_path = output_dir / "qwen_prompt_compaction_manifests.jsonl"
        _write_jsonl(preflight_path, [])
        _write_jsonl(compacted_path, [])
        _write_jsonl(manifest_path, [])
        preflight_rows = []
        for index, case in enumerate(all_cases, start=1):
            print(
                f"QWEN_PREFLIGHT_CASE={index}/{len(all_cases)} CASE_ID={case.case_id}",
                flush=True,
            )
            compacted = None
            failure = None
            try:
                compacted = compact_qwen_messages(
                    list(case.messages),
                    token_counter=lambda messages: _token_count(
                        args.base_url, model, messages, args.timeout_seconds
                    ),
                    input_token_budget=args.input_token_budget,
                )
                _append_jsonl(
                    compacted_path,
                    {
                        "case_id": case.case_id,
                        "control_id": case.control_id,
                        "operation": case.operation,
                        "source_prompt_sha256": compacted.source_sha256,
                        "compacted_prompt_sha256": compacted.compacted_sha256,
                        "input_tokens": compacted.input_tokens,
                        "input_token_budget": args.input_token_budget,
                        "messages": compacted.messages,
                    },
                )
                _append_jsonl(
                    manifest_path,
                    {
                        "case_id": case.case_id,
                        "source_prompt_sha256": compacted.source_sha256,
                        "compacted_prompt_sha256": compacted.compacted_sha256,
                        "transformations": compacted.manifest,
                    },
                )
            except Exception as exc:
                failure = f"{type(exc).__name__}: {exc}"
            row = {
                "case_id": case.case_id,
                "control_id": case.control_id,
                "operation": case.operation,
                "prompt_sha256": case.prompt_sha256,
                "input_tokens": compacted.input_tokens if compacted else None,
                "within_budget": compacted is not None,
                "failure": failure,
            }
            preflight_rows.append(row)
            _append_jsonl(preflight_path, row)
        passed = all(item["within_budget"] for item in preflight_rows)
        token_counts = [
            int(item["input_tokens"])
            for item in preflight_rows
            if item["input_tokens"] is not None
        ]
        report = {
            "format": "MTS_V4_QWEN_PROMPT_PREFLIGHT_REPORT_V1",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "qwen_model": model,
            "cases": len(preflight_rows),
            "cases_within_budget": sum(bool(item["within_budget"]) for item in preflight_rows),
            "maximum_input_tokens": max(token_counts) if token_counts else None,
            "input_token_budget": args.input_token_budget,
            "model_generation_calls": 0,
            "status": "PASS" if passed else "FAIL",
        }
        (output_dir / "qwen_prompt_preflight_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"QWEN_PREFLIGHT_STATUS={report['status']}")
        print(f"QWEN_PREFLIGHT_CASES={report['cases']}")
        print(f"QWEN_PREFLIGHT_MAX_INPUT_TOKENS={report['maximum_input_tokens']}")
        print("QWEN_MODEL_GENERATION_CALLS=0")
        print(f"OUTPUT_DIR={output_dir}")
        return 0 if passed else 2

    prior_observations = []
    prior_decisions = []
    prior_compacted_cases = []
    prior_manifests = []
    if args.retry_failed_from_output_dir:
        prior_dir = Path(args.retry_failed_from_output_dir).expanduser().resolve()
        if not prior_dir.is_dir():
            raise RuntimeError(f"prior Qwen capability output is missing: {prior_dir}")
        prior_observations = _read_jsonl(prior_dir / "qwen_observations.jsonl")
        prior_decisions = _read_jsonl(
            prior_dir / "qwen_decisions_for_scientific_review.jsonl"
        )
        prior_compacted_cases = _read_jsonl(prior_dir / "compacted_qwen_cases.jsonl")
        prior_manifests = _read_jsonl(
            prior_dir / "qwen_prompt_compaction_manifests.jsonl"
        )

    case_by_id = {case.case_id: case for case in all_cases}
    if len(case_by_id) != len(all_cases):
        raise RuntimeError("current Qwen capability cases contain duplicate case_id values")
    valid_prior_by_id = {
        str(item.get("case_id")): item
        for item in prior_observations
        if bool(item.get("objective_contract_valid"))
    }
    prior_observation_by_id = {
        str(item.get("case_id")): item for item in prior_observations
    }
    prior_decision_by_id = {
        str(item.get("case_id")): item for item in prior_decisions
    }
    for case_id, observation in valid_prior_by_id.items():
        case = case_by_id.get(case_id)
        if case is None:
            raise RuntimeError(f"valid prior case is absent from current replay corpus: {case_id}")
        if observation.get("prompt_sha256") != case.prompt_sha256:
            raise RuntimeError(f"valid prior case prompt fingerprint changed: {case_id}")
        if case_id not in prior_decision_by_id:
            raise RuntimeError(f"valid prior case lacks its preserved Qwen decision: {case_id}")
    for case_id, observation in prior_observation_by_id.items():
        case = case_by_id.get(case_id)
        if case is not None and observation.get("prompt_sha256") != case.prompt_sha256:
            raise RuntimeError(f"prior case prompt fingerprint changed: {case_id}")
    cases = tuple(case for case in all_cases if case.case_id not in valid_prior_by_id)

    carried_observations = [
        {**valid_prior_by_id[case.case_id], "carried_from_prior_output": True}
        for case in all_cases
        if case.case_id in valid_prior_by_id
    ]
    carried_decisions = [
        {**prior_decision_by_id[case.case_id], "carried_from_prior_output": True}
        for case in all_cases
        if case.case_id in valid_prior_by_id
    ]
    carried_ids = set(valid_prior_by_id)
    carried_compacted_cases = [
        item for item in prior_compacted_cases if item.get("case_id") in carried_ids
    ]
    carried_manifests = [
        item for item in prior_manifests if item.get("case_id") in carried_ids
    ]

    _write_jsonl(
        output_dir / "blinded_qwen_cases.jsonl",
        (case.to_mapping() for case in all_cases),
    )
    observation_path = output_dir / "qwen_observations.jsonl"
    decision_path = output_dir / "qwen_decisions_for_scientific_review.jsonl"
    compacted_path = output_dir / "compacted_qwen_cases.jsonl"
    manifest_path = output_dir / "qwen_prompt_compaction_manifests.jsonl"
    _write_jsonl(observation_path, carried_observations)
    _write_jsonl(decision_path, carried_decisions)
    _write_jsonl(compacted_path, carried_compacted_cases)
    _write_jsonl(manifest_path, carried_manifests)
    observations = list(carried_observations)
    decisions = list(carried_decisions)
    for index, case in enumerate(cases, start=1):
        print(
            f"QWEN_CAPABILITY_CASE={index}/{len(cases)} "
            f"CONTROL={case.control_id} OPERATION={case.operation}",
            flush=True,
        )
        transport_success = False
        decoded = False
        contract_valid = False
        analysis_count = 0
        raw_response = None
        initial_raw_response = None
        decoded_decision = None
        failure = None
        compacted = None
        representation_repair_attempted = False
        representation_repair_attempt_number = 0
        generation_calls = 0
        try:
            compacted = compact_qwen_messages(
                list(case.messages),
                token_counter=lambda messages: _token_count(
                    args.base_url, model, messages, args.timeout_seconds
                ),
                input_token_budget=args.input_token_budget,
            )
            compacted_record = {
                "case_id": case.case_id,
                "control_id": case.control_id,
                "operation": case.operation,
                "source_prompt_sha256": compacted.source_sha256,
                "compacted_prompt_sha256": compacted.compacted_sha256,
                "input_tokens": compacted.input_tokens,
                "input_token_budget": args.input_token_budget,
                "messages": compacted.messages,
            }
            manifest_record = {
                "case_id": case.case_id,
                "source_prompt_sha256": compacted.source_sha256,
                "compacted_prompt_sha256": compacted.compacted_sha256,
                "transformations": compacted.manifest,
            }
            _append_jsonl(compacted_path, compacted_record)
            _append_jsonl(manifest_path, manifest_record)
            prior_observation = prior_observation_by_id.get(case.case_id)
            prior_decision_record = prior_decision_by_id.get(case.case_id)
            prior_repair_attempts = 0
            if prior_observation is not None:
                recorded_attempt = prior_observation.get(
                    "representation_repair_attempt_number"
                )
                if isinstance(recorded_attempt, int):
                    prior_repair_attempts = recorded_attempt
                elif prior_observation.get("representation_repair_attempted"):
                    prior_repair_attempts = 1
            prior_failed_response = (
                prior_decision_record.get("qwen_raw_response")
                if prior_observation is not None
                and not prior_observation.get("decision_decoded")
                and str(prior_observation.get("failure", "")).startswith(
                    "BatchResearchDecisionDecodeError:"
                )
                and prior_decision_record is not None
                else None
            )
            if isinstance(prior_failed_response, str) and prior_failed_response.strip():
                if prior_repair_attempts >= MAX_QWEN_REPRESENTATION_REPAIRS:
                    raise RuntimeError(
                        "Qwen representation repair budget exhausted for "
                        f"{case.case_id}: {prior_repair_attempts}/"
                        f"{MAX_QWEN_REPRESENTATION_REPAIRS}"
                    )
                initial_raw_response = prior_failed_response
                representation_repair_attempted = True
                representation_repair_attempt_number = prior_repair_attempts + 1
                request_messages = _representation_repair_messages(
                    list(compacted.messages),
                    raw_response=initial_raw_response,
                    decode_defect=str(prior_observation.get("failure")),
                )
            else:
                request_messages = list(compacted.messages)
            raw_response = _chat(
                args.base_url,
                model,
                request_messages,
                args.timeout_seconds,
                effective_max_output_tokens,
                enable_thinking=not args.disable_thinking,
            )
            generation_calls += 1
            transport_success = True
            try:
                decision = BatchResearchDecisionCodec.decode(raw_response)
            except BatchResearchDecisionDecodeError as exc:
                if representation_repair_attempted:
                    raise
                initial_raw_response = raw_response
                representation_repair_attempted = True
                representation_repair_attempt_number = 1
                raw_response = _chat(
                    args.base_url,
                    model,
                    _representation_repair_messages(
                        list(compacted.messages),
                        raw_response=initial_raw_response,
                        decode_defect=str(exc),
                    ),
                    args.timeout_seconds,
                    effective_max_output_tokens,
                    enable_thinking=not args.disable_thinking,
                )
                generation_calls += 1
                decision = BatchResearchDecisionCodec.decode(raw_response)
            decoded = True
            contract_valid = _objective_contract_valid(decision, list(case.messages))
            analysis_count = sum(
                len(package.analyses) for package in decision.research_packages
            )
            decoded_decision = asdict(decision)
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"

        observation = {
            "case_id": case.case_id,
            "control_id": case.control_id,
            "operation": case.operation,
            "independence_class": case.independence_class,
            "prompt_sha256": case.prompt_sha256,
            "compacted_prompt_sha256": (
                compacted.compacted_sha256 if compacted is not None else None
            ),
            "input_tokens": compacted.input_tokens if compacted is not None else None,
            "transport_success": transport_success,
            "decision_decoded": decoded,
            "objective_contract_valid": contract_valid,
            "analysis_operations_proposed": analysis_count,
            "representation_repair_attempted": representation_repair_attempted,
            "representation_repair_attempt_number": representation_repair_attempt_number,
            "generation_calls": generation_calls,
            "failure": failure,
        }
        observations.append(observation)
        decision_record = {
            **observation,
            "initial_qwen_raw_response": initial_raw_response,
            "qwen_raw_response": raw_response,
            "qwen_decision": decoded_decision,
        }
        decisions.append(decision_record)
        _append_jsonl(observation_path, observation)
        _append_jsonl(decision_path, decision_record)

    report = dict(mechanical_capability_report(observations))
    if args.scientific_sentinel:
        sentinel_ready = (
            len(all_cases) == 5
            and len({case.control_id for case in all_cases}) == 5
            and len(observations) == 5
            and all(
                observation.get("transport_success")
                and observation.get("decision_decoded")
                and observation.get("objective_contract_valid")
                for observation in observations
            )
        )
        report["mechanical_status"] = (
            "READY_FOR_INDEPENDENT_SCIENTIFIC_REVIEW"
            if sentinel_ready
            else "QWEN_SCIENTIFIC_SENTINEL_NOT_READY"
        )
    report.update(
        {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "qwen_model": model,
            "controls": sorted({case.control_id for case in all_cases}),
            "cases_carried_from_prior_output": len(carried_observations),
            "cases_executed_this_run": len(cases),
            "scientific_sentinel": args.scientific_sentinel,
            "thinking_enabled": not args.disable_thinking,
            "maximum_output_tokens": effective_max_output_tokens,
            "maximum_representation_repairs_per_case": (
                MAX_QWEN_REPRESENTATION_REPAIRS
            ),
            "selected_case_ids": [case.case_id for case in all_cases],
        }
    )
    (output_dir / "qwen_current_capability_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    print(f"QWEN_MODEL={model}")
    print(f"QWEN_CASES={len(all_cases)}")
    print(f"QWEN_CASES_CARRIED={len(carried_observations)}")
    print(f"QWEN_CASES_EXECUTED={len(cases)}")
    print(f"QWEN_THINKING_ENABLED={not args.disable_thinking}")
    print(f"QWEN_MAX_OUTPUT_TOKENS={effective_max_output_tokens}")
    print(f"MECHANICAL_STATUS={report['mechanical_status']}")
    print("SCIENTIFIC_GRADE=AWAITING_INDEPENDENT_REVIEW")
    print("END_TO_END_QWEN_AUTONOMY_TESTED=False")
    print("SOL_FALLBACK_USED=False")
    print(f"OUTPUT_DIR={output_dir}")
    return 0 if report["mechanical_status"] == "READY_FOR_INDEPENDENT_SCIENTIFIC_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())

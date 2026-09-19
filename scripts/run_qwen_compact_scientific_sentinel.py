from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import urllib.request

from MTS_V4.qwen_compact_batch_intent import (
    QwenCompactIntentError,
    compact_intent_json_schema,
    compact_intent_messages,
    compile_compact_batch_intent,
    decision_json,
    decode_compact_batch_intent,
)
from MTS_V4.qwen_current_capability import (
    blinded_cases_from_state_dirs,
    discover_control_state_dirs,
)
from MTS_V4.qwen_prompt_compaction import compact_qwen_messages
from scripts.run_qwen_shadow_replay import _objective_contract_valid


def _model(base_url: str, configured: str | None) -> str:
    if configured and configured.strip():
        return configured.strip()
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/v1/models", timeout=30) as response:
        document = json.loads(response.read().decode("utf-8"))
    data = document.get("data", [])
    if not data or not isinstance(data[0].get("id"), str):
        raise RuntimeError("Qwen /v1/models did not expose a model id")
    return data[0]["id"]


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
    if isinstance(count, int):
        return count
    tokens = document.get("tokens")
    if not isinstance(tokens, list):
        raise RuntimeError("Qwen /tokenize response contains neither count nor tokens")
    return len(tokens)


def _chat(
    *,
    base_url: str,
    model: str,
    messages,
    timeout: int,
    max_output_tokens: int,
) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": max_output_tokens,
            "chat_template_kwargs": {"enable_thinking": True},
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "mts_v4_qwen_compact_batch_intent",
                    "strict": True,
                    "schema": compact_intent_json_schema(),
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
        raise RuntimeError("Qwen returned no compact scientific intent")
    return content


def _action_reconciliation_schema():
    return {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["EXECUTE", "WAIT", "CLOSE"]},
            "continuation_summary": {"type": ["string", "null"]},
            "close_reason": {"type": ["string", "null"]},
            "estimated_remaining_batches": {"type": "integer", "minimum": 0},
            "estimated_remaining_model_calls": {"type": "integer", "minimum": 0},
            "decision_rationale": {"type": "string", "minLength": 1},
        },
        "required": [
            "action",
            "continuation_summary",
            "close_reason",
            "estimated_remaining_batches",
            "estimated_remaining_model_calls",
            "decision_rationale",
        ],
        "additionalProperties": False,
    }


def _action_shape_defect(exc: Exception) -> bool:
    message = str(exc)
    return isinstance(exc, QwenCompactIntentError) and any(
        marker in message
        for marker in (
            "EXECUTE requires",
            "WAIT requires",
            "CLOSE requires",
            "continuing intent requires",
        )
    )


def _chat_action_reconciliation(
    *,
    base_url: str,
    model: str,
    messages,
    raw_response: str,
    defect: str,
    timeout: int,
    max_output_tokens: int,
) -> str:
    reconciliation_messages = list(messages) + [
        {"role": "assistant", "content": raw_response},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "operation": "RECONCILE_QWEN_COMPACT_ACTION",
                    "objective_defect": defect,
                    "instruction": (
                        "Exercise scientific judgment and reconcile only the terminal action state "
                        "of your preceding compact intent. Choose EXECUTE to retain and run its "
                        "research_lines, WAIT to perform no analyses now while continuing later, or "
                        "CLOSE to discard its research_lines and end inquiry. Supply the required "
                        "continuation summary or close reason and internally consistent remaining-work "
                        "estimates. Deterministic code will apply exactly your choice; it will not "
                        "choose an action or invent scientific content."
                    ),
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        },
    ]
    body = json.dumps(
        {
            "model": model,
            "messages": reconciliation_messages,
            "temperature": 0.0,
            "max_tokens": min(max_output_tokens, 4_000),
            "chat_template_kwargs": {"enable_thinking": True},
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "mts_v4_qwen_compact_action_reconciliation",
                    "strict": True,
                    "schema": _action_reconciliation_schema(),
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
        raise RuntimeError("Qwen returned no compact action reconciliation")
    return content


def _apply_action_reconciliation(raw_response: str, reconciliation: str) -> str:
    try:
        intent = json.loads(raw_response)
        choice = json.loads(reconciliation)
    except json.JSONDecodeError as exc:
        raise QwenCompactIntentError(
            f"action reconciliation is not valid JSON: {exc}"
        ) from exc
    if not isinstance(intent, dict) or not isinstance(choice, dict):
        raise QwenCompactIntentError("action reconciliation requires JSON objects")

    action = str(choice.get("action", "")).strip().upper()
    continuation = choice.get("continuation_summary")
    close_reason = choice.get("close_reason")
    remaining_batches = choice.get("estimated_remaining_batches")
    remaining_calls = choice.get("estimated_remaining_model_calls")
    if action == "EXECUTE":
        if not intent.get("research_lines"):
            raise QwenCompactIntentError(
                "Qwen reconciled to EXECUTE without authored research lines"
            )
        if not isinstance(continuation, str) or not continuation.strip():
            raise QwenCompactIntentError(
                "Qwen reconciled to EXECUTE without a continuation summary"
            )
        if not isinstance(remaining_batches, int) or remaining_batches < 1:
            raise QwenCompactIntentError(
                "Qwen reconciled to EXECUTE without a remaining batch"
            )
        if not isinstance(remaining_calls, int) or remaining_calls < 1:
            raise QwenCompactIntentError(
                "Qwen reconciled to EXECUTE without a remaining model call"
            )
        intent["continuation_summary"] = continuation.strip()
        intent["close_reason"] = None
    elif action == "WAIT":
        if not isinstance(continuation, str) or not continuation.strip():
            raise QwenCompactIntentError(
                "Qwen reconciled to WAIT without a continuation summary"
            )
        if not isinstance(remaining_batches, int) or remaining_batches < 1:
            raise QwenCompactIntentError(
                "Qwen reconciled to WAIT without a remaining batch"
            )
        if not isinstance(remaining_calls, int) or remaining_calls < 1:
            raise QwenCompactIntentError(
                "Qwen reconciled to WAIT without a remaining model call"
            )
        intent["research_lines"] = []
        intent["continuation_summary"] = continuation.strip()
        intent["close_reason"] = None
    elif action == "CLOSE":
        if not isinstance(close_reason, str) or not close_reason.strip():
            raise QwenCompactIntentError(
                "Qwen reconciled to CLOSE without a close reason"
            )
        if remaining_batches != 0 or remaining_calls != 0:
            raise QwenCompactIntentError(
                "Qwen reconciled to CLOSE with nonzero remaining work"
            )
        intent["research_lines"] = []
        intent["continuation_summary"] = None
        intent["close_reason"] = close_reason.strip()
    else:
        raise QwenCompactIntentError("Qwen reconciliation action is invalid")

    progress = intent.get("progress")
    if not isinstance(progress, dict):
        raise QwenCompactIntentError("compact intent progress must be an object")
    intent["action"] = action
    progress["estimated_remaining_batches"] = remaining_batches
    progress["estimated_remaining_model_calls"] = remaining_calls
    return json.dumps(intent, sort_keys=True, separators=(",", ":"))


def _append_jsonl(path: Path, item) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(item, sort_keys=True, default=str, separators=(",", ":"))
            + "\n"
        )
        handle.flush()
        os.fsync(handle.fileno())


def _scientific_sentinel_cases(cases, selected_control_ids=()):
    last_interpretation = {}
    controls = set()
    for case in cases:
        controls.add(case.control_id)
        if case.operation == "INTERPRET_BATCH_RESULTS":
            last_interpretation[case.control_id] = case
    missing = sorted(controls - set(last_interpretation))
    if missing:
        raise RuntimeError(f"controls lack an interpretation case: {missing}")
    if selected_control_ids:
        requested = set(selected_control_ids)
        unknown = sorted(requested - set(last_interpretation))
        if unknown:
            raise RuntimeError(f"requested controls are unavailable: {unknown}")
        selected = tuple(last_interpretation[key] for key in sorted(requested))
    else:
        selected = tuple(last_interpretation[key] for key in sorted(last_interpretation))
    if not selected_control_ids and len(selected) != 5:
        raise RuntimeError(f"compact scientific sentinel requires five controls, found {len(selected)}")
    return selected


def _repair_messages(messages, *, raw_response: str, defect: str):
    defect_specific_instruction = ""
    if "observed unavailable from executable result transport" in defect:
        defect_specific_instruction = (
            " The rejected dataset has already failed executable transport and is prohibited for "
            "this decision. Remove every research line, analysis, and input that depends on that "
            "dataset. Do not rename it, repoint it to another catalog entry, or claim that another "
            "source exposes it unless context.qwen_state_grounding explicitly lists it as a "
            "confirmed executable current-batch dataset. Reassess the supplied completed evidence "
            "and independently choose either CLOSE, or genuinely different work using only "
            "confirmed executable inputs. The repair instruction does not choose that scientific "
            "action for you."
        )
    elif "already completed in the newest batch" in defect:
        defect_specific_instruction = (
            " The rejected analysis has already completed and its result is supplied. Remove every "
            "attempt to rerun that analysis. Interpret the completed result and independently "
            "choose either CLOSE, or scientifically distinct work with a new question and local "
            "key. The repair instruction does not choose that scientific action for you."
        )
    return list(messages) + [
        {"role": "assistant", "content": raw_response},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "operation": "REPAIR_QWEN_COMPACT_BATCH_INTENT",
                    "objective_defect": defect,
                    "instruction": (
                        "Return one complete corrected compact batched scientific intent. Correct "
                        "the exact defect while preserving or revising your scientific choices as "
                        "you judge warranted. Do not emit MTS IDs or lineage plumbing. Do not split "
                        "the batch. Deterministic code will not invent scientific content."
                        + defect_specific_instruction
                    ),
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        },
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run five blinded control interpretations through the isolated compact batched "
            "Qwen adapter. Makes no Sol calls and grants no Qwen autonomy."
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
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--input-token-budget", type=int, default=48_000)
    parser.add_argument("--max-output-tokens", type=int, default=4_000)
    parser.add_argument("--max-representation-repairs", type=int, default=2)
    parser.add_argument("--control-id", action="append", default=[])
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(argv)
    if not 0 <= args.max_representation_repairs <= 2:
        raise RuntimeError("max representation repairs must be between zero and two")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    model = _model(args.base_url, args.model)
    state_dirs = discover_control_state_dirs(
        campaign_roots=args.campaign_root,
        state_dirs=args.state_dir,
        excluded_control_ids=args.exclude_control_id,
    )
    cases = _scientific_sentinel_cases(
        blinded_cases_from_state_dirs(state_dirs),
        selected_control_ids=args.control_id,
    )

    observation_path = output_dir / "qwen_compact_observations.jsonl"
    review_path = output_dir / "qwen_compact_decisions_for_scientific_review.jsonl"
    prompt_path = output_dir / "qwen_compact_prompts.jsonl"
    observation_path.touch(exist_ok=False)
    review_path.touch(exist_ok=False)
    prompt_path.touch(exist_ok=False)

    observations = []
    for index, case in enumerate(cases, start=1):
        print(
            f"QWEN_COMPACT_SENTINEL_CASE={index}/{len(cases)} CONTROL={case.control_id}",
            flush=True,
        )
        raw_response = None
        compact_intent = None
        compiled_decision = None
        failure = None
        transport_success = False
        intent_decoded = False
        compiled = False
        contract_valid = False
        repairs = 0
        generation_calls = 0
        input_tokens = None
        try:
            compact_messages = compact_intent_messages(case.messages)
            compacted = compact_qwen_messages(
                compact_messages,
                token_counter=lambda messages: _token_count(
                    args.base_url, model, messages, args.timeout_seconds
                ),
                input_token_budget=args.input_token_budget,
            )
            input_tokens = compacted.input_tokens
            _append_jsonl(
                prompt_path,
                {
                    "case_id": case.case_id,
                    "control_id": case.control_id,
                    "source_prompt_sha256": compacted.source_sha256,
                    "compacted_prompt_sha256": compacted.compacted_sha256,
                    "input_tokens": compacted.input_tokens,
                    "messages": compacted.messages,
                    "compaction_manifest": compacted.manifest,
                },
            )
            if args.preflight_only:
                observations.append(
                    {
                        "case_id": case.case_id,
                        "control_id": case.control_id,
                        "input_tokens": input_tokens,
                        "preflight_ready": True,
                    }
                )
                continue

            request_messages = list(compacted.messages)
            raw_response = _chat(
                base_url=args.base_url,
                model=model,
                messages=request_messages,
                timeout=args.timeout_seconds,
                max_output_tokens=args.max_output_tokens,
            )
            generation_calls += 1
            transport_success = True
            while True:
                try:
                    compact_intent = decode_compact_batch_intent(raw_response)
                    intent_decoded = True
                    compiled_decision = compile_compact_batch_intent(
                        compact_intent,
                        messages=case.messages,
                        case_id=case.case_id,
                    )
                    compiled = True
                    contract_valid = _objective_contract_valid(
                        compiled_decision, list(case.messages)
                    )
                    if not contract_valid:
                        raise QwenCompactIntentError(
                            "compiled decision violates active subject/method/evidence contract"
                        )
                    break
                except Exception as exc:
                    if repairs >= args.max_representation_repairs:
                        raise
                    repairs += 1
                    defect = f"{type(exc).__name__}: {exc}"
                    if _action_shape_defect(exc):
                        while True:
                            reconciliation = _chat_action_reconciliation(
                                base_url=args.base_url,
                                model=model,
                                messages=compacted.messages,
                                raw_response=raw_response,
                                defect=defect,
                                timeout=args.timeout_seconds,
                                max_output_tokens=args.max_output_tokens,
                            )
                            generation_calls += 1
                            try:
                                raw_response = _apply_action_reconciliation(
                                    raw_response, reconciliation
                                )
                                break
                            except Exception as reconciliation_exc:
                                if repairs >= args.max_representation_repairs:
                                    raise
                                repairs += 1
                                defect = (
                                    f"{type(reconciliation_exc).__name__}: "
                                    f"{reconciliation_exc}"
                                )
                    else:
                        request_messages = _repair_messages(
                            compacted.messages,
                            raw_response=raw_response,
                            defect=defect,
                        )
                        repair_tokens = _token_count(
                            args.base_url, model, request_messages, args.timeout_seconds
                        )
                        if repair_tokens > args.input_token_budget:
                            raise RuntimeError(
                                "compact intent repair exceeds governed input budget: "
                                f"{repair_tokens} > {args.input_token_budget}"
                            )
                        raw_response = _chat(
                            base_url=args.base_url,
                            model=model,
                            messages=request_messages,
                            timeout=args.timeout_seconds,
                            max_output_tokens=args.max_output_tokens,
                        )
                        generation_calls += 1
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"

        if args.preflight_only:
            failed_preflight = {
                "case_id": case.case_id,
                "control_id": case.control_id,
                "input_tokens": input_tokens,
                "preflight_ready": False,
                "failure": failure,
            }
            observations.append(failed_preflight)
            _append_jsonl(observation_path, failed_preflight)
            continue
        observation = {
            "case_id": case.case_id,
            "control_id": case.control_id,
            "operation": case.operation,
            "input_tokens": input_tokens,
            "transport_success": transport_success,
            "intent_decoded": intent_decoded,
            "decision_compiled": compiled,
            "objective_contract_valid": contract_valid,
            "representation_repairs": repairs,
            "qwen_generation_calls": generation_calls,
            "failure": failure,
        }
        observations.append(observation)
        _append_jsonl(observation_path, observation)
        _append_jsonl(
            review_path,
            {
                **observation,
                "qwen_raw_response": raw_response,
                "qwen_compact_intent": (
                    asdict(compact_intent) if compact_intent is not None else None
                ),
                "compiled_batch_decision": (
                    json.loads(decision_json(compiled_decision))
                    if compiled_decision is not None
                    else None
                ),
            },
        )

    if args.preflight_only:
        ready = len(observations) == len(cases) and all(
            item.get("preflight_ready") for item in observations
        )
        token_counts = [
            int(item["input_tokens"])
            for item in observations
            if item.get("input_tokens") is not None
        ]
        report = {
            "format": "MTS_V4_QWEN_COMPACT_SENTINEL_PREFLIGHT_V1",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "qwen_model": model,
            "cases": len(observations),
            "maximum_input_tokens": max(token_counts) if token_counts else None,
            "model_generation_calls": 0,
            "status": "PASS" if ready else "FAIL",
            "sol_calls": 0,
        }
        (output_dir / "qwen_compact_preflight_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"QWEN_COMPACT_PREFLIGHT_STATUS={report['status']}")
        print(f"QWEN_COMPACT_PREFLIGHT_MAX_INPUT_TOKENS={report['maximum_input_tokens']}")
        print("QWEN_GENERATION_CALLS=0")
        print("SOL_CALLS=0")
        print(f"OUTPUT_DIR={output_dir}")
        return 0 if ready else 2

    ready = len(observations) == len(cases) and all(
        item["transport_success"]
        and item["intent_decoded"]
        and item["decision_compiled"]
        and item["objective_contract_valid"]
        for item in observations
    )
    report = {
        "format": "MTS_V4_QWEN_COMPACT_SCIENTIFIC_SENTINEL_REPORT_V1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "qwen_model": model,
        "cases": len(observations),
        "controls": [item["control_id"] for item in observations],
        "mechanical_status": (
            "READY_FOR_INDEPENDENT_SCIENTIFIC_REVIEW"
            if ready
            else "QWEN_COMPACT_SENTINEL_NOT_READY"
        ),
        "scientific_grade": "AWAITING_INDEPENDENT_REVIEW",
        "qwen_generation_calls": sum(
            int(item["qwen_generation_calls"]) for item in observations
        ),
        "sol_calls": 0,
        "sol_fallback_used": False,
        "qwen_autonomy_authorized": False,
    }
    (output_dir / "qwen_compact_scientific_sentinel_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"QWEN_MODEL={model}")
    print(f"QWEN_COMPACT_CASES={len(cases)}")
    print(f"QWEN_GENERATION_CALLS={report['qwen_generation_calls']}")
    print(f"MECHANICAL_STATUS={report['mechanical_status']}")
    print("SCIENTIFIC_GRADE=AWAITING_INDEPENDENT_REVIEW")
    print("SOL_CALLS=0")
    print("SOL_FALLBACK_USED=False")
    print("QWEN_AUTONOMY_AUTHORIZED=False")
    print(f"OUTPUT_DIR={output_dir}")
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())

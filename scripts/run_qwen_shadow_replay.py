from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import urllib.request

from MTS_V4.batch_rd_codec import BatchResearchDecisionCodec, BatchResearchDecisionDecodeError
from MTS_V4.qwen_shadow_gate import QwenShadowObservation


def _read_jsonl(path: Path):
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            yield line_number, json.loads(line)


def _model(base_url: str, configured: str | None) -> str:
    if configured and configured.strip():
        return configured.strip()
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/v1/models", timeout=30) as response:
        document = json.loads(response.read().decode("utf-8"))
    data = document.get("data", [])
    if not data or not isinstance(data[0].get("id"), str):
        raise RuntimeError("Qwen /v1/models did not expose a model id")
    return data[0]["id"]


def _chat(base_url: str, model: str, messages, timeout: int) -> str:
    body = json.dumps({"model": model, "messages": messages, "temperature": 0.2}, separators=(",", ":")).encode()
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


def _objective_contract_valid(decision, messages) -> bool:
    try:
        user = json.loads(messages[-1]["content"])
        context = user["context"]
        active_subject = context["subject"]["subject_id"]
        methods = {item["method_id"] for item in context.get("available_analysis_methods", []) if isinstance(item, dict) and "method_id" in item}
        evidence_ids = {item["evidence_id"] for item in context.get("evidence", []) if isinstance(item, dict) and "evidence_id" in item}
    except Exception:
        return False
    current_analysis_ids = {analysis.analysis_id for package in decision.research_packages for analysis in package.analyses}
    for package in decision.research_packages:
        for analysis in package.analyses:
            if analysis.subject_id != active_subject or analysis.method_id not in methods:
                return False
            for item in analysis.inputs:
                if item.evidence_id is not None and item.evidence_id not in evidence_ids:
                    return False
                if item.analysis_id is not None and item.analysis_id not in current_analysis_ids:
                    # Prior analysis IDs require the campaign catalog; absence here is
                    # not enough to declare invalid, so defer to later full execution.
                    continue
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Replay preserved Sol governed prompt envelopes through local Qwen in supervised shadow mode. Never grants autonomy.")
    parser.add_argument("--corpus-jsonl", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--base-url", default=os.getenv("MTS_RD_AI_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--model", default=os.getenv("MTS_RD_AI_MODEL"))
    parser.add_argument("--timeout-seconds", type=int, default=int(os.getenv("MTS_RD_AI_TIMEOUT_SECONDS", "180")))
    parser.add_argument("--max-cases", type=int, default=0)
    args = parser.parse_args(argv)

    output = Path(args.output_jsonl)
    if output.exists():
        raise RuntimeError(f"refusing to overwrite shadow observations: {output}")
    model = _model(args.base_url, args.model)
    observations = []
    replayed = 0
    skipped = 0
    for line_number, record in _read_jsonl(Path(args.corpus_jsonl)):
        messages = record.get("replay_messages")
        if not isinstance(messages, list) or not messages:
            skipped += 1
            continue
        if args.max_cases and replayed >= args.max_cases:
            break
        case_id = str(record.get("case_id") or f"line-{line_number}")
        transport_success = False
        decoded = False
        contract_valid = False
        analyses = 0
        try:
            content = _chat(args.base_url, model, messages, args.timeout_seconds)
            transport_success = True
            decision = BatchResearchDecisionCodec.decode(content)
            decoded = True
            analyses = sum(len(package.analyses) for package in decision.research_packages)
            contract_valid = _objective_contract_valid(decision, messages)
        except (BatchResearchDecisionDecodeError, Exception) as exc:
            # Persist the exact failure class/message for review; no Sol appeal is
            # permitted in shadow replay because this run is measuring Qwen itself.
            failure = f"{type(exc).__name__}: {exc}"
        else:
            failure = None
        observations.append(
            QwenShadowObservation(
                case_id=case_id,
                transport_success=transport_success,
                decision_decoded=decoded,
                objective_contract_valid=contract_valid,
                analysis_operations_proposed=analyses,
                reviewer_notes=failure,
            )
        )
        replayed += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        for item in observations:
            handle.write(json.dumps(asdict(item), sort_keys=True, default=str, separators=(",", ":")) + "\n")
    print(f"QWEN_MODEL={model}")
    print(f"REPLAYED_CASES={replayed}")
    print(f"SKIPPED_LEGACY_CASES_WITHOUT_EXACT_CONTEXT={skipped}")
    print(f"OBSERVATIONS={output}")
    print("QWEN_AUTONOMY_AUTHORIZED=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

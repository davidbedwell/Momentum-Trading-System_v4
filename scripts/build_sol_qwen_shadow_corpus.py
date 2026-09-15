from __future__ import annotations

import argparse
import json
from pathlib import Path


PRIMARY_OPERATIONS = {"BEGIN_BATCH_RESEARCH", "INTERPRET_BATCH_RESULTS", "REPAIR_BATCH_PLAN"}


def _read_jsonl(path: Path):
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            yield line_number, json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc


def _parser():
    parser = argparse.ArgumentParser(description="Build a read-only Sol benchmark corpus for supervised Qwen replay/shadow evaluation.")
    parser.add_argument("--campaign-state-dir", action="append", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--require-exact-replay-context", action="store_true")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    output = Path(args.output_jsonl)
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing benchmark corpus: {output}")
    records = []
    replay_ready = 0
    for raw_dir in args.campaign_state_dir:
        state_dir = Path(raw_dir)
        decision_path = state_dir / "batch_decisions.jsonl"
        report_path = state_dir / "batch_reports.jsonl"
        replay_path = state_dir / "sol_replay_envelopes.jsonl"
        if not decision_path.exists():
            raise RuntimeError(f"missing Sol decision trace: {decision_path}")
        reports = {int(item.get("decisions", -1)): item for _, item in _read_jsonl(report_path)} if report_path.exists() else {}
        envelopes = []
        if replay_path.exists():
            envelopes = [item for _, item in _read_jsonl(replay_path) if item.get("operation") in PRIMARY_OPERATIONS]
        decisions = list(_read_jsonl(decision_path))
        if args.require_exact_replay_context and len(envelopes) != len(decisions):
            raise RuntimeError(
                f"exact replay context count mismatch in {state_dir}: decisions={len(decisions)} envelopes={len(envelopes)}"
            )
        for index, (line_number, item) in enumerate(decisions):
            sequence = int(item.get("decision_sequence", line_number))
            decision = item.get("decision", {})
            envelope = envelopes[index] if index < len(envelopes) else None
            messages = envelope.get("messages") if isinstance(envelope, dict) else None
            ready = isinstance(messages, list) and bool(messages)
            replay_ready += int(ready)
            records.append({
                "corpus_format": "MTS_V4_SOL_QWEN_SHADOW_V2",
                "case_id": f"{state_dir.name}:decision:{sequence}",
                "source_state_dir": str(state_dir),
                "decision_sequence": sequence,
                "analyses_executed_at_decision": item.get("analyses_executed"),
                "sol_decision": decision,
                "preceding_or_same_sequence_report": reports.get(sequence),
                "replay_ready": ready,
                "replay_operation": envelope.get("operation") if isinstance(envelope, dict) else None,
                "replay_messages": messages if ready else None,
                "sol_raw_response": envelope.get("sol_response") if isinstance(envelope, dict) else None,
                "usage_policy": "SUPERVISED_REPLAY_SHADOW_ONLY_NOT_AUTONOMOUS_AUTHORITY",
                "expected_use": (
                    "When replay_ready=true, Qwen receives the exact governed messages preserved at the Sol decision boundary. "
                    "Legacy records without exact messages remain useful as historical approach examples but are not exact replay cases."
                ),
            })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, default=str, separators=(",", ":")) + "\n")
    print(f"CORPUS={output}")
    print(f"RECORDS={len(records)}")
    print(f"EXACT_REPLAY_READY_RECORDS={replay_ready}")
    print("QWEN_AUTONOMY_AUTHORIZED=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

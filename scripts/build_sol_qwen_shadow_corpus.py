from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_jsonl(path: Path):
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            yield line_number, json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc


def _parser():
    parser = argparse.ArgumentParser(
        description="Build a read-only Sol historical decision/analysis benchmark corpus for later supervised Qwen replay/shadow evaluation."
    )
    parser.add_argument("--campaign-state-dir", action="append", required=True)
    parser.add_argument("--output-jsonl", required=True)
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    output = Path(args.output_jsonl)
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing benchmark corpus: {output}")
    records = []
    for raw_dir in args.campaign_state_dir:
        state_dir = Path(raw_dir)
        decision_path = state_dir / "batch_decisions.jsonl"
        report_path = state_dir / "batch_reports.jsonl"
        if not decision_path.exists():
            raise RuntimeError(f"missing Sol decision trace: {decision_path}")
        reports = {int(item.get("decisions", -1)): item for _, item in _read_jsonl(report_path)} if report_path.exists() else {}
        for line_number, item in _read_jsonl(decision_path):
            sequence = int(item.get("decision_sequence", line_number))
            decision = item.get("decision", {})
            records.append({
                "corpus_format": "MTS_V4_SOL_QWEN_SHADOW_V1",
                "source_state_dir": str(state_dir),
                "decision_sequence": sequence,
                "analyses_executed_at_decision": item.get("analyses_executed"),
                "sol_decision": decision,
                "preceding_or_same_sequence_report": reports.get(sequence),
                "usage_policy": "SUPERVISED_REPLAY_SHADOW_ONLY_NOT_AUTONOMOUS_AUTHORITY",
                "expected_use": (
                    "Qwen receives the same governed evidence/context available at the historical boundary; "
                    "its proposed research action is compared with Sol's preserved action for contract competence, "
                    "scientific usefulness, unnecessary-analysis rate, and continuation judgment."
                ),
            })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, default=str, separators=(",", ":")) + "\n")
    print(f"CORPUS={output}")
    print(f"RECORDS={len(records)}")
    print("QWEN_AUTONOMY_AUTHORIZED=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

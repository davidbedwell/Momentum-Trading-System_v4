#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _telemetry_summary(path: Path) -> tuple[int, float, dict | None]:
    calls = 0
    spend = 0.0
    exhausted = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        if row.get("event") == "OPENROUTER_RD_CALL_COMPLETE":
            calls += 1
            cost = row.get("actual_call_cost_usd")
            if isinstance(cost, (int, float)):
                spend += float(cost)
        elif row.get("event") == "BATCH_DECISION_REPRESENTATION_REPAIR_EXHAUSTED":
            exhausted = row
    return calls, spend, exhausted


def main() -> int:
    p = argparse.ArgumentParser(description="Fail-close a Gemini equivalence experiment after a proven representation-repair exhaustion.")
    p.add_argument("--experiment-root", required=True)
    p.add_argument("--ticker", required=True)
    args = p.parse_args()

    exp = Path(args.experiment_root).resolve()
    ticker = args.ticker.upper()
    subject = exp / ticker
    final = exp / "EXPERIMENT_TERMINAL_FAILURE.json"
    if final.exists():
        doc = json.loads(final.read_text(encoding="utf-8"))
        print(f"TERMINAL_FAILURE ticker={doc['ticker']} reason={doc['reason']} spend=${doc['gemini_spend_usd']:.6f}")
        return 0

    candidates = [subject / "GEMINI_RD"] + sorted(subject.glob("GEMINI_RD_FAILED_REPRESENTATION*"))
    telemetry = next((p / "openrouter_telemetry.jsonl" for p in candidates if (p / "openrouter_telemetry.jsonl").is_file()), None)
    if telemetry is None:
        raise SystemExit("FAIL_CLOSED: no Gemini telemetry found; refusing to manufacture terminal failure")

    calls, spend, exhausted = _telemetry_summary(telemetry)
    if exhausted is None:
        raise SystemExit("FAIL_CLOSED: representation repair exhaustion is not proven by telemetry")
    if calls < 1:
        raise SystemExit("FAIL_CLOSED: no completed paid Gemini calls found")

    doc = {
        "qualified": False,
        "terminal": True,
        "ticker": ticker,
        "arm": "GEMINI_RD",
        "reason": "BATCH_DECISION_REPRESENTATION_REPAIR_EXHAUSTED",
        "decode_defect": exhausted.get("decode_defect"),
        "repair_attempts": exhausted.get("repair_attempts"),
        "gemini_completed_calls": calls,
        "gemini_spend_usd": spend,
        "source_telemetry": str(telemetry),
        "governance": {
            "paid_rerun_permitted": False,
            "proceed_to_sol_appeal": False,
            "proceed_to_later_tickers": False,
            "scientific_contract_weakened": False,
        },
    }
    final.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"TERMINAL_FAILURE ticker={ticker} reason={doc['reason']} spend=${spend:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

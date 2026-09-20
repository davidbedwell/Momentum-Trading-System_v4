from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "finalize_failed_gemini_equivalence.py"
spec = importlib.util.spec_from_file_location("finalize_failed_gemini_equivalence", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_telemetry_summary_requires_and_accounts_terminal_failure(tmp_path):
    telemetry = tmp_path / "openrouter_telemetry.jsonl"
    rows = [
        {"event": "OPENROUTER_RD_CALL_COMPLETE", "actual_call_cost_usd": 0.31},
        {"event": "BATCH_DECISION_REPRESENTATION_DEFECT", "repair_attempt": 1},
        {"event": "OPENROUTER_RD_CALL_COMPLETE", "actual_call_cost_usd": 0.29},
        {"event": "BATCH_DECISION_REPRESENTATION_REPAIR_EXHAUSTED", "repair_attempts": 2, "decode_defect": "missing continuation state"},
    ]
    telemetry.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
    calls, spend, exhausted = mod._telemetry_summary(telemetry)
    assert calls == 2
    assert spend == pytest.approx(0.60)
    assert exhausted["repair_attempts"] == 2


def test_no_exhaustion_is_not_terminal(tmp_path):
    telemetry = tmp_path / "openrouter_telemetry.jsonl"
    telemetry.write_text(json.dumps({"event": "OPENROUTER_RD_CALL_COMPLETE", "actual_call_cost_usd": 0.2}) + "\n", encoding="utf-8")
    calls, spend, exhausted = mod._telemetry_summary(telemetry)
    assert calls == 1
    assert spend == pytest.approx(0.2)
    assert exhausted is None

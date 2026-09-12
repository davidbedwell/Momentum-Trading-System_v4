
import json
def test_batch_representation_defect_preserves_raw_response(tmp_path, monkeypatch):
    from MTS_V4.sol_batch_provider import SolBatchResearchDirector

    telemetry_path = tmp_path / "sol_transport_telemetry.jsonl"
    monkeypatch.setenv("MTS_SOL_TELEMETRY_PATH", str(telemetry_path))

    raw = '{"continue_research":true} trailing-invalid-content'
    defect = "invalid batch decision JSON: Extra data"

    preserved = SolBatchResearchDirector._preserve_batch_representation_defect(
        operation="INTERPRET_BATCH_RESULTS",
        repair_attempt=0,
        defect=defect,
        content=raw,
    )

    expected = tmp_path / "sol_representation_defects.jsonl"
    assert preserved == str(expected)
    assert expected.exists()

    record = json.loads(expected.read_text().splitlines()[0])
    assert record["operation"] == "INTERPRET_BATCH_RESULTS"
    assert record["repair_attempt"] == 0
    assert record["decode_defect"] == defect
    assert record["raw_assistant_response"] == raw


def test_batch_provider_repairs_exactly_one_extra_terminal_closing_brace(tmp_path):
    import json
    from MTS_V4.sol_batch_provider import SolBatchResearchDirector

    valid = {
        "continue_research": False,
        "research_packages": [],
        "rp_closures": [],
        "promote_findings": [],
        "research_state": {},
        "close_reason": "Research complete.",
        "batch_interpretation": "Complete.",
        "research_progress": {
            "estimated_percent_complete": 100.0,
            "estimated_remaining_batches": 0,
            "estimated_remaining_sol_calls": 0,
            "estimate_confidence": "HIGH",
            "estimate_rationale": "Research is complete.",
        },
    }

    malformed = json.dumps(valid, separators=(",", ":")) + "}"

    rd = object.__new__(SolBatchResearchDirector)
    telemetry = []

    rd._write_telemetry = telemetry.append

    decision = rd._decode_batch_decision_with_terminal_brace_repair(
        content=malformed,
        operation="INTERPRET_BATCH_RESULTS",
        repair_attempt=0,
    )

    assert decision.continue_research is False
    assert decision.close_reason == "Research complete."

    assert telemetry == [
        {
            "event": "BATCH_DECISION_SINGLE_TERMINAL_BRACE_REPAIRED",
            "operation": "INTERPRET_BATCH_RESULTS",
            "repair_attempt": 0,
            "original_decode_defect": (
                "invalid batch decision JSON: Extra data: "
                f"line 1 column {len(malformed)} (char {len(malformed) - 1})"
            ),
            "mechanical_edit": "REMOVE_EXACTLY_ONE_TERMINAL_CLOSING_BRACE",
            "scientific_content_modified": False,
        }
    ]

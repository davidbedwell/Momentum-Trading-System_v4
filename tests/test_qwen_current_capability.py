from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from MTS_V4.batch_rd_codec import BatchResearchDecisionDecodeError
from MTS_V4.qwen_current_capability import (
    BlindedQwenCapabilityCase,
    blinded_cases_from_state_dirs,
    discover_control_state_dirs,
    mechanical_capability_report,
)
from MTS_V4.qwen_prompt_compaction import (
    QwenPromptCompactionError,
    compact_qwen_messages,
)
from scripts.run_qwen_current_capability_test import (
    MAX_QWEN_REPRESENTATION_REPAIRS,
    SCIENTIFIC_SENTINEL_MAX_OUTPUT_TOKENS,
    _decision_json_schema,
    _representation_repair_messages,
    _schema_smoke_messages,
    _select_cases,
)
import scripts.run_qwen_current_capability_test as capability_script


def _state(tmp_path, control_id="medium_term_trend_persistence"):
    state = tmp_path / control_id
    state.mkdir()
    (state / "universe_scientific_context.json").write_text(
        json.dumps({"calibration_control_id": control_id}),
        encoding="utf-8",
    )
    envelope = {
        "operation": "BEGIN_BATCH_RESEARCH",
        "messages": [
            {"role": "system", "content": "governed system"},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "operation": "BEGIN_BATCH_RESEARCH",
                        "context": {
                            "subject": {"subject_id": "universe:test"},
                            "available_analysis_methods": [],
                            "evidence": [],
                        },
                    }
                ),
            },
        ],
        "sol_response": "HIDDEN SOL ANSWER",
    }
    (state / "sol_replay_envelopes.jsonl").write_text(
        json.dumps(envelope) + "\n",
        encoding="utf-8",
    )
    return state


def test_blinded_cases_never_include_sol_response(tmp_path) -> None:
    state = _state(tmp_path)

    cases = blinded_cases_from_state_dirs((state,))
    serialized = json.dumps(cases[0].to_mapping())

    assert len(cases) == 1
    assert cases[0].independence_class == "INDEPENDENT_INITIAL_PLANNING"
    assert "HIDDEN SOL ANSWER" not in serialized
    assert "sol_response" not in serialized


def test_state_discovery_rejects_duplicate_controls_and_supports_exclusion(tmp_path) -> None:
    root = tmp_path / "campaign"
    root.mkdir()
    first = _state(root, "medium_term_trend_persistence")
    replacement_root = tmp_path / "replacement"
    replacement_root.mkdir()
    replacement = _state(replacement_root, "medium_term_trend_persistence")

    with pytest.raises(RuntimeError, match="duplicate"):
        discover_control_state_dirs(campaign_roots=(root,), state_dirs=(replacement,))

    assert discover_control_state_dirs(
        campaign_roots=(root,),
        excluded_control_ids=("medium_term_trend_persistence",),
        state_dirs=(replacement,),
    ) == (replacement,)


def test_mechanical_report_does_not_claim_autonomy_or_scientific_grade() -> None:
    observations = [
        {
            "operation": "BEGIN_BATCH_RESEARCH",
            "transport_success": True,
            "decision_decoded": True,
            "objective_contract_valid": True,
            "analysis_operations_proposed": 12,
        },
        {
            "operation": "INTERPRET_BATCH_RESULTS",
            "transport_success": True,
            "decision_decoded": True,
            "objective_contract_valid": True,
            "analysis_operations_proposed": 0,
        },
    ]

    report = mechanical_capability_report(observations)

    assert report["mechanical_status"] == "READY_FOR_INDEPENDENT_SCIENTIFIC_REVIEW"
    assert report["scientific_grade"] == "AWAITING_INDEPENDENT_REVIEW"
    assert report["end_to_end_qwen_autonomy_tested"] is False
    assert report["sol_fallback_allowed"] is False


def test_prompt_compaction_is_deterministic_audited_and_preserves_scientific_range() -> None:
    rows = [
        {"security_id": f"S{i:04d}", "effect": float(i - 50), "stable": i % 2 == 0}
        for i in range(100)
    ]
    document = {
        "operation": "INTERPRET_BATCH_RESULTS",
        "context": {
            "evidence": [
                {
                    "evidence_id": "evidence:test",
                    "coverage_start": "2024-01-01",
                    "coverage_end": "2026-01-01",
                    "row_count": 100,
                    "content_identity": "sha256:dataset",
                    "cache_key": "/temporary/cache/path",
                    "provenance": {"query": {"security_ids": [f"S{i:04d}" for i in range(100)]}},
                }
            ],
            "batch_execution_report": {
                "records": [
                    {
                        "analysis_id": "analysis:test",
                        "rp_id": "rp:test",
                        "status": "SUCCESS",
                        "analysis_result": {
                            "result_id": "result:test",
                            "method_id": "analysis.test",
                            "outputs": {"rows": rows},
                            "limitations": ["finite test fixture"],
                        },
                    }
                ]
            },
            "prior_subject_scientific_context": {"sol_answer": "must not leak"},
        },
    }
    messages = (
        {"role": "system", "content": "governed"},
        {"role": "user", "content": json.dumps(document)},
    )
    counter = lambda compacted: sum(len(item["content"]) for item in compacted) // 2

    first = compact_qwen_messages(messages, token_counter=counter, input_token_budget=100_000)
    second = compact_qwen_messages(messages, token_counter=counter, input_token_budget=100_000)

    assert first == second
    compacted = json.loads(first.messages[1]["content"])
    evidence = compacted["context"]["evidence"][0]
    aggregate = compacted["context"]["batch_execution_report"]["records"]
    assert evidence["content_identity"] == "sha256:dataset"
    assert evidence["coverage_start"] == "2024-01-01"
    assert evidence["provenance"]["query"]["security_ids"]["subject_count"] == 100
    assert "cache_key" not in evidence
    assert "prior_subject_scientific_context" not in compacted["context"]
    effect = aggregate["scientific_outputs_by_method"]["analysis.test"]["field_summaries"][
        "[].rows[].effect"
    ]
    assert effect["minimum"] == -50.0
    assert effect["maximum"] == 49.0
    assert effect["observed_count"] == 100
    actions = {item["action"] for item in first.manifest}
    assert "OMITTED_OPERATIONAL_ONLY" in actions
    assert "OMITTED_SOL_AUTHORED_CROSS_SUBJECT_CONTEXT_FOR_BLINDING" in actions
    assert "TOKEN_BUDGET_VERIFIED_BY_SERVING_MODEL" in actions


def test_prompt_compaction_fails_closed_over_server_token_budget() -> None:
    messages = ({"role": "user", "content": json.dumps({"context": {}})},)

    with pytest.raises(QwenPromptCompactionError, match="model call refused"):
        compact_qwen_messages(
            messages,
            token_counter=lambda _messages: 48_001,
            input_token_budget=48_000,
        )


def test_prompt_compaction_collapses_large_and_temporal_dynamic_mappings() -> None:
    outputs = {
        "group_sizes": {f"2026-01-{day:02d}": day for day in range(1, 32)},
        "year_stability": {
            str(year): {"mean_association": (year - 2010) / 100.0, "n_dates": year - 2000}
            for year in range(2006, 2027)
        },
    }
    document = {
        "context": {
            "batch_execution_report": {
                "records": [
                    {
                        "analysis_id": "analysis:dynamic",
                        "rp_id": "rp:dynamic",
                        "status": "SUCCESS",
                        "analysis_result": {
                            "result_id": "result:dynamic",
                            "method_id": "analysis.cross_sectional.association",
                            "outputs": outputs,
                        },
                    }
                ]
            }
        }
    }
    messages = ({"role": "user", "content": json.dumps(document)},)

    compacted = compact_qwen_messages(
        messages,
        token_counter=lambda _messages: 100,
        input_token_budget=48_000,
    )
    rendered = compacted.messages[0]["content"]

    assert "{dynamic_value}" in rendered
    assert len(rendered) < len(json.dumps(document)) * 2


def test_schema_constrains_required_nonblank_decision_fields() -> None:
    schema = _decision_json_schema()
    package = schema["properties"]["research_packages"]["items"]
    analysis = package["properties"]["analyses"]["items"]

    assert schema["additionalProperties"] is False
    assert package["properties"]["objective"]["minLength"] == 1
    assert analysis["properties"]["question_id"]["minLength"] == 1
    assert analysis["properties"]["research_phase"]["enum"] == [
        "EXPLORATION",
        "VALIDATION",
    ]
    input_reference = analysis["properties"]["inputs"]["items"]
    assert input_reference["required"] == [
        "role",
        "evidence_id",
        "analysis_id",
        "dataset_name",
    ]
    assert len(input_reference["oneOf"]) == 2
    for branch in input_reference["oneOf"]:
        assert branch["required"] == input_reference["required"]
        assert branch["properties"]["role"]["minLength"] == 1
        assert branch["additionalProperties"] is False
    assert len(schema["oneOf"]) == 3


def _case(case_id: str, control_id: str, operation: str) -> BlindedQwenCapabilityCase:
    return BlindedQwenCapabilityCase(
        case_id=case_id,
        control_id=control_id,
        operation=operation,
        prompt_sha256=f"sha256:{case_id}",
        messages=({"role": "user", "content": case_id},),
        independence_class="INDEPENDENT_INTERPRETATION",
    )


def test_scientific_sentinel_selects_last_interpretation_per_control() -> None:
    cases = (
        _case("a:begin", "a", "BEGIN_BATCH_RESEARCH"),
        _case("a:first", "a", "INTERPRET_BATCH_RESULTS"),
        _case("a:last", "a", "INTERPRET_BATCH_RESULTS"),
        _case("b:begin", "b", "BEGIN_BATCH_RESEARCH"),
        _case("b:last", "b", "INTERPRET_BATCH_RESULTS"),
    )

    selected = _select_cases(cases, case_ids=(), scientific_sentinel=True)

    assert [case.case_id for case in selected] == ["a:last", "b:last"]


def test_explicit_case_selection_preserves_requested_order_and_rejects_missing() -> None:
    cases = (
        _case("a", "control", "BEGIN_BATCH_RESEARCH"),
        _case("b", "control", "INTERPRET_BATCH_RESULTS"),
    )

    selected = _select_cases(cases, case_ids=("b", "a"), scientific_sentinel=False)
    assert [case.case_id for case in selected] == ["b", "a"]

    with pytest.raises(RuntimeError, match="missing"):
        _select_cases(cases, case_ids=("absent",), scientific_sentinel=False)


def test_execute_schema_smoke_names_the_required_semantic_input_role() -> None:
    payload = json.loads(_schema_smoke_messages("EXECUTE")[1]["content"])

    assert payload["available_input_role"] == "dataset"
    assert "role='dataset'" in payload["requirements"]["EXECUTE"]


def test_schema_smoke_gives_qwen_one_audited_representation_repair(tmp_path, monkeypatch) -> None:
    responses = iter(("bad-execute", "fixed-execute", "wait", "close"))
    monkeypatch.setattr(capability_script, "_model", lambda *_args: "qwen-test")
    monkeypatch.setattr(capability_script, "_chat", lambda *_args, **_kwargs: next(responses))

    smoke_input = SimpleNamespace(
        role="dataset",
        evidence_id="evidence:schema-smoke",
        analysis_id=None,
        dataset_name=None,
    )
    execute = SimpleNamespace(
        continue_research=True,
        waiting_for_future_cohorts=False,
        research_packages=(
            SimpleNamespace(analyses=(SimpleNamespace(inputs=(smoke_input,)),)),
        ),
        close_reason=None,
    )
    wait = SimpleNamespace(
        continue_research=True,
        waiting_for_future_cohorts=True,
        research_packages=(),
        close_reason=None,
    )
    close = SimpleNamespace(
        continue_research=False,
        waiting_for_future_cohorts=False,
        research_packages=(),
        close_reason="complete",
    )

    def decode(raw):
        if raw == "bad-execute":
            raise BatchResearchDecisionDecodeError("input.role must be a nonblank string")
        return {"fixed-execute": execute, "wait": wait, "close": close}[raw]

    monkeypatch.setattr(capability_script.BatchResearchDecisionCodec, "decode", decode)
    monkeypatch.setattr(capability_script, "asdict", lambda value: vars(value))

    output_dir = tmp_path / "schema-smoke"
    exit_code = capability_script.main(
        ["--output-dir", str(output_dir), "--schema-smoke-only"]
    )
    report = json.loads(
        (output_dir / "qwen_schema_smoke_report.json").read_text(encoding="utf-8")
    )

    assert exit_code == 0
    assert report["status"] == "PASS"
    assert report["generation_calls"] == 4
    assert report["representation_repairs_attempted"] == 1


def test_representation_repair_preserves_raw_response_and_exact_defect() -> None:
    original = [{"role": "user", "content": "scientific prompt"}]
    messages = _representation_repair_messages(
        original,
        raw_response='{"truncated":',
        decode_defect="invalid batch decision JSON: unterminated string",
    )
    repair = json.loads(messages[-1]["content"])

    assert messages[:-2] == original
    assert messages[-2] == {"role": "assistant", "content": '{"truncated":'}
    assert repair["decode_defect"] == "invalid batch decision JSON: unterminated string"
    assert "will not invent or replace scientific content" in repair["instruction"]
    assert MAX_QWEN_REPRESENTATION_REPAIRS == 2
    assert SCIENTIFIC_SENTINEL_MAX_OUTPUT_TOKENS == 8_000

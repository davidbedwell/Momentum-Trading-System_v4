from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from MTS_V4.qwen_compact_batch_intent import (
    QwenCompactIntentError,
    compact_intent_json_schema,
    compact_intent_messages,
    compile_compact_batch_intent,
    decision_json,
    decode_compact_batch_intent,
)
from scripts.run_qwen_compact_scientific_sentinel import (
    _action_reconciliation_schema,
    _apply_action_reconciliation,
    _repair_messages,
)


EVIDENCE_ID = "evidence:universe:test"
EXISTING_RP_ID = "RP-EXISTING-001"


def _messages():
    return (
        {"role": "system", "content": "governed batch research"},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "operation": "INTERPRET_BATCH_RESULTS",
                    "required_batch_decision_schema": {"legacy": True},
                    "instructions": ["Preserve scientific authority."],
                    "context": {
                        "subject": {"subject_id": "universe:test"},
                        "available_analysis_methods": [
                            {"method_id": "analysis.descriptive.statistics"}
                        ],
                        "evidence": [{"evidence_id": EVIDENCE_ID}],
                        "research_packages": {
                            "research_package_summaries": [
                                {
                                    "rp_id": EXISTING_RP_ID,
                                    "parent_rp_id": None,
                                    "status": "OPEN",
                                }
                            ]
                        },
                    },
                }
            ),
        },
    )


def _progress(*, continuing=True):
    return {
        "estimated_percent_complete": 60.0 if continuing else 100.0,
        "estimated_remaining_batches": 1 if continuing else 0,
        "estimated_remaining_model_calls": 1 if continuing else 0,
        "estimate_confidence": "MODERATE",
        "estimate_rationale": "One compact batched interpretation remains.",
    }


def _execute_intent(*, existing_rp_id=EXISTING_RP_ID, method_id=None):
    return {
        "action": "EXECUTE",
        "batch_interpretation": "The current evidence warrants one batched follow-up.",
        "research_lines": [
            {
                "existing_rp_id": existing_rp_id,
                "parent_existing_rp_id": (
                    EXISTING_RP_ID if existing_rp_id is None else None
                ),
                "objective": "Measure the selected distribution without changing the hypothesis.",
                "decision_boundary": "Close if the distribution contains no stable structure.",
                "analyses": [
                    {
                        "local_key": "distribution",
                        "parent_local_key": None,
                        "question": "What is the distribution of the selected predictor?",
                        "method_id": method_id or "analysis.descriptive.statistics",
                        "inputs": [
                            {
                                "role": "dataset",
                                "source_kind": "EVIDENCE",
                                "source_id": EVIDENCE_ID,
                                "dataset_name": None,
                            }
                        ],
                        "parameters": {"columns": ["predictor"]},
                        "research_phase": "EXPLORATION",
                        "rationale": "The distribution bounds the next scientific decision.",
                    }
                ],
            }
        ],
        "rp_closures": [],
        "findings": [],
        "continuation_summary": "Interpret the distribution in the next batch.",
        "close_reason": None,
        "progress": _progress(),
    }


def _grounded_messages():
    messages = list(copy.deepcopy(_messages()))
    document = json.loads(messages[-1]["content"])
    context = document["context"]
    context["batch_execution_report"] = {
        "records": {
            "record_identities_and_exceptions": [
                {
                    "analysis_id": "analysis:completed-tail-test:v1",
                    "method_id": "analysis.descriptive.statistics",
                    "result_id": "analysis-result:completed",
                    "rp_id": EXISTING_RP_ID,
                    "status": "SUCCESS",
                    "objective_defect": None,
                },
                {
                    "analysis_id": "analysis:failed-compose:v1",
                    "method_id": "analysis.dataset.compose",
                    "result_id": None,
                    "rp_id": EXISTING_RP_ID,
                    "status": "OBJECTIVE_CONTRACT_DEFECT",
                    "objective_defect": (
                        "Analysis result analysis-result:source does not contain the requested "
                        "output_path ('derived_datasets', 'daily_market_structure_panel'): "
                        "KeyError: 'derived_datasets'"
                    ),
                },
            ],
            "scientific_outputs_by_method": {
                "analysis.cross_sectional.rank": {
                    "field_summaries": {
                        "[].derived_dataset_catalog.cross_sectional_ranked_dataset.row_count": {
                            "observed_count": 1
                        }
                    }
                }
            },
        }
    }
    context["nexus_context"] = {
        "campaign_analysis_result_catalog": {
            "entries": [
                {
                    "analysis_id": "analysis:source:v1",
                    "execution_status": "SUCCESS",
                    "reusable_dataset_metadata_refs": {
                        "daily_market_structure_panel": {"row_count": 100},
                        "metadata_only_panel": {"row_count": 100},
                        "cross_sectional_ranked_dataset": {"row_count": 100},
                    },
                }
            ]
        }
    }
    messages[-1] = {"role": "user", "content": json.dumps(document)}
    return tuple(messages)


def _raw_grounded_messages():
    messages = list(copy.deepcopy(_messages()))
    document = json.loads(messages[-1]["content"])
    context = document["context"]
    context["batch_execution_report"] = {
        "records": [
            {
                "analysis_id": "analysis:completed-tail-test:v1",
                "rp_id": EXISTING_RP_ID,
                "status": "SUCCESS",
                "objective_defect": None,
                "analysis_result": {
                    "method_id": "analysis.descriptive.statistics",
                    "result_id": "analysis-result:completed",
                    "outputs": {
                        "derived_dataset_catalog": {
                            "cross_sectional_ranked_dataset": {"row_count": 100}
                        }
                    },
                },
            },
            {
                "analysis_id": "analysis:failed-compose:v1",
                "rp_id": EXISTING_RP_ID,
                "status": "OBJECTIVE_CONTRACT_DEFECT",
                "objective_defect": (
                    "Analysis result analysis-result:source does not contain the requested "
                    "output_path ('derived_datasets', 'daily_market_structure_panel'): "
                    "KeyError: 'derived_datasets'"
                ),
                "compiled_request_audit": {"method_id": "analysis.dataset.compose"},
            },
        ]
    }
    context["nexus_context"] = {
        "campaign_analysis_result_catalog": [
            {
                "analysis_id": "analysis:source:v1",
                "execution_status": "SUCCESS",
                "reusable_dataset_metadata_refs": {
                    "daily_market_structure_panel": {"row_count": 100},
                    "metadata_only_panel": {"row_count": 100},
                    "cross_sectional_ranked_dataset": {"row_count": 100},
                },
            }
        ]
    }
    messages[-1] = {"role": "user", "content": json.dumps(document)}
    return tuple(messages)


def test_compact_batch_intent_compiles_to_existing_authoritative_contract() -> None:
    intent = decode_compact_batch_intent(json.dumps(_execute_intent()))

    decision = compile_compact_batch_intent(
        intent,
        messages=_messages(),
        case_id="control:case:1",
    )
    encoded = json.loads(decision_json(decision))

    assert decision.continue_research is True
    assert decision.research_packages[0].rp_id == EXISTING_RP_ID
    analysis = decision.research_packages[0].analyses[0]
    assert analysis.subject_id == "universe:test"
    assert analysis.method_id == "analysis.descriptive.statistics"
    assert analysis.inputs[0].role == "dataset"
    assert analysis.inputs[0].evidence_id == EVIDENCE_ID
    assert analysis.analysis_id.startswith("qwen-analysis:")
    assert analysis.question_id.startswith("QWEN-Q:")
    assert encoded["research_state"]["scientific_continuation_state"]["source"] == (
        "QWEN_COMPACT_BATCH_INTENT_V1"
    )


def test_existing_research_line_cannot_replace_its_durable_parent() -> None:
    raw = _execute_intent()
    raw["research_lines"][0]["parent_existing_rp_id"] = "RP-QWEN-PROPOSED-PARENT"
    intent = decode_compact_batch_intent(json.dumps(raw))

    decision = compile_compact_batch_intent(
        intent,
        messages=_messages(),
        case_id="control:case:durable-parent",
    )

    package = decision.research_packages[0]
    assert package.rp_id == EXISTING_RP_ID
    assert package.parent_rp_id is None
    assert package.analyses[0].parent_rp_id is None


def test_new_research_line_gets_safe_generated_identity_and_durable_parent() -> None:
    intent = decode_compact_batch_intent(
        json.dumps(_execute_intent(existing_rp_id=None))
    )

    decision = compile_compact_batch_intent(
        intent,
        messages=_messages(),
        case_id="control:case:new-line",
    )

    package = decision.research_packages[0]
    assert package.rp_id.startswith("QWEN-RP:")
    assert package.rp_id != EXISTING_RP_ID
    assert package.parent_rp_id == EXISTING_RP_ID
    assert package.analyses[0].parent_rp_id == EXISTING_RP_ID


def test_compact_compiler_fails_closed_on_unavailable_scientific_choice() -> None:
    intent = decode_compact_batch_intent(
        json.dumps(_execute_intent(method_id="analysis.unavailable"))
    )

    with pytest.raises(QwenCompactIntentError, match="method_id is unavailable"):
        compile_compact_batch_intent(
            intent,
            messages=_messages(),
            case_id="control:case:bad-method",
        )


def test_close_intent_preserves_qwen_authored_interpretation_and_reason() -> None:
    intent = decode_compact_batch_intent(
        json.dumps(
            {
                "action": "CLOSE",
                "batch_interpretation": "The supplied evidence does not support another test.",
                "research_lines": [],
                "rp_closures": [
                    {
                        "existing_rp_id": EXISTING_RP_ID,
                        "close_reason": "Reasonable inquiry is exhausted.",
                        "final_assessment": "No stable effect was established.",
                    }
                ],
                "findings": [],
                "continuation_summary": None,
                "close_reason": "No additional research is scientifically warranted.",
                "progress": _progress(continuing=False),
            }
        )
    )

    decision = compile_compact_batch_intent(
        intent,
        messages=_messages(),
        case_id="control:case:close",
    )

    assert decision.continue_research is False
    assert decision.research_packages == ()
    assert decision.close_reason == "No additional research is scientifically warranted."
    assert decision.rp_closures[0].rp_id == EXISTING_RP_ID


def test_compact_schema_and_prompt_remove_model_authored_plumbing_ids() -> None:
    schema = compact_intent_json_schema()
    keys = set()

    def visit(value):
        if isinstance(value, dict):
            keys.update(map(str, value.keys()))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(schema)
    transformed = compact_intent_messages(_messages())
    user = json.loads(transformed[-1]["content"])

    assert "rp_id" not in keys
    assert "analysis_id" not in keys
    assert "question_id" not in keys
    assert "finding_id" not in keys
    assert user["required_batch_decision_schema"] == schema
    assert "legacy" not in user["required_batch_decision_schema"]
    assert "Do not invent RP" in user["qwen_compact_batch_contract"]["identity_rules"]


def test_existing_sol_provider_has_no_dependency_on_qwen_compact_adapter() -> None:
    repository = Path(__file__).resolve().parents[1]
    sol_provider = (repository / "MTS_V4" / "sol_batch_provider.py").read_text(
        encoding="utf-8"
    )
    qwen_runner = (
        repository / "scripts" / "run_qwen_compact_scientific_sentinel.py"
    ).read_text(encoding="utf-8")

    assert "qwen_compact_batch_intent" not in sol_provider
    assert "MTS_SOL_BASE_URL" not in qwen_runner
    assert "MTS_SOL_API_KEY" not in qwen_runner
    assert "SOL_CALLS=0" in qwen_runner


def test_qwen_authored_execute_reconciliation_preserves_scientific_batch() -> None:
    contradictory = _execute_intent()
    contradictory["continuation_summary"] = None
    original_lines = contradictory["research_lines"]

    repaired = json.loads(
        _apply_action_reconciliation(
            json.dumps(contradictory),
            json.dumps(
                {
                    "action": "EXECUTE",
                    "continuation_summary": "Run the authored batch and interpret it.",
                    "close_reason": None,
                    "estimated_remaining_batches": 1,
                    "estimated_remaining_model_calls": 1,
                    "decision_rationale": "The authored analyses remain scientifically necessary.",
                }
            ),
        )
    )

    assert repaired["action"] == "EXECUTE"
    assert repaired["research_lines"] == original_lines
    assert repaired["continuation_summary"] == "Run the authored batch and interpret it."
    assert repaired["close_reason"] is None
    decode_compact_batch_intent(json.dumps(repaired))


def test_qwen_authored_close_reconciliation_discards_unexecuted_lines() -> None:
    contradictory = _execute_intent()
    contradictory["action"] = "CLOSE"
    contradictory["continuation_summary"] = None
    contradictory["close_reason"] = None
    contradictory["progress"] = _progress(continuing=False)

    repaired = json.loads(
        _apply_action_reconciliation(
            json.dumps(contradictory),
            json.dumps(
                {
                    "action": "CLOSE",
                    "continuation_summary": None,
                    "close_reason": "The evidence has exhausted reasonable inquiry.",
                    "estimated_remaining_batches": 0,
                    "estimated_remaining_model_calls": 0,
                    "decision_rationale": "No additional test is scientifically warranted.",
                }
            ),
        )
    )

    assert repaired["action"] == "CLOSE"
    assert repaired["research_lines"] == []
    assert repaired["continuation_summary"] is None
    assert repaired["close_reason"] == "The evidence has exhausted reasonable inquiry."
    decode_compact_batch_intent(json.dumps(repaired))


def test_reconciliation_schema_cannot_author_research_content() -> None:
    properties = set(_action_reconciliation_schema()["properties"])

    assert "research_lines" not in properties
    assert "findings" not in properties
    assert "method_id" not in properties
    assert "action" in properties


def test_unavailable_dataset_repair_is_explicit_without_choosing_science() -> None:
    repaired = _repair_messages(
        ({"role": "system", "content": "governed"},),
        raw_response=json.dumps(_execute_intent()),
        defect=(
            "QwenCompactIntentError: selected analysis dataset was observed unavailable from "
            "executable result transport: daily_market_structure_panel; catalog advertisement "
            "alone does not authorize another retry"
        ),
    )
    instruction = json.loads(repaired[-1]["content"])["instruction"]

    assert "prohibited for this decision" in instruction
    assert "Remove every research line, analysis, and input" in instruction
    assert "Do not rename it" in instruction
    assert "confirmed executable current-batch dataset" in instruction
    assert "either CLOSE, or genuinely different work" in instruction
    assert "does not choose that scientific action" in instruction


def test_completed_analysis_repair_requires_interpretation_not_reexecution() -> None:
    repaired = _repair_messages(
        ({"role": "system", "content": "governed"},),
        raw_response=json.dumps(_execute_intent()),
        defect=(
            "QwenCompactIntentError: analysis local_key identifies work already completed in "
            "the newest batch: analysis:done"
        ),
    )
    instruction = json.loads(repaired[-1]["content"])["instruction"]

    assert "Remove every attempt to rerun that analysis" in instruction
    assert "Interpret the completed result" in instruction
    assert "does not choose that scientific action" in instruction


def test_compact_prompt_exposes_completed_and_executable_state_separately() -> None:
    transformed = compact_intent_messages(_grounded_messages())
    user = json.loads(transformed[-1]["content"])
    ledger = user["context"]["qwen_state_grounding"]

    assert ledger["completed_newest_batch_analyses"] == [
        {
            "analysis_id": "analysis:completed-tail-test:v1",
            "method_id": "analysis.descriptive.statistics",
            "result_id": "analysis-result:completed",
            "rp_id": EXISTING_RP_ID,
            "status": "COMPLETED_SUCCESS",
        }
    ]
    assert ledger["confirmed_executable_current_batch_datasets"] == [
        "cross_sectional_ranked_dataset"
    ]
    assert "metadata_only_panel" in ledger["metadata_only_catalog_datasets"]
    assert "daily_market_structure_panel" in ledger["metadata_only_catalog_datasets"]
    assert ledger["observed_unavailable_dataset_paths"][0]["dataset_name"] == (
        "daily_market_structure_panel"
    )


def test_compact_prompt_exposes_grounding_from_raw_precompaction_records() -> None:
    transformed = compact_intent_messages(_raw_grounded_messages())
    user = json.loads(transformed[-1]["content"])
    ledger = user["context"]["qwen_state_grounding"]

    assert [
        item["analysis_id"] for item in ledger["completed_newest_batch_analyses"]
    ] == ["analysis:completed-tail-test:v1"]
    assert ledger["completed_newest_batch_analyses"][0]["result_id"] == (
        "analysis-result:completed"
    )
    assert ledger["confirmed_executable_current_batch_datasets"] == [
        "cross_sectional_ranked_dataset"
    ]
    assert "metadata_only_panel" in ledger["metadata_only_catalog_datasets"]
    assert ledger["observed_unavailable_dataset_paths"][0]["dataset_name"] == (
        "daily_market_structure_panel"
    )


def test_compiler_rejects_exact_repetition_of_completed_batch_analysis() -> None:
    repeated = _execute_intent()
    repeated["research_lines"][0]["analyses"][0]["local_key"] = (
        "analysis:completed-tail-test:v1"
    )
    intent = decode_compact_batch_intent(json.dumps(repeated))

    with pytest.raises(QwenCompactIntentError, match="already completed"):
        compile_compact_batch_intent(
            intent,
            messages=_grounded_messages(),
            case_id="control:case:completed-repeat",
        )


def test_compiler_rejects_observed_unavailable_dataset_retry() -> None:
    retried = _execute_intent()
    analysis = retried["research_lines"][0]["analyses"][0]
    analysis["local_key"] = "retry-market-structure-compose"
    analysis["inputs"] = [
        {
            "role": "market_structure",
            "source_kind": "ANALYSIS",
            "source_id": "analysis:source:v1",
            "dataset_name": "daily_market_structure_panel",
        }
    ]
    intent = decode_compact_batch_intent(json.dumps(retried))

    with pytest.raises(QwenCompactIntentError, match="observed unavailable"):
        compile_compact_batch_intent(
            intent,
            messages=_grounded_messages(),
            case_id="control:case:unavailable-retry",
        )


@pytest.mark.parametrize("messages", [_raw_grounded_messages, _grounded_messages])
def test_compiler_guards_apply_before_and_after_prompt_compaction(messages) -> None:
    repeated = _execute_intent()
    repeated["research_lines"][0]["analyses"][0]["local_key"] = (
        "analysis:completed-tail-test:v1"
    )
    with pytest.raises(QwenCompactIntentError, match="already completed"):
        compile_compact_batch_intent(
            decode_compact_batch_intent(json.dumps(repeated)),
            messages=messages(),
            case_id="control:case:shape-completed",
        )

    retried = _execute_intent()
    analysis = retried["research_lines"][0]["analyses"][0]
    analysis["local_key"] = "retry-market-structure-compose"
    analysis["inputs"] = [
        {
            "role": "market_structure",
            "source_kind": "ANALYSIS",
            "source_id": "analysis:source:v1",
            "dataset_name": "daily_market_structure_panel",
        }
    ]
    with pytest.raises(QwenCompactIntentError, match="observed unavailable"):
        compile_compact_batch_intent(
            decode_compact_batch_intent(json.dumps(retried)),
            messages=messages(),
            case_id="control:case:shape-unavailable",
        )

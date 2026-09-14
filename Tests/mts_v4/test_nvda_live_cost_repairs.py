from __future__ import annotations

from MTS_V4.contracts import AnalysisResult
from MTS_V4.discovery_methods import arithmetic_transform
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector


def test_arithmetic_transform_preserves_source_columns_and_mechanical_lineage():
    rows = (
        {
            "date": "2026-01-02",
            "return_close": -0.06,
            "atr_pct_20": 0.04,
            "h5_terminal_return": 0.08,
        },
        {
            "date": "2026-01-05",
            "return_close": 0.03,
            "atr_pct_20": 0.02,
            "h5_terminal_return": -0.01,
        },
    )

    outputs = arithmetic_transform(
        {"daily_panel": rows},
        {
            "left": {"column": "return_close"},
            "right": {"column": "atr_pct_20"},
            "operation": "DIVIDE",
            "output_name": "return_close_over_atrpct20",
        },
    )

    derived = outputs["derived_datasets"]["arithmetic_feature"]
    assert len(derived) == 2
    assert derived[0]["date"] == "2026-01-02"
    assert derived[0]["return_close"] == -0.06
    assert derived[0]["atr_pct_20"] == 0.04
    assert derived[0]["h5_terminal_return"] == 0.08
    assert derived[0]["return_close_over_atrpct20"] == -1.5
    assert derived[0]["index"] == 0
    assert derived[0]["__observation_lineage"] == {
        "input_name": "daily_panel",
        "input_row_start": 0,
        "input_row_end": 0,
        "input_row_anchor": 0,
        "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
    }
    assert "date" in outputs["derived_dataset_catalog"]["arithmetic_feature"]["schema"]
    assert "h5_terminal_return" in outputs["derived_dataset_catalog"]["arithmetic_feature"]["schema"]


def test_rd_transport_withholds_row_alias_when_canonical_copy_only_adds_lineage():
    exposed_events = [
        {"index": index, "value": float(index)}
        for index in range(100)
    ]
    canonical_events = [
        {
            **row,
            "__observation_lineage": {
                "input_name": "intraday_panel",
                "input_row_start": row["index"],
                "input_row_end": row["index"],
                "input_row_anchor": row["index"],
                "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
            },
        }
        for row in exposed_events
    ]
    result = AnalysisResult(
        result_id="result:threshold",
        request_id="request:threshold",
        subject_id="equity:NVDA",
        method_id="analysis.events.threshold",
        evidence_ids=(),
        outputs={
            "column": "forward_return_5m",
            "threshold": -999.0,
            "event_count": len(exposed_events),
            "events": exposed_events,
            "derived_dataset_catalog": {
                "threshold_events": {
                    "row_count": len(canonical_events),
                    "schema": ["index", "value", "__observation_lineage"],
                    "output_path": ["derived_datasets", "threshold_events"],
                    "temporary": True,
                }
            },
            "derived_datasets": {"threshold_events": canonical_events},
            "interpretation_boundary": "EVENT_SELECTION_EXACTLY_AS_RD_PARAMETERIZED",
        },
    )

    payload = OpenAICompatibleResearchDirector._analysis_result_payload(result)
    transported = payload["outputs"]

    assert "derived_datasets" not in transported
    assert "events" not in transported
    assert transported["event_count"] == 100
    assert transported["column"] == "forward_return_5m"
    assert transported["derived_dataset_catalog"]["threshold_events"]["row_count"] == 100
    assert transported["withheld_row_output_aliases"]["aliases"]["events"] == {
        "dataset_name": "threshold_events",
        "output_path": ["derived_datasets", "threshold_events"],
        "row_count": 100,
    }

    # Transport compaction must not mutate campaign-local Analysis results used for chaining.
    assert result.outputs["events"] == exposed_events
    assert result.outputs["derived_datasets"]["threshold_events"] == canonical_events


def test_rd_transport_keeps_nonduplicate_scientific_summary_lists():
    result = AnalysisResult(
        result_id="result:summary",
        request_id="request:summary",
        subject_id="equity:NVDA",
        method_id="analysis.example",
        evidence_ids=(),
        outputs={
            "group_summaries": [{"group": "A", "mean": 1.2}],
            "derived_dataset_catalog": {
                "rows": {
                    "row_count": 1,
                    "schema": ["index", "value", "__observation_lineage"],
                    "output_path": ["derived_datasets", "rows"],
                    "temporary": True,
                }
            },
            "derived_datasets": {
                "rows": [
                    {
                        "index": 0,
                        "value": 1.2,
                        "__observation_lineage": {"input_row_anchor": 0},
                    }
                ]
            },
        },
    )

    payload = OpenAICompatibleResearchDirector._analysis_result_payload(result)
    assert payload["outputs"]["group_summaries"] == [{"group": "A", "mean": 1.2}]

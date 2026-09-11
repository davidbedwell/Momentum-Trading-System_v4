from __future__ import annotations

from MTS_V4.checkpoint import _forbidden_checkpoint_paths


def test_checkpoint_guard_allows_scalar_rows_aggregate_counts():
    document = {
        "decision": {
            "promote_findings": [
                {
                    "finding_id": "F-NVDA-1",
                    "metadata": {
                        "severe_group": {"rows": 71, "positive_finish_fraction": 0.690141},
                        "nonsevere_group": {"rows": 420, "positive_finish_fraction": 0.552381},
                    },
                }
            ]
        }
    }
    assert _forbidden_checkpoint_paths(document) == ()


def test_checkpoint_guard_rejects_structured_raw_rows():
    document = {
        "decision": {
            "analysis_request": {
                "rows": [
                    {"date": "2026-01-02", "close": 100.0},
                    {"date": "2026-01-03", "close": 101.0},
                ]
            }
        }
    }
    assert _forbidden_checkpoint_paths(document) == (
        "checkpoint.decision.analysis_request.rows",
    )


def test_checkpoint_guard_rejects_payload_cache_and_derived_dataset_keys():
    document = {
        "decision": {
            "payload": {"x": 1},
            "nested": {
                "cache_key": "abc",
                "derived_datasets": ["temporary-result"],
            },
        }
    }
    paths = set(_forbidden_checkpoint_paths(document))
    assert "checkpoint.decision.payload" in paths
    assert "checkpoint.decision.nested.cache_key" in paths
    assert "checkpoint.decision.nested.derived_datasets" in paths

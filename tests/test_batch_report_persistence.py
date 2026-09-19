from __future__ import annotations

from MTS_V4.batch_contracts import BatchAnalysisRecord, BatchExecutionReport
from MTS_V4.batch_report_persistence import compact_batch_report
from MTS_V4.contracts import AnalysisResult
from MTS_V4.jsonl_io import append_jsonl, iter_jsonl
from scripts.compact_batched_universe_reports import main as compact_reports


def test_compact_report_preserves_science_but_removes_row_payloads() -> None:
    result = AnalysisResult(
        result_id="analysis-result:test",
        request_id="request:test",
        subject_id="universe:test",
        method_id="analysis.dataset.compose",
        evidence_ids=(),
        outputs={
            "aligned_row_count": 2,
            "derived_dataset_catalog": {
                "composed_dataset": {
                    "row_count": 2,
                    "output_path": ["derived_datasets", "composed_dataset"],
                }
            },
            "derived_datasets": {"composed_dataset": [{"x": 1}, {"x": 2}]},
        },
    )
    report = BatchExecutionReport(
        records=(
            BatchAnalysisRecord(
                analysis_id="analysis:test",
                rp_id="RP-TEST",
                status="SUCCESS",
                result=result,
            ),
        )
    )

    compact = compact_batch_report(report)
    outputs = compact["records"][0]["result"]["outputs"]

    assert outputs["aligned_row_count"] == 2
    assert outputs["derived_dataset_catalog"]["composed_dataset"]["row_count"] == 2
    assert "derived_datasets" not in outputs
    assert outputs["durable_row_payload"].startswith("WITHHELD")


def test_jsonl_round_trips_transparently_through_gzip(tmp_path) -> None:
    path = tmp_path / "batch_reports.jsonl.gz"
    append_jsonl(path, {"sequence": 1, "value": "preserved"})
    append_jsonl(path, {"sequence": 2, "value": "preserved"})

    assert list(iter_jsonl(path)) == [
        {"sequence": 1, "value": "preserved"},
        {"sequence": 2, "value": "preserved"},
    ]


def test_existing_raw_report_is_verified_compressed_and_summarized(tmp_path) -> None:
    state_dir = tmp_path / "campaign"
    state_dir.mkdir()
    raw_path = state_dir / "batch_reports.jsonl"
    append_jsonl(
        raw_path,
        {
            "decisions": 1,
            "analyses_executed": 0,
            "report": {"records": []},
        },
    )

    assert compact_reports(["--state-dir", str(state_dir)]) == 0

    compressed = state_dir / "batch_reports.jsonl.gz"
    summary = state_dir / "batch_report_summaries.jsonl"
    assert compressed.is_file()
    assert summary.is_file()
    assert not raw_path.exists()
    assert list(iter_jsonl(compressed))[0]["report"] == {"records": []}
    assert list(iter_jsonl(summary))[0]["assessment_summary_only"] is True

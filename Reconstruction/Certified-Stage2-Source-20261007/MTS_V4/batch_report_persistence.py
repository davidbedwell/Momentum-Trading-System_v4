from __future__ import annotations

from dataclasses import asdict
from typing import Mapping

from .batch_contracts import BatchExecutionReport


def compact_batch_report(report: BatchExecutionReport) -> Mapping[str, object]:
    """Preserve scientific outputs while excluding campaign-local row payloads.

    The full report remains the recovery authority in compressed storage.  This
    representation exists for assessment, inspection, and Qwen shadow-corpus
    assembly; it must never be used to reconstruct executable Analysis state.
    """
    raw = asdict(report)
    for record in raw.get("records", []):
        if not isinstance(record, dict):
            continue
        result = record.get("result")
        if not isinstance(result, dict):
            continue
        outputs = result.get("outputs")
        if not isinstance(outputs, dict):
            continue
        derived = outputs.pop("derived_datasets", None)
        if isinstance(derived, Mapping) and not isinstance(
            outputs.get("derived_dataset_catalog"), Mapping
        ):
            outputs["derived_dataset_catalog"] = {
                str(name): {
                    "row_count": len(rows) if isinstance(rows, (list, tuple)) else None,
                    "output_path": ["derived_datasets", str(name)],
                    "temporary": True,
                }
                for name, rows in derived.items()
            }
        if derived is not None:
            outputs["durable_row_payload"] = (
                "WITHHELD_FROM_ASSESSMENT_SUMMARY; retained in compressed recovery report"
            )
    return raw

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from MTS_V4.batch_campaign_reconstruction import decode_batch_execution_report
from MTS_V4.batch_report_persistence import compact_batch_report
from MTS_V4.jsonl_io import append_jsonl, iter_jsonl


def _sha256_uncompressed(path: Path, *, compressed: bool = False) -> str:
    digest = hashlib.sha256()
    opener = gzip.open if compressed or path.suffix == ".gz" else path.open
    with opener(path, "rb") if compressed or path.suffix == ".gz" else opener("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compress durable universe batch reports and create a row-free assessment summary."
    )
    parser.add_argument("--state-dir", required=True)
    args = parser.parse_args(argv)

    state_dir = Path(args.state_dir).expanduser().resolve()
    raw_path = state_dir / "batch_reports.jsonl"
    compressed_path = state_dir / "batch_reports.jsonl.gz"
    summary_path = state_dir / "batch_report_summaries.jsonl"
    source = compressed_path if compressed_path.is_file() else raw_path
    if not source.is_file():
        raise RuntimeError("state directory contains no batch report")
    if summary_path.exists():
        raise RuntimeError(f"refusing to overwrite existing assessment summary: {summary_path}")

    print("COMPACTION_PHASE=BUILD_ASSESSMENT_SUMMARY", flush=True)
    rows = 0
    for item in iter_jsonl(source):
        report_raw = item.get("report")
        if not isinstance(report_raw, dict):
            raise RuntimeError("batch report row is missing report object")
        report = decode_batch_execution_report(report_raw)
        append_jsonl(
            summary_path,
            {
                **{key: value for key, value in item.items() if key != "report"},
                "report": compact_batch_report(report),
                "assessment_summary_only": True,
            },
        )
        rows += 1

    if source == raw_path:
        print("COMPACTION_PHASE=COMPRESS_RECOVERY_REPORT", flush=True)
        temporary = compressed_path.with_suffix(compressed_path.suffix + ".tmp")
        processed = 0
        next_progress = 64 * 1024 * 1024
        with raw_path.open("rb") as incoming, gzip.open(temporary, "wb") as outgoing:
            for chunk in iter(lambda: incoming.read(1024 * 1024), b""):
                outgoing.write(chunk)
                processed += len(chunk)
                if processed >= next_progress:
                    print(f"COMPRESSION_PROGRESS_BYTES={processed}", flush=True)
                    next_progress += 64 * 1024 * 1024
        print("COMPACTION_PHASE=VERIFY_COMPRESSED_RECOVERY_REPORT", flush=True)
        if _sha256_uncompressed(raw_path) != _sha256_uncompressed(
            temporary,
            compressed=True,
        ):
            temporary.unlink(missing_ok=True)
            raise RuntimeError("compressed report verification failed; original preserved")
        temporary.replace(compressed_path)
        raw_path.unlink()

    print(f"STATE_DIR={state_dir}")
    print(f"REPORT_ROWS={rows}")
    print(f"COMPRESSED_RECOVERY_REPORT={compressed_path}")
    print(f"ASSESSMENT_SUMMARY={summary_path}")
    print(f"COMPRESSED_BYTES={compressed_path.stat().st_size}")
    print(f"SUMMARY_BYTES={summary_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

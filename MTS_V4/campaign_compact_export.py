from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path


COMPACT_EXPORT_FORMAT = "MTS_V4_COMPACT_CAMPAIGN_EXPORT_V1"
ROOT_FILES = {
    "research_nexus.json",
    "batch_decisions.jsonl",
    "batch_reports.jsonl",
    "universe_scientific_context.json",
    "run_summary.json",
    "scientific_exposure_ledger.json",
    "sol_spend_authorization_required.json",
}


class CampaignCompactExportError(RuntimeError):
    pass


def _eligible_files(state_dir: Path) -> tuple[Path, ...]:
    selected = [state_dir / name for name in sorted(ROOT_FILES) if (state_dir / name).is_file()]
    package_root = state_dir / "research_packages"
    if package_root.is_dir():
        selected.extend(sorted(path for path in package_root.rglob("*.json") if path.is_file()))
    for path in selected:
        if path.is_symlink():
            raise CampaignCompactExportError(f"compact export refuses symlink: {path}")
        if path.suffix == ".parquet":
            raise CampaignCompactExportError("derived market Parquet is forbidden in compact export")
    return tuple(selected)


def create_compact_campaign_export(*, state_dir: str | Path, output_path: str | Path) -> dict[str, object]:
    """Export compact science/analytics records without market rows or caches."""

    source = Path(state_dir).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    if not source.is_dir():
        raise CampaignCompactExportError(f"campaign state directory not found: {source}")
    if source == output or source in output.parents:
        raise CampaignCompactExportError("output archive must be outside the campaign state directory")
    files = _eligible_files(source)
    if not files:
        raise CampaignCompactExportError("campaign contains no compact durable records")
    records = []
    for path in files:
        payload = path.read_bytes()
        records.append({
            "path": path.relative_to(source).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    manifest = {
        "format": COMPACT_EXPORT_FORMAT,
        "source_state_dir_name": source.name,
        "contents": records,
        "exclusions": [
            "derived-market-store parquet and manifests",
            "raw/reacquirable market data",
            "campaign analysis cache datasets",
            "AI transport telemetry and replay envelopes",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        for path in files:
            archive.add(path, arcname=path.relative_to(source).as_posix(), recursive=False)
        encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        info = tarfile.TarInfo("compact_export_manifest.json")
        info.size = len(encoded)
        info.mode = 0o644
        archive.addfile(info, fileobj=io.BytesIO(encoded))
    return manifest

from __future__ import annotations

import json
from pathlib import Path

from .models import IntakeArtifact


def stage_for_publication(artifact: IntakeArtifact, directory: str | Path) -> Path:
    """Create a transient publication package.

    This is staging only, never canonical durable storage. The caller must keep
    it until verified Nexus publication and may then delete it.
    """
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)

    data_path = root / "canonical_market_history.parquet"
    manifest_path = root / "manifest.json"
    provenance_path = root / "provenance.json"
    quality_path = root / "quality_report.json"
    audit_path = root / "computation_audit.parquet"

    try:
        artifact.observations.to_parquet(data_path, index=False, compression="zstd")
        artifact.execution_audit.to_parquet(audit_path, index=False, compression="zstd")
    except ImportError as exc:
        raise RuntimeError(
            "Parquet support is required for Intake publication staging. "
            "Install the repository-governed parquet dependency."
        ) from exc

    manifest_path.write_text(
        json.dumps(artifact.manifest, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    provenance_path.write_text(
        json.dumps(artifact.provenance, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    quality_path.write_text(
        json.dumps(artifact.quality_report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return root

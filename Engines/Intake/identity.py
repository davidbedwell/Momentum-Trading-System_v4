from __future__ import annotations

import hashlib
import json

import pandas as pd


def dataframe_sha256(df: pd.DataFrame) -> str:
    """Stable content hash of canonical observations."""
    canonical = df.copy()
    if "date" in canonical.columns:
        canonical["date"] = canonical["date"].map(
            lambda x: x.isoformat() if hasattr(x, "isoformat") else str(x)
        )
    payload = canonical.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def semantic_version_fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

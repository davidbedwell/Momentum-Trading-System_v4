from __future__ import annotations

from uuid import uuid4


_ARTIFACT_PREFIX = "artifact:"


def new_artifact_id() -> str:
    """Return a new opaque, location-independent MTS artifact identity.

    UUID4 is intentionally used instead of a Python-version-specific UUID7 API
    so the identity contract remains compatible with the project's declared
    Python >=3.11 baseline.
    """
    return f"{_ARTIFACT_PREFIX}{uuid4()}"

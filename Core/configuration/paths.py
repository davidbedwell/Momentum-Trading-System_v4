from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_PROJECT_NAME = "momentum-trading-system-v4"
_MARKER_FILE = "pyproject.toml"


class RepositoryRootNotFoundError(RuntimeError):
    """Raised when the MTS v4 repository root cannot be identified."""


def _is_mts_v4_root(path: Path) -> bool:
    marker = path / _MARKER_FILE
    if not marker.is_file():
        return False

    try:
        text = marker.read_text(encoding="utf-8")
    except OSError:
        return False

    return f'name = "{_PROJECT_NAME}"' in text or f"name = '{_PROJECT_NAME}'" in text


@lru_cache(maxsize=1)
def repository_root() -> Path:
    """Return the canonical MTS v4 repository root.

    Discovery is semantic: walk upward from this module and identify the
    repository by its pyproject project name. No caller-visible behavior
    depends on a fixed parent depth or current working directory.
    """
    start = Path(__file__).resolve().parent

    for candidate in (start, *start.parents):
        if _is_mts_v4_root(candidate):
            return candidate

    raise RepositoryRootNotFoundError(
        f"Unable to identify {_PROJECT_NAME!r} repository root from {start}"
    )


def governance_root() -> Path:
    return repository_root() / "Governance"


def schemas_root() -> Path:
    return governance_root() / "Schemas"


def contracts_root() -> Path:
    return governance_root() / "Contracts"

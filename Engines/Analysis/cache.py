from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .canonical import canonical_json_bytes


class ResearchCacheError(RuntimeError):
    pass


def _safe_component(value: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in value.strip()
    )
    cleaned = cleaned.strip("._")
    if not cleaned:
        raise ResearchCacheError("Cache component cannot be empty.")
    return cleaned[:160]


@dataclass(frozen=True, slots=True)
class CacheEntry:
    task_id: str
    key: str
    path: Path
    content_hash: str
    size_bytes: int
    persistence_class: str = "CLASS_III"
    authoritative: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "key": self.key,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
            "persistence_class": self.persistence_class,
            "authoritative": self.authoritative,
        }


class ResearchCache:
    """Task-local replaceable working state. Not a second Research Nexus."""

    def __init__(self, root: Path | str, *, task_id: str) -> None:
        self.root = Path(root).expanduser().resolve()
        self.task_id = task_id
        task_digest = hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:16]
        self.task_root = self.root / f"task-{task_digest}"
        self.task_root.mkdir(parents=True, exist_ok=True)

    def put_json(self, key: str, payload: Mapping[str, Any]) -> CacheEntry:
        safe_key = _safe_component(key)
        data = canonical_json_bytes(payload)
        digest = hashlib.sha256(data).hexdigest()
        path = self.task_root / f"{safe_key}-{digest[:16]}.json"
        path.write_bytes(data)
        return CacheEntry(
            task_id=self.task_id,
            key=key,
            path=path,
            content_hash=f"sha256:{digest}",
            size_bytes=len(data),
        )

    def get_json(self, entry: CacheEntry) -> dict[str, Any]:
        self._assert_owned(entry)
        return json.loads(entry.path.read_text(encoding="utf-8"))

    def exists(self, entry: CacheEntry) -> bool:
        self._assert_owned(entry)
        return entry.path.is_file()

    def delete(self, entry: CacheEntry) -> None:
        self._assert_owned(entry)
        entry.path.unlink(missing_ok=True)

    def clear_task(self) -> None:
        if self.task_root.exists():
            shutil.rmtree(self.task_root)

    def _assert_owned(self, entry: CacheEntry) -> None:
        try:
            entry.path.resolve().relative_to(self.task_root.resolve())
        except ValueError as exc:
            raise ResearchCacheError(
                "Cache entry does not belong to this task-local cache."
            ) from exc
        if entry.task_id != self.task_id:
            raise ResearchCacheError(
                "Cache entry task identity does not match this cache."
            )

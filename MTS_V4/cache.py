from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CacheState(str, Enum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


@dataclass(slots=True)
class CacheEntry:
    cache_key: str
    payload: Any
    state: CacheState = CacheState.ACTIVE


class TemporaryResearchCache:
    """Ephemeral campaign storage for reproducible evidence.

    The cache intentionally has no Nexus publication behavior. Promotion into
    durable research memory must occur through explicit RD-authored findings.
    """

    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}

    def put(self, cache_key: str, payload: Any) -> None:
        if not cache_key:
            raise ValueError("cache_key cannot be blank")
        self._entries[cache_key] = CacheEntry(cache_key=cache_key, payload=payload)

    def get(self, cache_key: str) -> Any:
        entry = self._entries[cache_key]
        if entry.state is not CacheState.ACTIVE:
            raise KeyError(cache_key)
        return entry.payload

    def release(self, cache_key: str) -> None:
        entry = self._entries[cache_key]
        entry.payload = None
        entry.state = CacheState.RELEASED

    def purge_released(self) -> int:
        released = [key for key, entry in self._entries.items() if entry.state is CacheState.RELEASED]
        for key in released:
            del self._entries[key]
        return len(released)

    def active_keys(self) -> tuple[str, ...]:
        return tuple(sorted(key for key, entry in self._entries.items() if entry.state is CacheState.ACTIVE))

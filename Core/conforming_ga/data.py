"""Fail-closed partition/PIT data boundary for the clean MTS engine."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, numpy as np

@dataclass(frozen=True)
class Partition:
    name: str
    tickers: tuple[str,...]

class ProtectedDataError(RuntimeError): pass

class PartitionStore:
    def __init__(self, panel: dict[str,np.ndarray], protected: set[str]):
        self._protected=frozenset(protected)
        overlap=set(panel)&self._protected
        if overlap: raise ProtectedDataError(f"protected tickers loaded: {sorted(overlap)}")
        self._panel={k:np.asarray(v).copy() for k,v in panel.items()}
    def materialize(self, part: Partition) -> np.ndarray:
        bad=set(part.tickers)&self._protected
        if bad: raise ProtectedDataError(f"protected partition request: {sorted(bad)}")
        missing=set(part.tickers)-set(self._panel)
        if missing: raise KeyError(sorted(missing))
        return np.column_stack([self._panel[k] for k in part.tickers])
    def provenance_hash(self, part: Partition) -> str:
        a=self.materialize(part)
        h=hashlib.sha256(); h.update(part.name.encode()); h.update("\0".join(part.tickers).encode()); h.update(a.tobytes())
        return h.hexdigest()

def causal_view(a: np.ndarray, t: int) -> np.ndarray:
    """Explicit PIT truncation; no data after t is visible."""
    return np.asarray(a)[:t+1].copy()

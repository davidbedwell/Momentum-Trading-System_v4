from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol

import pandas as pd


@dataclass(frozen=True)
class SourcePayload:
    """Provider-native observations plus source metadata.

    The DataFrame is intentionally provider-facing at this boundary. The
    normalizer is responsible for translating it into canonical MTS OHLCV.
    """

    frame: pd.DataFrame
    source_id: str
    source_format: str
    source_locator: str | None = None
    provider_metadata: Mapping[str, object] = field(default_factory=dict)


class SourceAdapter(Protocol):
    def load(self) -> SourcePayload:
        """Load source observations without interpreting market meaning."""
        ...

from __future__ import annotations

from typing import Mapping

import pandas as pd

from .base import SourcePayload


class DataFrameAdapter:
    """In-memory adapter used by tests and upstream connector integrations."""

    def __init__(
        self,
        frame: pd.DataFrame,
        *,
        source_id: str,
        provider_metadata: Mapping[str, object] | None = None,
    ) -> None:
        self.frame = frame
        self.source_id = source_id
        self.provider_metadata = dict(provider_metadata or {})

    def load(self) -> SourcePayload:
        return SourcePayload(
            frame=self.frame.copy(),
            source_id=self.source_id,
            source_format="DATAFRAME",
            provider_metadata=self.provider_metadata,
        )

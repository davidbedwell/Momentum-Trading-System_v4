from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

from .base import SourcePayload


class CSVAdapter:
    """Generic CSV source adapter.

    Column aliases are supplied by configuration rather than hard-coded to a
    provider. Example: {"timestamp": "date", "vol": "volume"}.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        source_id: str,
        column_aliases: Mapping[str, str] | None = None,
        provider_metadata: Mapping[str, object] | None = None,
        read_csv_kwargs: Mapping[str, object] | None = None,
    ) -> None:
        self.path = Path(path)
        self.source_id = source_id
        self.column_aliases = dict(column_aliases or {})
        self.provider_metadata = dict(provider_metadata or {})
        self.read_csv_kwargs = dict(read_csv_kwargs or {})

    def load(self) -> SourcePayload:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        frame = pd.read_csv(self.path, **self.read_csv_kwargs)
        if self.column_aliases:
            frame = frame.rename(columns=self.column_aliases)
        return SourcePayload(
            frame=frame,
            source_id=self.source_id,
            source_format="CSV",
            source_locator=str(self.path),
            provider_metadata=self.provider_metadata,
        )

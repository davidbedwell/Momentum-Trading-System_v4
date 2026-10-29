from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

from .base import SourcePayload


class ParquetAdapter:
    """Generic Parquet source adapter for provider/native market-history files.

    The adapter loads source observations only. It does not interpret market
    meaning or compute measurements. Extra source columns remain provider
    metadata unless explicitly mapped into canonical fields.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        source_id: str,
        column_aliases: Mapping[str, str] | None = None,
        provider_metadata: Mapping[str, object] | None = None,
    ) -> None:
        self.path = Path(path)
        self.source_id = source_id
        self.column_aliases = dict(column_aliases or {})
        self.provider_metadata = dict(provider_metadata or {})

    def load(self) -> SourcePayload:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        frame = pd.read_parquet(self.path)

        if self.column_aliases:
            frame = frame.rename(columns=self.column_aliases)

        metadata = dict(self.provider_metadata)

        # Capture objective source descriptors without treating them as
        # canonical OHLCV or derived measurements.
        for column in ("ticker", "source", "data_status"):
            if column in frame.columns:
                values = frame[column].dropna().unique().tolist()
                if len(values) == 1:
                    metadata[column] = values[0]
                else:
                    metadata[f"{column}_values"] = values

        metadata["source_columns"] = [str(c) for c in frame.columns]
        metadata["source_row_count"] = int(len(frame))

        return SourcePayload(
            frame=frame,
            source_id=self.source_id,
            source_format="PARQUET",
            source_locator=str(self.path),
            provider_metadata=metadata,
        )

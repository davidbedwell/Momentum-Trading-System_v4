from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd

from .base import SourcePayload


class CSVTypeConversionError(ValueError):
    """Declared CSV numeric typing failed for one or more nonblank values."""


class CSVAdapter:
    """Generic CSV source adapter with explicit type authority.

    Unspecified columns are read as text so identifiers are not silently coerced.
    Only columns explicitly declared in ``numeric_columns`` are converted to
    numeric values. Nonblank conversion failures are reported with row/value
    detail instead of being silently replaced or scientifically interpreted.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        source_id: str,
        column_aliases: Mapping[str, str] | None = None,
        numeric_columns: Sequence[str] = (),
        provider_metadata: Mapping[str, object] | None = None,
        read_csv_kwargs: Mapping[str, object] | None = None,
    ) -> None:
        self.path = Path(path)
        self.source_id = source_id
        self.column_aliases = dict(column_aliases or {})
        self.numeric_columns = tuple(str(column) for column in numeric_columns)
        self.provider_metadata = dict(provider_metadata or {})
        self.read_csv_kwargs = dict(read_csv_kwargs or {})

    def load(self) -> SourcePayload:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        read_kwargs = dict(self.read_csv_kwargs)
        # Explicit caller dtype remains authoritative. Otherwise preserve source
        # tokens as text and convert only declared numeric columns below.
        read_kwargs.setdefault("dtype", str)
        read_kwargs.setdefault("keep_default_na", False)
        frame = pd.read_csv(self.path, **read_kwargs)
        if self.column_aliases:
            frame = frame.rename(columns=self.column_aliases)

        for column in self.numeric_columns:
            if column not in frame.columns:
                raise CSVTypeConversionError(
                    f"declared numeric column is absent after aliases: {column}"
                )
            original = frame[column]
            converted = pd.to_numeric(original, errors="coerce")
            invalid = original.astype(str).str.strip().ne("") & converted.isna()
            if invalid.any():
                examples = [
                    {"row": int(index), "value": str(original.loc[index])}
                    for index in original.index[invalid][:10]
                ]
                raise CSVTypeConversionError(
                    f"numeric conversion failed for column {column!r}: {examples}"
                )
            frame[column] = converted

        return SourcePayload(
            frame=frame,
            source_id=self.source_id,
            source_format="CSV",
            source_locator=str(self.path),
            provider_metadata=self.provider_metadata,
        )

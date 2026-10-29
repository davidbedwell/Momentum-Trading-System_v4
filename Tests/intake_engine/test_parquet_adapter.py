from pathlib import Path

import pandas as pd

from Engines.Intake.adapters import ParquetAdapter


def test_parquet_adapter_loads_source_and_preserves_provider_metadata(tmp_path: Path):
    path = tmp_path / "SMH.parquet"

    pd.DataFrame({
        "ticker": ["SMH", "SMH"],
        "date": pd.to_datetime(["2026-07-30", "2026-07-31"]),
        "open": [529.86, 557.50],
        "high": [544.64, 561.44],
        "low": [524.56, 535.24],
        "close": [538.90, 540.53],
        "volume": [14175000, 14637100],
        "source": ["Yahoo Finance", "Yahoo Finance"],
        "data_status": ["RAW_UNVALIDATED", "RAW_UNVALIDATED"],
    }).to_parquet(path, index=False)

    payload = ParquetAdapter(
        path,
        source_id="raw-yahoo-daily",
    ).load()

    assert payload.source_format == "PARQUET"
    assert payload.provider_metadata["ticker"] == "SMH"
    assert payload.provider_metadata["source"] == "Yahoo Finance"
    assert payload.provider_metadata["data_status"] == "RAW_UNVALIDATED"
    assert payload.provider_metadata["source_row_count"] == 2
    assert "close" in payload.provider_metadata["source_columns"]
    assert list(payload.frame["ticker"].unique()) == ["SMH"]

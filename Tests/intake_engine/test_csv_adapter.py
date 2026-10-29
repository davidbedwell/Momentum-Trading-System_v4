from pathlib import Path

import pytest

from Engines.Intake.adapters import CSVAdapter, CSVTypeConversionError


def test_csv_adapter_supports_configured_aliases_and_preserves_unspecified_text(tmp_path: Path):
    path = tmp_path / "bars.csv"
    path.write_text(
        "timestamp,symbol,o,h,l,c,vol\n2025-01-01,00123,1,2,0.5,1.5,100\n",
        encoding="utf-8",
    )
    adapter = CSVAdapter(
        path,
        source_id="fixture",
        column_aliases={
            "timestamp": "date",
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "vol": "volume",
        },
        numeric_columns=("open", "high", "low", "close", "volume"),
    )
    payload = adapter.load()
    assert list(payload.frame.columns) == [
        "date", "symbol", "open", "high", "low", "close", "volume"
    ]
    assert payload.frame.loc[0, "symbol"] == "00123"
    assert payload.frame.loc[0, "close"] == pytest.approx(1.5)
    assert payload.frame.loc[0, "volume"] == pytest.approx(100)


def test_csv_adapter_reports_declared_numeric_conversion_errors(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("symbol,price\nAAPL,not-a-number\n", encoding="utf-8")
    adapter = CSVAdapter(
        path,
        source_id="fixture",
        numeric_columns=("price",),
    )
    with pytest.raises(CSVTypeConversionError) as exc_info:
        adapter.load()
    message = str(exc_info.value)
    assert "price" in message
    assert "not-a-number" in message
    assert "row" in message

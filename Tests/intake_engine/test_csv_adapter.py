from pathlib import Path

from Engines.Intake.adapters import CSVAdapter


def test_csv_adapter_supports_configured_aliases(tmp_path: Path):
    path = tmp_path / "bars.csv"
    path.write_text(
        "timestamp,o,h,l,c,vol\n2025-01-01,1,2,0.5,1.5,100\n",
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
    )
    payload = adapter.load()
    assert list(payload.frame.columns) == [
        "date", "open", "high", "low", "close", "volume"
    ]

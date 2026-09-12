from MTS_V4.live_sources import YFinanceDailyOhlcvSource


def test_yfinance_daily_ohlcv_defaults_to_twenty_year_history() -> None:
    source = YFinanceDailyOhlcvSource()

    assert source.period == "20y"

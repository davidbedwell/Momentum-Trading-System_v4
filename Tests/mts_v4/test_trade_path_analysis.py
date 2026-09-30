import pytest

from MTS_V4.trade_path_analysis import simulate_long_path, summarize_paths


def _bars():
    return [
        {"date":"d0","open":100,"high":101,"low":99,"close":100},
        {"date":"d1","open":100,"high":106,"low":97,"close":104},
        {"date":"d2","open":104,"high":110,"low":103,"close":108},
        {"date":"d3","open":108,"high":112,"low":107,"close":110},
        {"date":"d4","open":110,"high":111,"low":109,"close":110},
    ]


def test_path_enters_next_open_and_uses_future_bar_extremes():
    p=simulate_long_path(bars=_bars(),signal_index=0,horizon_sessions=3,stop_fractions=(0.05,))
    assert p.entry_date=="d1"
    assert p.entry_price==100
    assert p.exit_date=="d3"
    assert p.exit_price==110
    assert p.fixed_horizon_return==pytest.approx(0.10)
    assert p.mae_return==pytest.approx(-0.03)
    assert p.mfe_return==pytest.approx(0.12)
    assert p.stop_results["0.050000"]["stopped"] is False
    assert p.stop_results["0.050000"]["r_multiple"]==pytest.approx(2.0)


def test_stop_touch_fills_at_stop_and_reports_r():
    p=simulate_long_path(bars=_bars(),signal_index=0,horizon_sessions=3,stop_fractions=(0.02,))
    s=p.stop_results["0.020000"]
    assert s["stopped"] is True
    assert s["fill_date"]=="d1"
    assert s["fill_price"]==pytest.approx(98)
    assert s["r_multiple"]==pytest.approx(-1)


def test_gap_through_stop_fills_at_worse_open():
    bars=[
        {"date":"d0","open":100,"high":101,"low":99,"close":100},
        {"date":"d1","open":100,"high":102,"low":99,"close":101},
        {"date":"d2","open":90,"high":95,"low":89,"close":94},
    ]
    p=simulate_long_path(bars=bars,signal_index=0,horizon_sessions=2,stop_fractions=(0.05,))
    s=p.stop_results["0.050000"]
    assert s["stopped"] is True
    assert s["fill_date"]=="d2"
    assert s["fill_price"]==90
    assert s["r_multiple"]==pytest.approx(-2)


def test_summary_exposes_gross_but_not_fabricated_net_ev():
    p=simulate_long_path(bars=_bars(),signal_index=0,horizon_sessions=3,stop_fractions=(0.05,))
    s=summarize_paths([p])
    stop=s["stop_scenarios"]["0.050000"]
    assert stop["gross_ev_r"]==pytest.approx(2.0)
    assert stop["net_ev_r"].startswith("UNAVAILABLE")

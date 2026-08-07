import pytest

from Engines.Analysis.future_geometry import FutureGeometryError, FuturePriceGeometry


def rows():
    return [
        {"date":"2026-01-01T00:00:00Z","high":101.0,"low":99.0,"close":100.0},
        {"date":"2026-01-02T00:00:00Z","high":106.0,"low":98.0,"close":105.0},
        {"date":"2026-01-03T00:00:00Z","high":108.0,"low":103.0,"close":107.0},
        {"date":"2026-01-04T00:00:00Z","high":107.0,"low":95.0,"close":96.0},
    ]


def test_future_geometry_is_separate_and_retrospective():
    original = tuple(dict(row) for row in rows())
    result = FuturePriceGeometry().calculate(original, horizons=(2,), direction="LONG")

    first = result.outcomes[0]
    assert first["origin_date"] == "2026-01-01T00:00:00Z"
    assert first["terminal_date"] == "2026-01-03T00:00:00Z"
    assert first["forward_return"] == pytest.approx(0.07)
    assert first["maximum_favorable_excursion"] == pytest.approx(0.08)
    assert first["maximum_adverse_excursion"] == pytest.approx(-0.02)
    assert first["time_to_mfe_bars"] == 2
    assert first["time_to_mae_bars"] == 1
    assert first["excursion_order"] == "MAE_BEFORE_MFE"
    assert first["temporal_classification"] == "RETROSPECTIVE_OUTCOME"
    assert tuple(rows()) == original


def test_incomplete_horizon_is_explicit_missing_outcome():
    result = FuturePriceGeometry().calculate(rows(), horizons=(3,), direction="LONG")
    last = result.outcomes[-1]
    assert last["complete_horizon"] is False
    assert last["forward_return"] is None
    assert last["terminal_date"] is None


def test_short_direction_is_explicit():
    result = FuturePriceGeometry().calculate(rows(), horizons=(1,), direction="SHORT")
    first = result.outcomes[0]
    assert first["direction"] == "SHORT"
    assert first["maximum_favorable_excursion"] > 0
    assert first["maximum_adverse_excursion"] < 0


def test_invalid_direction_rejected():
    with pytest.raises(FutureGeometryError):
        FuturePriceGeometry().calculate(rows(), horizons=(1,), direction="SIDEWAYS")


def test_nonpositive_horizon_rejected():
    with pytest.raises(FutureGeometryError):
        FuturePriceGeometry().calculate(rows(), horizons=(0,), direction="LONG")

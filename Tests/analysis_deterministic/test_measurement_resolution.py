from Engines.Analysis.deterministic import DeterministicMeasurementResolver


def base_rows(count=25):
    return [
        {
            "date": f"2026-01-{day:02d}T00:00:00Z",
            "open": float(100 + day),
            "high": float(101 + day),
            "low": float(99 + day),
            "close": float(100 + day),
            "volume": float(1000 + day * 10),
        }
        for day in range(1, count + 1)
    ]


def test_reuses_materialized_measurement_without_recomputation():
    rows = [dict(row, sma_20=123.0) for row in base_rows()]
    result = DeterministicMeasurementResolver().resolve(
        rows,
        required_measurements=("sma_20",),
        input_identity={"artifact_id": "artifact:market", "artifact_version": 1},
    )

    assert result.measurements_reused == ("sma_20",)
    assert result.measurements_computed == ()
    assert result.records == tuple(rows)
    assert result.uses[0].source == "MATERIALIZED_INPUT"


def test_missing_measurement_is_computed_by_shared_library():
    rows = base_rows()
    result = DeterministicMeasurementResolver().resolve(
        rows,
        required_measurements=("sma_20",),
        input_identity={"artifact_id": "artifact:market", "artifact_version": 1},
    )

    assert result.measurements_reused == ()
    assert result.measurements_computed == ("sma_20",)
    assert "sma_20" in result.records[-1]
    assert result.records[-1]["sma_20"] is not None
    assert result.uses[0].source == "SHARED_DETERMINISTIC_LIBRARY"
    assert len(result.uses[0].input_fingerprint) == 64


def test_mixed_reuse_and_compute_paths_work_together():
    rows = [dict(row, sma_20=321.0) for row in base_rows()]
    result = DeterministicMeasurementResolver().resolve(
        rows,
        required_measurements=("sma_20", "sma_50"),
    )

    assert result.measurements_reused == ("sma_20",)
    assert result.measurements_computed == ("sma_50",)
    assert all("sma_20" in row for row in result.records)
    assert all("sma_50" in row for row in result.records)


def test_resolution_is_deterministic_for_same_input():
    rows = base_rows()
    resolver = DeterministicMeasurementResolver()

    first = resolver.resolve(rows, required_measurements=("sma_20",))
    second = resolver.resolve(rows, required_measurements=("sma_20",))

    assert first.records == second.records
    assert first.measurements_computed == second.measurements_computed
    assert first.uses[0].input_fingerprint == second.uses[0].input_fingerprint

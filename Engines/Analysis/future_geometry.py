from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class FutureGeometryError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class FutureGeometryResult:
    direction: str
    horizons: tuple[int, ...]
    origin_count: int
    outcomes: tuple[Mapping[str, Any], ...]
    temporal_classification: str = "RETROSPECTIVE_OUTCOME"

    def to_payload(self) -> dict[str, Any]:
        return {
            "direction": self.direction,
            "horizons": list(self.horizons),
            "origin_count": self.origin_count,
            "temporal_classification": self.temporal_classification,
            "outcomes": [dict(item) for item in self.outcomes],
            "interpretation_boundary":
                "RETROSPECTIVE_GEOMETRY_ONLY_NOT_SIGNAL_OR_DECISION",
        }


def _validate_records(records: Sequence[Mapping[str, Any]]) -> None:
    required = ("date", "high", "low", "close")
    if not records:
        raise FutureGeometryError("At least one historical observation is required.")

    previous_date = None
    for index, row in enumerate(records):
        missing = [name for name in required if row.get(name) is None]
        if missing:
            raise FutureGeometryError(
                f"Record {index} missing required field(s): {missing}"
            )

        close = float(row["close"])
        high = float(row["high"])
        low = float(row["low"])
        if close <= 0 or high <= 0 or low <= 0:
            raise FutureGeometryError("Future geometry requires positive prices.")
        if high < low:
            raise FutureGeometryError(f"Malformed high/low at record {index}.")

        date = str(row["date"])
        if previous_date is not None and date <= previous_date:
            raise FutureGeometryError(
                "Historical observations must be strictly date-ordered."
            )
        previous_date = date


class FuturePriceGeometry:
    """Explicitly retrospective outcome geometry, structurally separate from inputs."""

    def calculate(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        horizons: Sequence[int],
        direction: str = "LONG",
    ) -> FutureGeometryResult:
        _validate_records(records)

        normalized_horizons = tuple(sorted({int(h) for h in horizons}))
        if not normalized_horizons or any(h <= 0 for h in normalized_horizons):
            raise FutureGeometryError("Horizons must contain positive integers.")

        direction = direction.upper().strip()
        if direction not in {"LONG", "SHORT"}:
            raise FutureGeometryError("direction must be LONG or SHORT")

        rows = tuple(dict(row) for row in records)
        outcomes: list[dict[str, Any]] = []

        for origin_index, origin in enumerate(rows):
            origin_close = float(origin["close"])
            origin_date = str(origin["date"])

            for horizon in normalized_horizons:
                terminal_index = origin_index + horizon
                if terminal_index >= len(rows):
                    outcomes.append({
                        "origin_index": origin_index,
                        "origin_date": origin_date,
                        "horizon_bars": horizon,
                        "direction": direction,
                        "temporal_classification": "RETROSPECTIVE_OUTCOME",
                        "complete_horizon": False,
                        "forward_return": None,
                        "maximum_favorable_excursion": None,
                        "maximum_adverse_excursion": None,
                        "time_to_mfe_bars": None,
                        "time_to_mae_bars": None,
                        "excursion_order": None,
                        "terminal_date": None,
                    })
                    continue

                future = rows[origin_index + 1 : terminal_index + 1]
                terminal = rows[terminal_index]

                future_highs = [float(row["high"]) for row in future]
                future_lows = [float(row["low"]) for row in future]
                terminal_close = float(terminal["close"])

                high_value = max(future_highs)
                low_value = min(future_lows)
                time_to_high = future_highs.index(high_value) + 1
                time_to_low = future_lows.index(low_value) + 1

                if direction == "LONG":
                    forward_return = terminal_close / origin_close - 1.0
                    mfe = high_value / origin_close - 1.0
                    mae = low_value / origin_close - 1.0
                    time_to_mfe = time_to_high
                    time_to_mae = time_to_low
                else:
                    forward_return = origin_close / terminal_close - 1.0
                    mfe = origin_close / low_value - 1.0
                    mae = origin_close / high_value - 1.0
                    time_to_mfe = time_to_low
                    time_to_mae = time_to_high

                if time_to_mfe < time_to_mae:
                    order = "MFE_BEFORE_MAE"
                elif time_to_mae < time_to_mfe:
                    order = "MAE_BEFORE_MFE"
                else:
                    order = "SAME_BAR"

                outcomes.append({
                    "origin_index": origin_index,
                    "origin_date": origin_date,
                    "horizon_bars": horizon,
                    "direction": direction,
                    "temporal_classification": "RETROSPECTIVE_OUTCOME",
                    "complete_horizon": True,
                    "forward_return": forward_return,
                    "maximum_favorable_excursion": mfe,
                    "maximum_adverse_excursion": mae,
                    "time_to_mfe_bars": time_to_mfe,
                    "time_to_mae_bars": time_to_mae,
                    "excursion_order": order,
                    "terminal_date": str(terminal["date"]),
                })

        return FutureGeometryResult(
            direction=direction,
            horizons=normalized_horizons,
            origin_count=len(rows),
            outcomes=tuple(outcomes),
        )

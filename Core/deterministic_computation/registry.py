from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable

import pandas as pd

from .families import (
    market_structure,
    momentum,
    price_candle,
    statistics_liquidity,
    trend,
    volatility,
    volume_liquidity,
)

Calculator = Callable[[pd.DataFrame], pd.DataFrame]


@dataclass(frozen=True)
class ComputationFamily:
    family_id: str
    version: str
    calculator: Calculator
    description: str
    provenance: str = "MTS-v1 reference implementation, reviewed for v2"
    status: str = "ACTIVE"


def build_registry() -> OrderedDict[str, ComputationFamily]:
    families = [
        ComputationFamily(
            "PRICE_CANDLE", "0.1.0", price_candle.calculate,
            "Returns and single/adjacent-bar geometry.",
        ),
        ComputationFamily(
            "TREND", "0.1.0", trend.calculate,
            "Moving-average geometry, slopes, and DMI/ADX.",
        ),
        ComputationFamily(
            "MOMENTUM", "0.1.0", momentum.calculate,
            "ROC, RSI, MACD, PPO, stochastic, Williams %R, and CCI.",
        ),
        ComputationFamily(
            "VOLATILITY", "0.1.0", volatility.calculate,
            "True range, ATR, realized volatility, range estimators, and Bollinger geometry.",
        ),
        ComputationFamily(
            "VOLUME_LIQUIDITY", "0.1.0", volume_liquidity.calculate,
            "Volume baselines, relative volume, money flow, VWAP, liquidity, and volume trajectory.",
        ),
        ComputationFamily(
            "MARKET_STRUCTURE", "0.1.0", market_structure.calculate,
            "Rolling highs/lows, range location, distance, and new-high/new-low facts.",
        ),
        ComputationFamily(
            "STATISTICS_LIQUIDITY_REFERENCE", "0.1.0",
            statistics_liquidity.calculate,
            "Explicitly named v1 rolling-return statistics retained as reference computations.",
            status="REFERENCE",
        ),
    ]
    return OrderedDict((family.family_id, family) for family in families)


def registered_families() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "family_id": x.family_id,
                "version": x.version,
                "description": x.description,
                "provenance": x.provenance,
                "status": x.status,
            }
            for x in build_registry().values()
        ]
    )

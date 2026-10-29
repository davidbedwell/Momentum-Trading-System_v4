
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

import pandas as pd


class MaterializationMode(str, Enum):
    ACTIVE_FAMILIES = "ACTIVE_FAMILIES"
    EXPLICIT_MEASUREMENTS = "EXPLICIT_MEASUREMENTS"
    OBSERVATIONS_ONLY = "OBSERVATIONS_ONLY"


@dataclass(frozen=True)
class MaterializationPolicy:
    mode: MaterializationMode = MaterializationMode.ACTIVE_FAMILIES
    version: str = "intake-materialization-v0.1"
    families: tuple[str, ...] = ()
    measurement_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.mode == MaterializationMode.EXPLICIT_MEASUREMENTS and not self.measurement_names:
            raise ValueError("EXPLICIT_MEASUREMENTS requires measurement_names")
        if self.mode == MaterializationMode.OBSERVATIONS_ONLY and (
            self.families or self.measurement_names
        ):
            raise ValueError("OBSERVATIONS_ONLY cannot request computations")


@dataclass(frozen=True)
class IntakeRequest:
    symbol: str
    timeframe: str
    policy: MaterializationPolicy = field(default_factory=MaterializationPolicy)
    requested_by: str = "SYSTEM"
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if not self.timeframe.strip():
            raise ValueError("timeframe is required")


@dataclass(frozen=True)
class IntakeArtifact:
    # Intake semantic identity evidence; Nexus owns canonical artifact reference.
    semantic_fingerprint: str
    schema_id: str
    schema_version: int
    engine_version: str
    symbol: str
    timeframe: str
    observations: pd.DataFrame
    measurement_columns: tuple[str, ...]
    materialization_policy: Mapping[str, object]
    provenance: Mapping[str, object]
    quality_report: Mapping[str, object]
    execution_audit: pd.DataFrame
    manifest: Mapping[str, object]


@dataclass(frozen=True)
class IntakeResult:
    artifact: IntakeArtifact
    nexus_reference: object | None = None

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import csv

from .models import ResearchMode


class AnalysisMethodRegistryError(RuntimeError):
    pass


class AnalysisMethodNotFoundError(AnalysisMethodRegistryError):
    pass


@dataclass(frozen=True, slots=True)
class AnalysisMethodSpec:
    method_id: str
    method_name: str
    method_family: str
    version: str
    status: str
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    required_measurements: tuple[str, ...]
    compatible_artifact_types: tuple[str, ...]
    minimum_sample: int
    temporal_requirements: tuple[str, ...]
    future_information_allowance: str
    research_mode_compatibility: tuple[ResearchMode, ...]
    parameters: tuple[str, ...]
    outputs: tuple[str, ...]
    validation_rules: tuple[str, ...]
    determinism: str
    random_seed_requirement: str
    resource_profile: str
    implementation_reference: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "method_id": self.method_id,
            "method_name": self.method_name,
            "method_family": self.method_family,
            "version": self.version,
            "status": self.status,
            "required_inputs": list(self.required_inputs),
            "optional_inputs": list(self.optional_inputs),
            "required_measurements": list(self.required_measurements),
            "compatible_artifact_types": list(self.compatible_artifact_types),
            "minimum_sample": self.minimum_sample,
            "temporal_requirements": list(self.temporal_requirements),
            "future_information_allowance": self.future_information_allowance,
            "research_mode_compatibility": [mode.value for mode in self.research_mode_compatibility],
            "parameters": list(self.parameters),
            "outputs": list(self.outputs),
            "validation_rules": list(self.validation_rules),
            "determinism": self.determinism,
            "random_seed_requirement": self.random_seed_requirement,
            "resource_profile": self.resource_profile,
            "implementation_reference": self.implementation_reference,
        }


def _split(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split("|") if item.strip())


class AnalysisMethodRegistry:
    REQUIRED_COLUMNS = (
        "method_id",
        "method_name",
        "method_family",
        "version",
        "status",
        "required_inputs",
        "optional_inputs",
        "required_measurements",
        "compatible_artifact_types",
        "minimum_sample",
        "temporal_requirements",
        "future_information_allowance",
        "research_mode_compatibility",
        "parameters",
        "outputs",
        "validation_rules",
        "determinism",
        "random_seed_requirement",
        "resource_profile",
        "implementation_reference",
    )

    def __init__(self, specs: Iterable[AnalysisMethodSpec]) -> None:
        self._specs = {}
        for spec in specs:
            if spec.method_id in self._specs:
                raise AnalysisMethodRegistryError(f"Duplicate method_id: {spec.method_id}")
            self._specs[spec.method_id] = spec

    @classmethod
    def from_csv(cls, path: str | Path) -> "AnalysisMethodRegistry":
        path = Path(path)
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = tuple(reader.fieldnames or ())
            missing = [column for column in cls.REQUIRED_COLUMNS if column not in fieldnames]
            if missing:
                raise AnalysisMethodRegistryError(
                    f"Analysis method registry missing required columns: {missing}"
                )
            specs = [cls._parse_row(row, line_number=index + 2) for index, row in enumerate(reader)]
        return cls(specs)

    @classmethod
    def _parse_row(cls, row: Mapping[str, str], *, line_number: int) -> AnalysisMethodSpec:
        method_id = row["method_id"].strip()
        if not method_id:
            raise AnalysisMethodRegistryError(f"Blank method_id at line {line_number}")
        if method_id.startswith("A09-"):
            raise AnalysisMethodRegistryError(
                f"Legacy A09 runtime identity is prohibited in v2 registry: {method_id}"
            )

        modes = []
        for value in _split(row["research_mode_compatibility"]):
            try:
                modes.append(ResearchMode(value))
            except ValueError as exc:
                raise AnalysisMethodRegistryError(
                    f"Unknown research mode {value!r} at line {line_number}"
                ) from exc

        minimum_sample_text = row["minimum_sample"].strip() or "0"
        try:
            minimum_sample = int(minimum_sample_text)
        except ValueError as exc:
            raise AnalysisMethodRegistryError(
                f"Invalid minimum_sample at line {line_number}: {minimum_sample_text!r}"
            ) from exc
        if minimum_sample < 0:
            raise AnalysisMethodRegistryError("minimum_sample cannot be negative")

        return AnalysisMethodSpec(
            method_id=method_id,
            method_name=row["method_name"].strip(),
            method_family=row["method_family"].strip(),
            version=row["version"].strip(),
            status=row["status"].strip(),
            required_inputs=_split(row["required_inputs"]),
            optional_inputs=_split(row["optional_inputs"]),
            required_measurements=_split(row["required_measurements"]),
            compatible_artifact_types=_split(row["compatible_artifact_types"]),
            minimum_sample=minimum_sample,
            temporal_requirements=_split(row["temporal_requirements"]),
            future_information_allowance=row["future_information_allowance"].strip(),
            research_mode_compatibility=tuple(modes),
            parameters=_split(row["parameters"]),
            outputs=_split(row["outputs"]),
            validation_rules=_split(row["validation_rules"]),
            determinism=row["determinism"].strip(),
            random_seed_requirement=row["random_seed_requirement"].strip(),
            resource_profile=row["resource_profile"].strip(),
            implementation_reference=row["implementation_reference"].strip(),
        )

    def get(self, method_id: str) -> AnalysisMethodSpec:
        try:
            return self._specs[method_id]
        except KeyError as exc:
            raise AnalysisMethodNotFoundError(method_id) from exc

    def all(self) -> tuple[AnalysisMethodSpec, ...]:
        return tuple(self._specs[key] for key in sorted(self._specs))

    def active(self) -> tuple[AnalysisMethodSpec, ...]:
        return tuple(spec for spec in self.all() if spec.status == "ACTIVE")

    def by_family(self, family: str, *, active_only: bool = True) -> tuple[AnalysisMethodSpec, ...]:
        specs = self.active() if active_only else self.all()
        return tuple(spec for spec in specs if spec.method_family == family)

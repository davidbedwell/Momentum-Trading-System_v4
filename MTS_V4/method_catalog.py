from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


class MethodCatalogError(RuntimeError):
    pass


class MethodNotFoundError(MethodCatalogError):
    pass


@dataclass(frozen=True, slots=True)
class ParameterContract:
    name: str
    required: bool = True
    python_types: tuple[type, ...] = ()
    exact_length: int | None = None
    minimum_length: int | None = None
    maximum_length: int | None = None
    allowed_values: tuple[Any, ...] = ()
    meaning: str = ""

    def capability_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "required": self.required,
            "types": [value.__name__ for value in self.python_types],
            "exact_length": self.exact_length,
            "minimum_length": self.minimum_length,
            "maximum_length": self.maximum_length,
            "allowed_values": list(self.allowed_values),
            "meaning": self.meaning,
        }


@dataclass(frozen=True, slots=True)
class MethodSpec:
    method_id: str
    artifact_types: tuple[str, ...]
    description: str = ""
    parameters: tuple[ParameterContract, ...] = ()
    minimum_sample: int = 0
    exploration_allowed: bool = True
    validation_allowed: bool = True
    allows_future_information: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def capability_payload(self) -> dict[str, Any]:
        """Neutral capability description supplied to the AI Research Director."""
        return {
            "method_id": self.method_id,
            "description": self.description,
            "artifact_types": list(self.artifact_types),
            "parameters": [parameter.capability_payload() for parameter in self.parameters],
            "minimum_sample": self.minimum_sample,
            "exploration_allowed": self.exploration_allowed,
            "validation_allowed": self.validation_allowed,
            "allows_future_information": self.allows_future_information,
            "metadata": dict(self.metadata),
        }


class MethodCatalog:
    """Objective method registry.

    It describes what exists and what its execution contract requires. It does
    not score, rank, recommend, infer, or select scientific methods.
    """

    def __init__(self, specs: Iterable[MethodSpec] = ()) -> None:
        self._specs: dict[str, MethodSpec] = {}
        for spec in specs:
            self.register(spec)

    def register(self, spec: MethodSpec) -> None:
        if not spec.method_id.strip():
            raise MethodCatalogError("method_id cannot be blank")
        if spec.method_id in self._specs:
            raise MethodCatalogError(f"duplicate method_id: {spec.method_id}")
        self._specs[spec.method_id] = spec

    def get(self, method_id: str) -> MethodSpec:
        try:
            return self._specs[method_id]
        except KeyError as exc:
            raise MethodNotFoundError(method_id) from exc

    def all(self) -> tuple[MethodSpec, ...]:
        return tuple(self._specs[key] for key in sorted(self._specs))

    def capability_payloads(self) -> tuple[dict[str, Any], ...]:
        return tuple(spec.capability_payload() for spec in self.all())

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

from .errors import SchemaValidationError
from .schema_registry import SchemaRegistry


class SchemaValidator:
    """Validate structured MTS objects against governed schemas."""

    def __init__(self, registry: SchemaRegistry | None = None) -> None:
        self._registry = registry or SchemaRegistry()

    @property
    def registry(self) -> SchemaRegistry:
        return self._registry

    def validate(
        self,
        instance: Any,
        *,
        schema_id: str,
        schema_version: int,
    ) -> None:
        governed = self._registry.get(schema_id, schema_version)

        validator = Draft202012Validator(
            governed.document,
            registry=self._registry.reference_registry,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )

        errors = tuple(
            self._format_error(error)
            for error in sorted(
                validator.iter_errors(instance),
                key=lambda item: tuple(str(part) for part in item.absolute_path),
            )
        )

        if errors:
            raise SchemaValidationError(
                schema_id=governed.schema_id,
                schema_version=governed.schema_version,
                errors=errors,
            )

    @staticmethod
    def _format_error(error: Any) -> str:
        if error.absolute_path:
            path = ".".join(str(part) for part in error.absolute_path)
        else:
            path = "<root>"
        return f"{path}: {error.message}"

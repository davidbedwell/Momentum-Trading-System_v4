from __future__ import annotations


class SchemaError(RuntimeError):
    """Base class for governed schema service failures."""


class SchemaRegistryError(SchemaError):
    """Raised when the governed schema registry cannot be constructed safely."""


class SchemaConflictError(SchemaRegistryError):
    """Raised when one logical schema identity/version maps to conflicting definitions."""


class SchemaNotFoundError(SchemaError):
    """Raised when a requested governed schema identity/version is unavailable."""


class SchemaValidationError(SchemaError):
    """Raised when an instance violates a governed schema."""

    def __init__(
        self,
        schema_id: str,
        schema_version: int,
        errors: tuple[str, ...],
    ) -> None:
        self.schema_id = schema_id
        self.schema_version = schema_version
        self.errors = errors

        detail = "; ".join(errors) if errors else "validation failed"
        super().__init__(
            f"{schema_id}@{schema_version} validation failed: {detail}"
        )

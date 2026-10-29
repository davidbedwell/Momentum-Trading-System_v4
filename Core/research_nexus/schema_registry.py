from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from Core.configuration import schemas_root

from .errors import (
    SchemaConflictError,
    SchemaNotFoundError,
    SchemaRegistryError,
)


@dataclass(frozen=True, slots=True)
class GovernedSchema:
    schema_id: str
    schema_version: int
    status: str
    document: Mapping[str, Any]
    source_path: Path

    @property
    def logical_key(self) -> tuple[str, int]:
        return (self.schema_id, self.schema_version)


class SchemaRegistry:
    """Read-only registry for Git-governed MTS JSON Schemas.

    Public lookup is by governed schema_id + schema_version. File names,
    repository-relative paths, and JSON Schema $id values are implementation
    details used only to load and resolve the published schema documents.
    """

    def __init__(self, root: Path | None = None) -> None:
        self._root = (root or schemas_root()).resolve()
        self._schemas: dict[tuple[str, int], GovernedSchema] = {}
        self._reference_registry = Registry()
        self._load()

    @property
    def root(self) -> Path:
        return self._root

    def identities(self) -> tuple[tuple[str, int], ...]:
        return tuple(sorted(self._schemas))

    def get(self, schema_id: str, schema_version: int) -> GovernedSchema:
        key = (schema_id, schema_version)
        try:
            return self._schemas[key]
        except KeyError as exc:
            raise SchemaNotFoundError(
                f"Governed schema not found: {schema_id}@{schema_version}"
            ) from exc

    @property
    def reference_registry(self) -> Registry:
        return self._reference_registry

    def _load(self) -> None:
        if not self._root.is_dir():
            raise SchemaRegistryError(
                f"Governed schema directory does not exist: {self._root}"
            )

        paths = sorted(self._root.glob("*.json"))
        if not paths:
            raise SchemaRegistryError(
                f"No governed JSON schemas found in: {self._root}"
            )

        reference_registry = Registry()

        for path in paths:
            document = self._read_schema(path)
            governed = self._governed_schema(path, document)

            existing = self._schemas.get(governed.logical_key)
            if existing is not None:
                if dict(existing.document) != dict(governed.document):
                    raise SchemaConflictError(
                        "Conflicting definitions for governed schema "
                        f"{governed.schema_id}@{governed.schema_version}: "
                        f"{existing.source_path} and {path}"
                    )
                raise SchemaRegistryError(
                    "Duplicate governed schema publication for "
                    f"{governed.schema_id}@{governed.schema_version}: "
                    f"{existing.source_path} and {path}"
                )

            self._schemas[governed.logical_key] = governed

            resource = Resource.from_contents(document)

            # Register every representation needed for local relative $ref
            # resolution without making any of them part of the public schema
            # lookup contract.
            reference_registry = reference_registry.with_resource(path.name, resource)
            reference_registry = reference_registry.with_resource(path.as_uri(), resource)

            json_schema_id = document.get("$id")
            if isinstance(json_schema_id, str) and json_schema_id:
                reference_registry = reference_registry.with_resource(
                    json_schema_id,
                    resource,
                )

        self._reference_registry = reference_registry

    @staticmethod
    def _read_schema(path: Path) -> Mapping[str, Any]:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SchemaRegistryError(
                f"Unable to load governed schema {path}: {exc}"
            ) from exc

        if not isinstance(document, dict):
            raise SchemaRegistryError(
                f"Governed schema must be a JSON object: {path}"
            )

        try:
            Draft202012Validator.check_schema(document)
        except Exception as exc:
            raise SchemaRegistryError(
                f"Invalid JSON Schema 2020-12 definition {path}: {exc}"
            ) from exc

        return document

    @staticmethod
    def _governed_schema(
        path: Path,
        document: Mapping[str, Any],
    ) -> GovernedSchema:
        schema_id = document.get("schema_id")
        schema_version = document.get("schema_version")
        status = document.get("status")

        if not isinstance(schema_id, str) or not schema_id.strip():
            raise SchemaRegistryError(
                f"Schema is missing non-empty schema_id: {path}"
            )

        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version < 1
        ):
            raise SchemaRegistryError(
                f"Schema has invalid schema_version: {path}"
            )

        if not isinstance(status, str) or not status.strip():
            raise SchemaRegistryError(
                f"Schema is missing non-empty status: {path}"
            )

        return GovernedSchema(
            schema_id=schema_id,
            schema_version=schema_version,
            status=status,
            document=document,
            source_path=path.resolve(),
        )

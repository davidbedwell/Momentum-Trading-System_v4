from __future__ import annotations

import json
from pathlib import Path

import pytest

from Core.configuration import schemas_root
from Core.research_nexus import (
    SchemaNotFoundError,
    SchemaRegistry,
    SchemaRegistryError,
    SchemaValidationError,
    SchemaValidator,
)


EXPECTED_IDENTITIES = {
    ("mts.artifact-envelope", 1),
    ("mts.artifact-reference", 1),
    ("mts.controlled-vocabularies", 1),
    ("mts.governed-reference", 1),
    ("mts.provenance", 1),
    ("mts.relationship", 1),
}


def valid_artifact_envelope() -> dict:
    return {
        "artifact_id": "artifact:01JTEST",
        "artifact_version": 1,
        "artifact_type": "FINDING",
        "schema_id": "mts.finding",
        "schema_version": 1,
        "created_at": "2026-08-07T10:00:00Z",
        "producer": {
            "producer_type": "ENGINE",
            "producer_id": "engine:discovery",
        },
        "provenance": {
            "input_refs": [],
        },
        "lifecycle_state": "DRAFT",
        "persistence_class": "CLASS_II",
        "retention_class": "SEMI_PERMANENT",
        "backup_requirement": "REQUIRED",
        "tags": ["AAPL"],
    }


def test_registry_loads_all_current_governed_schemas():
    registry = SchemaRegistry()

    assert registry.root == schemas_root().resolve()
    assert set(registry.identities()) == EXPECTED_IDENTITIES


def test_registry_lookup_uses_logical_identity_not_filename():
    registry = SchemaRegistry()

    schema = registry.get("mts.artifact-envelope", 1)

    assert schema.schema_id == "mts.artifact-envelope"
    assert schema.schema_version == 1
    assert schema.source_path.name == "artifact_envelope.schema.json"


def test_unknown_schema_fails_explicitly():
    registry = SchemaRegistry()

    with pytest.raises(SchemaNotFoundError):
        registry.get("mts.does-not-exist", 1)


def test_registry_rejects_missing_governed_schema_metadata(tmp_path):
    path = tmp_path / "bad.schema.json"
    path.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SchemaRegistryError, match="schema_id"):
        SchemaRegistry(tmp_path)


def test_registry_rejects_duplicate_logical_identity(tmp_path):
    source = json.loads(
        (schemas_root() / "artifact_reference.schema.json").read_text(
            encoding="utf-8"
        )
    )

    (tmp_path / "one.json").write_text(json.dumps(source), encoding="utf-8")
    (tmp_path / "two.json").write_text(json.dumps(source), encoding="utf-8")

    with pytest.raises(SchemaRegistryError, match="Duplicate governed schema"):
        SchemaRegistry(tmp_path)


def test_validator_accepts_valid_envelope_and_resolves_relative_refs():
    validator = SchemaValidator()

    validator.validate(
        valid_artifact_envelope(),
        schema_id="mts.artifact-envelope",
        schema_version=1,
    )


def test_validator_rejects_invalid_controlled_vocabulary():
    validator = SchemaValidator()
    instance = valid_artifact_envelope()
    instance["artifact_type"] = "MADE_UP_TYPE"

    with pytest.raises(SchemaValidationError) as exc_info:
        validator.validate(
            instance,
            schema_id="mts.artifact-envelope",
            schema_version=1,
        )

    assert any("artifact_type" in error for error in exc_info.value.errors)


def test_validator_rejects_invalid_datetime_format():
    validator = SchemaValidator()
    instance = valid_artifact_envelope()
    instance["created_at"] = "not-a-datetime"

    with pytest.raises(SchemaValidationError) as exc_info:
        validator.validate(
            instance,
            schema_id="mts.artifact-envelope",
            schema_version=1,
        )

    assert any("created_at" in error for error in exc_info.value.errors)


def test_validator_rejects_missing_required_field():
    validator = SchemaValidator()
    instance = valid_artifact_envelope()
    del instance["provenance"]

    with pytest.raises(SchemaValidationError) as exc_info:
        validator.validate(
            instance,
            schema_id="mts.artifact-envelope",
            schema_version=1,
        )

    assert any("provenance" in error for error in exc_info.value.errors)

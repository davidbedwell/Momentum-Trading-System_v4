from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from Core.research_nexus.models import ArtifactReference
from Core.research_nexus.storage import (
    IndexDocument,
    IndexStore,
    SQLiteIndexStore,
    UnsupportedIndexCriterionError,
)


@pytest.fixture
def index(tmp_path: Path) -> SQLiteIndexStore:
    return SQLiteIndexStore(tmp_path / "index.sqlite3")


def doc(
    artifact_id: str,
    version: int = 1,
    **fields,
) -> IndexDocument:
    return IndexDocument(
        artifact_ref=ArtifactReference(artifact_id, version),
        fields=fields,
    )


def test_sqlite_index_satisfies_index_port(index):
    assert isinstance(index, IndexStore)


def test_schema_initializes_once(index):
    with sqlite3.connect(index.database_path) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
        assert conn.execute(
            "SELECT version FROM index_schema_migrations"
        ).fetchall() == [(1,)]


def test_upsert_and_search_exact_scalar(index):
    index.upsert(
        doc(
            "artifact:a",
            artifact_type="FINDING",
            lifecycle_state="VALIDATED",
        )
    )

    assert index.search({"artifact_type": "FINDING"}) == (
        ArtifactReference("artifact:a", 1),
    )


def test_search_requires_all_criteria(index):
    index.upsert(
        doc(
            "artifact:a",
            artifact_type="FINDING",
            lifecycle_state="VALIDATED",
        )
    )
    index.upsert(
        doc(
            "artifact:b",
            artifact_type="FINDING",
            lifecycle_state="DRAFT",
        )
    )

    assert index.search(
        {
            "artifact_type": "FINDING",
            "lifecycle_state": "VALIDATED",
        }
    ) == (ArtifactReference("artifact:a", 1),)


def test_scalar_expected_matches_member_of_list_field(index):
    index.upsert(
        doc(
            "artifact:a",
            tags=["AAPL", "MOMENTUM"],
        )
    )

    assert index.search({"tags": "AAPL"}) == (
        ArtifactReference("artifact:a", 1),
    )


def test_list_expected_requires_all_members_of_list_field(index):
    index.upsert(
        doc(
            "artifact:a",
            tags=["AAPL", "MOMENTUM", "DAILY"],
        )
    )
    index.upsert(
        doc(
            "artifact:b",
            tags=["AAPL"],
        )
    )

    assert index.search({"tags": ["AAPL", "MOMENTUM"]}) == (
        ArtifactReference("artifact:a", 1),
    )


def test_list_expected_against_scalar_means_any_allowed_value(index):
    index.upsert(doc("artifact:a", artifact_type="FINDING"))
    index.upsert(doc("artifact:b", artifact_type="EVIDENCE"))
    index.upsert(doc("artifact:c", artifact_type="DECISION"))

    assert index.search(
        {"artifact_type": ["FINDING", "EVIDENCE"]}
    ) == (
        ArtifactReference("artifact:a", 1),
        ArtifactReference("artifact:b", 1),
    )


def test_missing_field_does_not_match(index):
    index.upsert(doc("artifact:a", artifact_type="FINDING"))

    assert index.search({"instrument": "AAPL"}) == ()


def test_empty_criteria_returns_all_in_stable_order(index):
    index.upsert(doc("artifact:b", artifact_type="EVIDENCE"))
    index.upsert(doc("artifact:a", artifact_type="FINDING", version_marker=1))
    index.upsert(doc("artifact:a", 2, artifact_type="FINDING", version_marker=2))

    assert index.search({}) == (
        ArtifactReference("artifact:a", 1),
        ArtifactReference("artifact:a", 2),
        ArtifactReference("artifact:b", 1),
    )


def test_limit_is_applied_after_matching(index):
    for name in ("a", "b", "c"):
        index.upsert(
            doc(
                f"artifact:{name}",
                artifact_type="FINDING",
            )
        )

    assert index.search({"artifact_type": "FINDING"}, limit=2) == (
        ArtifactReference("artifact:a", 1),
        ArtifactReference("artifact:b", 1),
    )


def test_zero_limit_returns_empty(index):
    index.upsert(doc("artifact:a", artifact_type="FINDING"))

    assert index.search({}, limit=0) == ()


def test_negative_limit_rejected(index):
    with pytest.raises(ValueError):
        index.search({}, limit=-1)


def test_upsert_replaces_index_fields_for_same_artifact_version(index):
    index.upsert(
        doc(
            "artifact:a",
            artifact_type="FINDING",
            lifecycle_state="DRAFT",
        )
    )
    index.upsert(
        doc(
            "artifact:a",
            artifact_type="FINDING",
            lifecycle_state="VALIDATED",
        )
    )

    assert index.search({"lifecycle_state": "DRAFT"}) == ()
    assert index.search({"lifecycle_state": "VALIDATED"}) == (
        ArtifactReference("artifact:a", 1),
    )


def test_remove_is_idempotent(index):
    ref = ArtifactReference("artifact:a", 1)
    index.upsert(doc("artifact:a", artifact_type="FINDING"))

    index.remove(ref)
    index.remove(ref)

    assert index.search({}) == ()


def test_artifact_versions_are_indexed_independently(index):
    index.upsert(doc("artifact:a", 1, state="OLD"))
    index.upsert(doc("artifact:a", 2, state="CURRENT"))

    assert index.search({"state": "OLD"}) == (
        ArtifactReference("artifact:a", 1),
    )
    assert index.search({"state": "CURRENT"}) == (
        ArtifactReference("artifact:a", 2),
    )


def test_unsupported_nested_criterion_rejected(index):
    with pytest.raises(UnsupportedIndexCriterionError):
        index.search({"provenance": {"model": "x"}})


def test_index_returns_only_governed_artifact_references(index):
    index.upsert(doc("artifact:a", artifact_type="FINDING"))

    result = index.search({})

    assert result
    assert all(isinstance(item, ArtifactReference) for item in result)


def test_index_database_has_no_dependency_on_catalog_tables(index):
    with sqlite3.connect(index.database_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

    assert "index_documents" in tables
    assert "artifacts" not in tables
    assert "representations" not in tables

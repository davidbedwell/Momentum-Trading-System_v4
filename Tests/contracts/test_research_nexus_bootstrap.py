from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from Core.research_nexus import (
    Producer,
    Provenance,
    ResearchNexus,
    ResearchNexusConfig,
    build_research_nexus,
    create_artifact_envelope,
)


def test_config_derives_backend_paths_from_runtime_root(tmp_path: Path):
    config = ResearchNexusConfig(tmp_path / "runtime")

    assert config.catalog_path == tmp_path / "runtime" / "catalog" / "nexus_catalog.sqlite3"
    assert config.index_path == tmp_path / "runtime" / "index" / "nexus_index.sqlite3"
    assert config.payload_root == tmp_path / "runtime" / "payloads"


def test_bootstrap_returns_public_facade(tmp_path: Path):
    nexus = build_research_nexus(
        ResearchNexusConfig(tmp_path / "runtime")
    )

    assert isinstance(nexus, ResearchNexus)


def test_bootstrap_creates_required_runtime_storage(tmp_path: Path):
    config = ResearchNexusConfig(tmp_path / "runtime")

    build_research_nexus(config)

    assert config.catalog_path.is_file()
    assert config.index_path.is_file()
    assert config.payload_root.is_dir()


def test_bootstrapped_nexus_round_trip(tmp_path: Path):
    nexus = build_research_nexus(
        ResearchNexusConfig(tmp_path / "runtime")
    )

    env = create_artifact_envelope(
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:discovery",
        ),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id="artifact:bootstrap",
        artifact_version=1,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        tags=("AAPL",),
    )

    result = nexus.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING", "tags": ["AAPL"]},
    )

    retrieved = nexus.get(result.artifact_ref)

    assert retrieved.envelope == env
    assert retrieved.payload == b"payload"
    assert nexus.query({"tags": "AAPL"}) == (env,)


def test_bootstrap_reuses_existing_runtime_state(tmp_path: Path):
    config = ResearchNexusConfig(tmp_path / "runtime")
    first = build_research_nexus(config)

    env = create_artifact_envelope(
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:discovery",
        ),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id="artifact:persisted",
        artifact_version=1,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
    )

    result = first.publish(
        envelope=env,
        payload=b"persisted",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING"},
    )

    second = build_research_nexus(config)

    assert second.get(result.artifact_ref).payload == b"persisted"
    assert second.query({"artifact_type": "FINDING"}) == (env,)


def test_bootstrap_module_is_only_backend_composition_boundary():
    import Core.research_nexus.bootstrap as bootstrap

    source = Path(bootstrap.__file__).read_text(encoding="utf-8")

    assert "SQLiteCatalogStore" in source
    assert "SQLiteIndexStore" in source
    assert "FilesystemPayloadStore" in source


def test_public_facade_module_does_not_import_concrete_backends():
    import Core.research_nexus.facade as facade

    source = Path(facade.__file__).read_text(encoding="utf-8")

    assert "SQLiteCatalogStore" not in source
    assert "SQLiteIndexStore" not in source
    assert "FilesystemPayloadStore" not in source


def test_runtime_root_is_explicit_not_repo_derived(tmp_path: Path):
    config = ResearchNexusConfig(tmp_path / "external-runtime")

    assert config.runtime_root == tmp_path / "external-runtime"
    assert "Momentum-Trading-System_v2" not in str(config.runtime_root)

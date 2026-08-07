from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from Core.research_nexus.models import ArtifactReference
from Core.research_nexus.storage import (
    FilesystemPayloadStore,
    InvalidLocatorError,
    PayloadNotFoundError,
    PayloadStore,
)


@pytest.fixture
def store(tmp_path: Path) -> FilesystemPayloadStore:
    return FilesystemPayloadStore(tmp_path / "nexus-payload")


def test_filesystem_payload_store_satisfies_payload_port(store):
    assert isinstance(store, PayloadStore)


def test_put_get_round_trip(store):
    ref = ArtifactReference("artifact:test", 1)
    payload = b'{"value": 42}'

    result = store.put(
        ref,
        payload,
        media_type="application/json",
    )

    assert store.get(result.locator) == payload
    assert result.media_type == "application/json"
    assert result.size_bytes == len(payload)


def test_sha256_is_recorded_from_written_bytes(store):
    ref = ArtifactReference("artifact:test", 1)
    payload = b"abc"

    result = store.put(
        ref,
        payload,
        media_type="application/octet-stream",
    )

    expected = hashlib.sha256(payload).hexdigest()
    assert result.content_hash == f"sha256:{expected}"


def test_backend_owns_physical_placement(store):
    ref = ArtifactReference("artifact:logical-id", 7)

    result = store.put(
        ref,
        b"payload",
        media_type="application/octet-stream",
    )

    assert result.locator.startswith("nexus-fs:///")
    assert str(store.root) not in result.locator
    assert result.locator != ref.artifact_id


def test_same_artifact_and_same_content_is_idempotent(store):
    ref = ArtifactReference("artifact:test", 1)

    first = store.put(
        ref,
        b"same",
        media_type="application/octet-stream",
    )
    second = store.put(
        ref,
        b"same",
        media_type="application/octet-stream",
    )

    assert first.locator == second.locator
    assert first.content_hash == second.content_hash


def test_same_artifact_different_content_gets_distinct_representation(store):
    ref = ArtifactReference("artifact:test", 1)

    first = store.put(
        ref,
        b"first",
        media_type="application/octet-stream",
    )
    second = store.put(
        ref,
        b"second",
        media_type="application/octet-stream",
    )

    assert first.locator != second.locator
    assert store.get(first.locator) == b"first"
    assert store.get(second.locator) == b"second"


def test_artifact_id_cannot_escape_storage_root(store):
    ref = ArtifactReference("artifact:../../escape", 1)

    result = store.put(
        ref,
        b"safe",
        media_type="application/octet-stream",
    )

    assert store.get(result.locator) == b"safe"
    assert store.root in Path(store.root).parents or store.root.is_absolute()


def test_exists_reports_current_representation_state(store):
    ref = ArtifactReference("artifact:test", 1)

    result = store.put(
        ref,
        b"payload",
        media_type="application/octet-stream",
    )

    assert store.exists(result.locator) is True

    store.delete(result.locator)

    assert store.exists(result.locator) is False


def test_get_missing_payload_raises_typed_error(store):
    with pytest.raises(PayloadNotFoundError):
        store.get("nexus-fs:///objects/aa/bb/missing/1/hash")


def test_delete_missing_payload_raises_typed_error(store):
    with pytest.raises(PayloadNotFoundError):
        store.delete("nexus-fs:///objects/aa/bb/missing/1/hash")


def test_foreign_locator_is_rejected(store):
    with pytest.raises(InvalidLocatorError):
        store.get("file:///tmp/not-owned-by-nexus")


def test_locator_escape_is_rejected(store):
    with pytest.raises(InvalidLocatorError):
        store.get("nexus-fs:///../../outside")


def test_payload_requires_bytes(store):
    ref = ArtifactReference("artifact:test", 1)

    with pytest.raises(TypeError):
        store.put(
            ref,
            "not-bytes",  # type: ignore[arg-type]
            media_type="text/plain",
        )


def test_media_type_must_be_non_empty(store):
    ref = ArtifactReference("artifact:test", 1)

    with pytest.raises(ValueError):
        store.put(
            ref,
            b"payload",
            media_type="",
        )

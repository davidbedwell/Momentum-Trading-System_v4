from __future__ import annotations

import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

from Core.research_nexus.models import ArtifactReference
from Core.research_nexus.storage.ports import PayloadWriteResult


class PayloadStoreError(RuntimeError):
    """Base class for filesystem payload-store failures."""


class InvalidLocatorError(PayloadStoreError):
    """Raised when a locator does not belong to this payload store."""


class PayloadNotFoundError(PayloadStoreError):
    """Raised when a referenced payload representation does not exist."""


class FilesystemPayloadStore:
    """Filesystem implementation of the PayloadStore port.

    The backend alone owns physical placement. Callers provide governed artifact
    identity plus bytes/media type and receive an opaque locator. Artifact
    identity never depends on the resulting path.
    """

    def __init__(self, root: Path) -> None:
        self._root = Path(root).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def put(
        self,
        artifact_ref: ArtifactReference,
        payload: bytes,
        *,
        media_type: str,
    ) -> PayloadWriteResult:
        if not isinstance(payload, bytes):
            raise TypeError("payload must be bytes")
        if not media_type or not isinstance(media_type, str):
            raise ValueError("media_type must be a non-empty string")

        content_hash = hashlib.sha256(payload).hexdigest()
        destination = self._path_for(artifact_ref, content_hash)

        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            existing = destination.read_bytes()
            if hashlib.sha256(existing).hexdigest() != content_hash:
                raise PayloadStoreError(
                    f"Existing payload at {destination} does not match expected hash"
                )
        else:
            self._atomic_write(destination, payload)

        stat = destination.stat()

        return PayloadWriteResult(
            locator=self._locator_for(destination),
            media_type=media_type,
            content_hash=f"sha256:{content_hash}",
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.utc,
            ).isoformat().replace("+00:00", "Z"),
        )

    def get(self, locator: str) -> bytes:
        path = self._path_from_locator(locator)

        try:
            return path.read_bytes()
        except FileNotFoundError as exc:
            raise PayloadNotFoundError(f"Payload not found: {locator}") from exc

    def exists(self, locator: str) -> bool:
        try:
            path = self._path_from_locator(locator)
        except InvalidLocatorError:
            return False
        return path.is_file()

    def delete(self, locator: str) -> None:
        path = self._path_from_locator(locator)

        try:
            path.unlink()
        except FileNotFoundError as exc:
            raise PayloadNotFoundError(f"Payload not found: {locator}") from exc

        self._prune_empty_parents(path.parent)

    def _path_for(
        self,
        artifact_ref: ArtifactReference,
        content_hash: str,
    ) -> Path:
        safe_id = quote(artifact_ref.artifact_id, safe="")
        version = str(artifact_ref.artifact_version)

        return (
            self._root
            / "objects"
            / content_hash[:2]
            / content_hash[2:4]
            / safe_id
            / version
            / content_hash
        )

    def _locator_for(self, path: Path) -> str:
        relative = path.relative_to(self._root)
        encoded_parts = [quote(part, safe="") for part in relative.parts]
        return "nexus-fs:///" + "/".join(encoded_parts)

    def _path_from_locator(self, locator: str) -> Path:
        parsed = urlparse(locator)

        if parsed.scheme != "nexus-fs" or parsed.netloc:
            raise InvalidLocatorError(f"Unsupported payload locator: {locator}")

        raw_parts = [part for part in parsed.path.split("/") if part]
        if not raw_parts:
            raise InvalidLocatorError(f"Invalid payload locator: {locator}")

        relative = Path(*(unquote(part) for part in raw_parts))
        candidate = (self._root / relative).resolve()

        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise InvalidLocatorError(
                f"Payload locator escapes configured root: {locator}"
            ) from exc

        return candidate

    @staticmethod
    def _atomic_write(destination: Path, payload: bytes) -> None:
        fd, tmp_name = tempfile.mkstemp(
            prefix=".staging-",
            dir=destination.parent,
        )
        tmp_path = Path(tmp_name)

        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(tmp_path, destination)
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            finally:
                raise

    def _prune_empty_parents(self, start: Path) -> None:
        current = start

        while current != self._root:
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent

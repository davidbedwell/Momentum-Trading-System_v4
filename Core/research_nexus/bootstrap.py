from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from Core.research_nexus.facade import NexusServices, ResearchNexus
from Core.research_nexus.publication import PublicationCoordinator
from Core.research_nexus.retrieval import RetrievalService
from Core.research_nexus.storage import (
    FilesystemPayloadStore,
    SQLiteCatalogStore,
    SQLiteIndexStore,
)


@dataclass(frozen=True, slots=True)
class ResearchNexusConfig:
    """Runtime composition settings for one Research Nexus instance."""

    runtime_root: Path

    @property
    def catalog_path(self) -> Path:
        return self.runtime_root / "catalog" / "nexus_catalog.sqlite3"

    @property
    def index_path(self) -> Path:
        return self.runtime_root / "index" / "nexus_index.sqlite3"

    @property
    def payload_root(self) -> Path:
        return self.runtime_root / "payloads"


def build_research_nexus(config: ResearchNexusConfig) -> ResearchNexus:
    """Construct the canonical initial Research Nexus stack.

    Backend choices live here, not in engines. Replacing SQLite/filesystem
    implementations later should require composition changes rather than
    engine-facing contract changes.
    """
    catalog = SQLiteCatalogStore(config.catalog_path)
    index = SQLiteIndexStore(config.index_path)
    payloads = FilesystemPayloadStore(config.payload_root)

    publication = PublicationCoordinator(
        catalog=catalog,
        payloads=payloads,
        index=index,
    )
    retrieval = RetrievalService(
        catalog=catalog,
        payloads=payloads,
        index=index,
    )

    return ResearchNexus(
        NexusServices(
            publication=publication,
            retrieval=retrieval,
        )
    )

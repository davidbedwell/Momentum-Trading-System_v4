from pathlib import Path

import pytest

from Engines.Analysis.registry import (
    AnalysisMethodRegistry,
    AnalysisMethodRegistryError,
)


REGISTRY = Path("Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv")


def test_clean_v2_registry_loads():
    registry = AnalysisMethodRegistry.from_csv(REGISTRY)
    assert len(registry.active()) == 5
    assert registry.get("analysis.foundation.dataset-introspection").version == "1"


def test_runtime_registry_contains_no_legacy_a09_identities():
    registry = AnalysisMethodRegistry.from_csv(REGISTRY)
    assert all(not spec.method_id.startswith("A09-") for spec in registry.all())


def test_registry_family_selection_is_deterministic():
    registry = AnalysisMethodRegistry.from_csv(REGISTRY)
    specs = registry.by_family("FOUNDATION")
    assert tuple(spec.method_id for spec in specs) == (
        "analysis.foundation.dataset-introspection",
    )


def test_legacy_a09_runtime_identity_is_rejected(tmp_path: Path):
    source = REGISTRY.read_text()
    source = source.replace(
        "analysis.foundation.dataset-introspection",
        "A09-FOUNDATION-001",
        1,
    )
    bad = tmp_path / "bad.csv"
    bad.write_text(source)
    with pytest.raises(AnalysisMethodRegistryError, match="Legacy A09"):
        AnalysisMethodRegistry.from_csv(bad)

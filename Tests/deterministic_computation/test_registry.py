from Core.deterministic_computation import build_registry, registered_families


def test_registry_identity_and_versions():
    registry = build_registry()
    assert "TREND" in registry
    assert "VOLUME_LIQUIDITY" in registry
    assert registry["TREND"].version == "0.1.0"
    assert registry["STATISTICS_LIQUIDITY_REFERENCE"].status == "REFERENCE"


def test_registry_table_is_complete():
    table = registered_families()
    assert len(table) == 7
    assert table["family_id"].is_unique

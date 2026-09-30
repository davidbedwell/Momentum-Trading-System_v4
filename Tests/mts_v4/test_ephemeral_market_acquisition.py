from pathlib import Path


def test_update_script_supports_diskless_ephemeral_acquisition():
    text = Path("scripts/update_derived_market_store.py").read_text()
    assert '"--ephemeral-acquisition"' in text
    assert "None if args.ephemeral_acquisition" in text
    assert "--ephemeral-acquisition cannot be combined with --acquisition-cache-root" in text


def test_updater_does_not_persist_raw_rows_and_clears_cache_after_success():
    text = Path("MTS_V4/derived_market_updater.py").read_text()
    assert '"raw_rows_persisted": False' in text
    assert "acquisition_cache.clear_after_success()" in text

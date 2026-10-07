from pathlib import Path
from Core.layered_ga.stage2_recovered_source_preflight_v3 import (
    verify_recovered_sources, SOURCES
)


def test_recovered_sources_are_never_implicitly_assumed_present():
    result = verify_recovered_sources()
    assert result["decision"] in ("PASS", "BLOCK")
    assert set(result["checks"]) == set(SOURCES)
    assert all(v["status"] in ("VERIFIED", "MISSING", "HASH_MISMATCH", "UNPINNED")
               for v in result["checks"].values())


def test_preflight_reports_exact_source_paths():
    result = verify_recovered_sources()
    for key, path in SOURCES.items():
        assert result["checks"][key]["path"].endswith(path.name)

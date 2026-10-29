from pathlib import Path

import pytest

from Engines.Analysis.cache import ResearchCache, ResearchCacheError


def test_cache_is_task_local_class_iii_and_non_authoritative(tmp_path):
    cache = ResearchCache(tmp_path / "analysis-cache", task_id="task:A")
    entry = cache.put_json("cohort-table", {"rows": [1, 2, 3]})

    assert entry.persistence_class == "CLASS_III"
    assert entry.authoritative is False
    assert cache.exists(entry)
    assert cache.get_json(entry) == {"rows": [1, 2, 3]}
    assert entry.path.is_relative_to(cache.task_root)


def test_cache_identity_is_deterministic_for_same_task_key_payload(tmp_path):
    cache = ResearchCache(tmp_path / "analysis-cache", task_id="task:A")
    first = cache.put_json("scratch", {"value": 1})
    second = cache.put_json("scratch", {"value": 1})
    assert first.path == second.path
    assert first.content_hash == second.content_hash


def test_cache_isolated_between_tasks(tmp_path):
    a = ResearchCache(tmp_path / "analysis-cache", task_id="task:A")
    b = ResearchCache(tmp_path / "analysis-cache", task_id="task:B")
    entry = a.put_json("scratch", {"value": 1})
    assert a.task_root != b.task_root
    with pytest.raises(ResearchCacheError):
        b.get_json(entry)


def test_cache_can_be_deleted(tmp_path):
    cache = ResearchCache(tmp_path / "analysis-cache", task_id="task:A")
    entry = cache.put_json("candidate", {"candidate": True})
    assert entry.path.exists()
    cache.clear_task()
    assert not cache.task_root.exists()


def test_cache_has_no_nexus_or_warehouse_dependency():
    source = Path("Engines/Analysis/cache.py").read_text()
    assert "research_nexus" not in source.lower()
    assert "Warehouse" not in source
    assert "publish(" not in source

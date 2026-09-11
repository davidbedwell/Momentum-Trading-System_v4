from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from Core.configuration import paths


def test_repository_root_is_semantically_identified():
    root = paths.repository_root()
    pyproject = root / "pyproject.toml"

    assert pyproject.is_file()
    text = pyproject.read_text(encoding="utf-8")
    assert 'name = "momentum-trading-system-v4"' in text


def test_repository_root_is_independent_of_cwd(tmp_path, monkeypatch):
    expected = paths.repository_root()
    monkeypatch.chdir(tmp_path)

    assert paths.repository_root() == expected


def test_governance_paths_resolve_from_repository_root():
    root = paths.repository_root()

    assert paths.governance_root() == root / "Governance"
    assert paths.schemas_root() == root / "Governance" / "Schemas"
    assert paths.contracts_root() == root / "Governance" / "Contracts"


def test_root_detection_does_not_depend_on_fixed_parent_depth(tmp_path):
    repo = tmp_path / "arbitrary" / "deep" / "mts"
    module_dir = repo / "x" / "y" / "z"
    module_dir.mkdir(parents=True)

    (repo / "pyproject.toml").write_text(
        '[project]\nname = "momentum-trading-system-v4"\nversion = "0.0.0"\n',
        encoding="utf-8",
    )

    source = Path(paths.__file__).read_text(encoding="utf-8")
    copied = module_dir / "paths.py"
    copied.write_text(source, encoding="utf-8")

    spec = importlib.util.spec_from_file_location("isolated_paths", copied)
    assert spec and spec.loader

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.repository_root() == repo


def test_root_detection_fails_loudly_when_identity_is_absent(tmp_path):
    module_dir = tmp_path / "not_mts" / "Core" / "configuration"
    module_dir.mkdir(parents=True)

    source = Path(paths.__file__).read_text(encoding="utf-8")
    copied = module_dir / "paths.py"
    copied.write_text(source, encoding="utf-8")

    spec = importlib.util.spec_from_file_location("isolated_paths_missing", copied)
    assert spec and spec.loader

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with pytest.raises(module.RepositoryRootNotFoundError):
        module.repository_root()

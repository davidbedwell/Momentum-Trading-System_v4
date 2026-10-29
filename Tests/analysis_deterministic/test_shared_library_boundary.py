from pathlib import Path


def test_analysis_contains_no_duplicate_sma_or_indicator_implementation():
    source = Path("Engines/Analysis/deterministic.py").read_text()

    assert "rolling(" not in source
    assert ".ewm(" not in source
    assert "def sma" not in source.lower()
    assert "execute_computations" in source


def test_analysis_imports_shared_core_library_not_intake_private_code():
    source = Path("Engines/Analysis/deterministic.py").read_text()

    assert "from Core.deterministic_computation import execute_computations" in source
    assert "Engines.Intake" not in source
    assert "Warehouse" not in source

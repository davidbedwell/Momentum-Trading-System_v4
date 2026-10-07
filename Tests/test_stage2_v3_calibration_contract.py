"""Fail-closed regression guards for the frozen V3 calibration contract.

These tests intentionally fail against the 2026-10-07 implementation.
They must pass before paid calibration can be restarted.
"""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
EVOLUTION = ROOT / "scripts/run_stage2_v3_evolutionary_calibration_20261007.py"


def _source():
    return EVOLUTION.read_text()


def test_evolutionary_calibration_uses_full_path_statistical_evaluator():
    source = _source()
    assert "evaluate_curve(" in source, (
        "GA fitness must use the real 1..63 path evaluator, not single-day target overlap"
    )


def test_evolutionary_fitness_has_no_target_or_effect_oracle():
    tree = ast.parse(_source())
    matched = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "MatchedEvaluator"
    )
    evaluate = next(
        node for node in matched.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "evaluate"
    )
    accesses = {
        node.attr for node in ast.walk(evaluate)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"
    }
    assert "target" not in accesses, "GA must not inspect planted target identity"
    assert "effect" not in accesses, "GA must not inspect known planted effect magnitude"


def test_evolutionary_search_has_independent_baseline_and_ga_best():
    source = _source()
    assert "best_ga':ev.best" not in source, (
        "ev.best includes the planted target baseline, so it cannot prove GA recovery"
    )


def test_evolutionary_calibration_has_real_certification_gate():
    source = _source()
    assert "STOPPED_ENGINEERING_FULL_BUDGET_AND_STATISTICAL_GATE_PENDING" not in source, (
        "A finished calibration must implement and enforce its statistical acceptance gate"
    )

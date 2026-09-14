from __future__ import annotations

import ast
from pathlib import Path


def _main_function(tree: ast.AST) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node
    raise AssertionError("main() not found in production SOL runner")


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return ""


def test_production_runner_builds_pre_sol_substrates_before_orchestrator_rd_boundary():
    source = Path("scripts/run_sol_batched_one_subject.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    main = _main_function(tree)

    build_line = None
    run_line = None
    run_call = None

    for node in ast.walk(main):
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "precomputed_results" for target in node.targets):
                value = node.value
                if isinstance(value, ast.Call) and _call_name(value) == "dict" and value.args:
                    inner = value.args[0]
                    if isinstance(inner, ast.Call) and _call_name(inner) == "build_pre_sol_substrates":
                        build_line = node.lineno
        elif isinstance(node, ast.Call) and _call_name(node) == "runtime.orchestrator.run":
            run_line = node.lineno
            run_call = node

    assert build_line is not None, "production runner does not build combined pre-SOL substrates"
    assert run_line is not None and run_call is not None, "production orchestrator.run() call not found"
    assert build_line < run_line, "pre-SOL Analysis must complete before the RD/orchestrator boundary"

    keywords = {keyword.arg: keyword.value for keyword in run_call.keywords if keyword.arg}
    assert "precomputed_results" in keywords, "orchestrator does not receive precomputed_results"
    handed_off = keywords["precomputed_results"]
    assert isinstance(handed_off, ast.Name) and handed_off.id == "precomputed_results"


def test_production_runner_uses_combined_pre_sol_composer_not_legacy_individual_builders():
    source = Path("scripts/run_sol_batched_one_subject.py").read_text(encoding="utf-8")
    assert "from MTS_V4.pre_sol_substrates import build_for_subject as build_pre_sol_substrates" in source
    assert "build_neutral_substrate" not in source
    assert "build_sec_share_structure" not in source

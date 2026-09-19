from __future__ import annotations

import pytest

from MTS_V4.acceptance_controls import BLINDED_CONTROLS
from scripts.run_sol_scientific_controls import (
    _run_control_with_live_log,
    _selected_controls,
)


def test_no_selection_preserves_full_five_control_campaign() -> None:
    assert _selected_controls(None) == BLINDED_CONTROLS


def test_one_control_selection_is_exact_and_rejects_unknown_ids() -> None:
    selected = _selected_controls("medium_term_trend_persistence")
    assert tuple(control.control_id for control in selected) == (
        "medium_term_trend_persistence",
    )
    with pytest.raises(ValueError, match="unknown scientific control"):
        _selected_controls("not-a-control")


def test_control_output_is_streamed_and_preserved(tmp_path, capsys) -> None:
    log_path = tmp_path / "control.runner.txt"

    exit_code = _run_control_with_live_log(
        ["python3", "-c", "print('CONTROL_PROGRESS PERCENT=50')"],
        control_id="medium_term_trend_persistence",
        log_path=log_path,
    )

    assert exit_code == 0
    assert "CONTROL_PROGRESS PERCENT=50" in log_path.read_text(encoding="utf-8")
    assert "[medium_term_trend_persistence] CONTROL_PROGRESS PERCENT=50" in capsys.readouterr().out

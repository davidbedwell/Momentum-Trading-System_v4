from Core.layered_ga.architecture import (
    CONTRACTS, ContextState, Direction, Stage,
    assert_objective_allowed, assert_stage_can_run,
)


def test_all_stages_have_contracts():
    assert set(CONTRACTS) == set(Stage)


def test_stage2_requires_archaeology_and_context():
    try:
        assert_stage_can_run(Stage.OPPORTUNITY, {Stage.CONTEXT_MAP})
    except RuntimeError as e:
        assert "ARCHAEOLOGY" in str(e)
    else:
        raise AssertionError("Stage 2 ran without frozen Stage 0")


def test_stage2_blocks_cagr_and_mdd():
    for objective in ("cagr", "mdd"):
        try:
            assert_objective_allowed(Stage.OPPORTUNITY, objective)
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"Stage 2 incorrectly allowed {objective}")


def test_context_is_not_a_trade_gate():
    forbidden = CONTRACTS[Stage.POSITION_SIZING].forbidden_objectives
    assert "hard_context_trade_gate" in forbidden


def test_long_short_are_independent_directions():
    assert Direction.LONG != Direction.SHORT


def test_five_context_states_exist():
    assert {
        ContextState.STRONG_DOWN, ContextState.DOWN, ContextState.FLAT,
        ContextState.UP, ContextState.STRONG_UP,
    } == {
        "STRONG_DOWN", "DOWN", "FLAT", "UP", "STRONG_UP",
    }

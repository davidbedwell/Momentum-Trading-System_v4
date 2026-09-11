import inspect

from MTS_V4.sol_primary_provider import SolPrimaryResearchDirector
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor
from MTS_V4.subject_selection import SolAdaptiveSubjectSelector


def test_primary_sol_prompt_does_not_inherit_prior_parameters_as_defaults():
    source = inspect.getsource(SolPrimaryResearchDirector._decision_messages)

    assert "must never delimit the discovery space" in source
    assert "lookback windows" in source
    assert "forward horizons" in source
    assert "continuous or" in source and "normalized representations" in source
    assert "entirely different research propositions" in source
    assert "Do not inherit a prior numeric" in source
    assert "negative result for one formulation" in source
    assert "positive result does not" in source


def test_subject_selection_does_not_bind_within_subject_parameter_space():
    source = inspect.getsource(SolAdaptiveSubjectSelector.choose_next)

    assert "implicit queue that narrows later" in source
    assert "does not bind its Research Director" in source
    assert "lookback, forward horizon, threshold" in source
    assert "different scientifically" in source
    assert "Prior hypotheses and frontier entries are context, not a mandatory" in source


def test_frontier_authoring_cannot_define_later_exploration_contract():
    source = inspect.getsource(SolSubjectScientificMemoryAuthor.author_and_persist)

    assert "advisory scientific working memory, not a queue, mandate, or parameter contract" in source
    assert "different lookbacks, forward horizons" in source
    assert "entirely different propositions" in source
    assert "negative result for one formulation" in source
    assert "alternative parameterizations" in source

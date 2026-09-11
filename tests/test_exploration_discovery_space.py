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


def test_primary_sol_distinguishes_rp_closure_from_subject_closure():
    source = inspect.getsource(SolPrimaryResearchDirector._decision_messages)

    assert "distinguish exhaustion of the current Research Package" in source
    assert "Closing one RP is not evidence that the ticker is adequately explored" in source
    assert "continue research by opening a new RP" in source
    assert "not a requirement to manufacture more analyses" in source
    assert "eligible for renewed exploration" in source


def test_subject_selection_does_not_bind_within_subject_parameter_space():
    source = inspect.getsource(SolAdaptiveSubjectSelector.choose_next)

    assert "implicit queue that narrows later" in source
    assert "does not bind its Research Director" in source
    assert "lookback, forward horizon, threshold" in source
    assert "different scientifically" in source
    assert "Prior hypotheses and frontier entries are context, not a mandatory" in source


def test_exploration_priority_is_not_ranked_by_blind_validation_eligibility():
    source = inspect.getsource(SolAdaptiveSubjectSelector.choose_next)

    assert "exploration_exposure_priority" in source
    assert "SCIENTIFICALLY_NEUTRAL" in source
    assert "validation_eligibility_must_not_rank_exploration_subjects" in source
    assert "unexposed status confers no inherent EXPLORATION priority" in source
    assert "ignore retrospective_blind_validation_eligible" in source
    assert "future blind-validation campaign" in source


def test_frontier_authoring_cannot_define_later_exploration_contract():
    source = inspect.getsource(SolSubjectScientificMemoryAuthor.author_and_persist)

    assert "advisory scientific working memory, not a queue, mandate, or parameter contract" in source
    assert "different lookbacks, forward horizons" in source
    assert "entirely different propositions" in source
    assert "negative result for one formulation" in source
    assert "alternative parameterizations" in source

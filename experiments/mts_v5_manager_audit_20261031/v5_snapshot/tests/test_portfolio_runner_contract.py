import pytest
from discovery.competitive_ga.portfolio_runner_contract import windows, run_walkforward

def test_chronological_training_and_paired_defense():
    calls = []
    def fit(years):
        calls.append(('fit', years))
        return tuple(years)
    def evaluate(frozen, year, defense):
        assert max(frozen) < year
        calls.append(('evaluate', year, defense))
        return {'year': year, 'defense': defense}
    results = run_walkforward(fit=fit, evaluate=evaluate)
    assert len(results) == 4
    assert [r['train_years'] for r in results] == [(1,), (1,2), (1,2,3), (1,2,3,4)]
    assert calls[:3] == [('fit',(1,)), ('evaluate',2,False), ('evaluate',2,True)]
    assert calls[-3:] == [('fit',(1,2,3,4)), ('evaluate',5,False), ('evaluate',5,True)]

def test_both_defense_paths_are_mandatory():
    with pytest.raises(ValueError, match='both paired'):
        run_walkforward(fit=lambda years: years, evaluate=lambda frozen, year, defense: None if defense else {}, years=2)

"""Explicit accounting fixtures; these are not research chromosomes/results."""
import pytest
from discovery.competitive_ga.first_year_evolution import evolve,metrics
from engines.portfolio_replay.kernel import Bar


def test_training_never_requests_validation_until_winner_frozen():
    calls=[]
    def factory(end):
        calls.append(end)
        days=[(f'2026-01-{i:02d}',{'A':Bar(100,100)},[],[],False)
              for i in range(2,int(end[-2:])+1)]
        return days,{}
    result=evolve(factory,train_start='2026-01-02',train_end='2026-01-04',
                  validation_end='2026-01-06',size=2,generations=2)
    assert calls==['2026-01-04']*4+['2026-01-06']
    assert result['validation_fitness']==(0.,0.)
    assert not result['differentiated_training_fitness']


def test_fitness_includes_loss_from_initial_capital():
    assert metrics({'nav':[('a',90000),('b',95000)]})==pytest.approx((-.05,-.1))


def test_rejects_future_factory_data():
    def factory(end):
        return [(d,{'A':Bar(1,1)},[],[],False) for d in
                ['2026-01-02','2026-01-09']],{}
    with pytest.raises(ValueError,match='exact requested'):
        evolve(factory,train_start='2026-01-02',train_end='2026-01-04',
               validation_end='2026-01-06')


def test_validation_cannot_rewrite_training_prefix():
    def factory(end):
        days=[(f'2026-01-{i:02d}',{'A':Bar(100,100)},[],[],False)
              for i in range(2,int(end[-2:])+1)]
        if end=='2026-01-06':
            date,bars,native,outcomes,_=days[0]
            days[0]=(date,bars,native,outcomes,True)
        return days,{}
    with pytest.raises(ValueError,match='changed training prefix'):
        evolve(factory,train_start='2026-01-02',train_end='2026-01-04',
               validation_end='2026-01-06')

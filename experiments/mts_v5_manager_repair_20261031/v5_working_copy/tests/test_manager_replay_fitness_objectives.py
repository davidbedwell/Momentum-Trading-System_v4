import math
import pytest
from discovery.competitive_ga.manager_evolution_v1 import population,pareto,offspring


def test_two_observed_objectives_are_accepted():
    a,b=population(2,seed=4)
    scored=[(a,(.1,-.2)),(b,(.08,-.3))]
    assert pareto(scored)==[scored[0]]
    assert len(offspring(scored,n=12,seed=2))==12


def test_mixed_objective_dimensions_rejected():
    a,b=population(2,seed=4)
    with pytest.raises(ValueError):pareto([(a,(.1,-.2)),(b,(.1,-.2,.3,.4))])


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),float('-inf')])
def test_nonfinite_fitness_rejected(bad):
    a=population(1)[0]
    with pytest.raises(ValueError):pareto([(a,(bad,-.1))])

"""No unsupported manager defunding even if a callback requests it."""
import pytest
from discovery.competitive_ga.capital_competition import Opportunity,compare

def test_costs_and_margin_protect_incumbent():
    incumbent=Opportunity(('HORIZONS','h'),'AAA',.08,.01,.0)
    costly=Opportunity(('GA7','g'),'BBB',.12,.02,.05)
    assert compare(incumbent,[costly],held_weight=.10,free_weight=0,required_weight=.10) is None
    near=Opportunity(('GA7','g'),'BBB',.09,.01,.0)
    assert compare(incumbent,[near],held_weight=.10,free_weight=0,required_weight=.10,margin=.02) is None

def test_nonfinite_capital_rejected():
    incumbent=Opportunity(('HORIZONS','h'),'AAA',.08,.01,0)
    with pytest.raises(ValueError):
        compare(incumbent,[],held_weight=.1,free_weight=float('nan'))

def test_zero_incumbent_rejected():
    incumbent=Opportunity(('HORIZONS','h'),'AAA',.08,.01,0)
    with pytest.raises(ValueError):
        compare(incumbent,[],held_weight=0,free_weight=0)

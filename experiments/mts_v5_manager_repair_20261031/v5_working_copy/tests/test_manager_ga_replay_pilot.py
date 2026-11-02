import pytest
from discovery.competitive_ga.manager_ga_replay_pilot import run


def test_bounded_pilot_evolves_from_observed_fitness():
    calls=[]
    def evaluator(genes,*,start_date,end_date):
        calls.append((genes.min_edge,start_date,end_date))
        value=genes.min_edge
        return {'fills':2,'sessions':8},(value,-value/2)
    result=run(size=3,generations=2,evaluator=evaluator)
    assert result['status']=='RESEARCH_ONLY_GA6_ENTRY_CAP_AND_EXIT_OVERRIDE'
    assert len(calls)==6
    assert len(result['history'])==2
    assert all(len(x['evaluations'])==3 for x in result['history'])
    assert result['history'][0]['evaluations'][0]['fitness'][0]==calls[0][0]


@pytest.mark.parametrize('size,generations',[(1,1),(17,1),(2,0),(2,6)])
def test_rejects_unbounded_pilot(size,generations):
    with pytest.raises(ValueError):run(size=size,generations=generations)

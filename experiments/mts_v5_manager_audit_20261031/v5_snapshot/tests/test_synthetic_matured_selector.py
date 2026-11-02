from discovery.competitive_ga.synthetic_matured_selector import MaturedSelector

def test_only_previous_session_closed_outcomes_can_rank():
    s=MaturedSelector(min_samples=1)
    entries=[('a',.1),('b',.1)]
    s.close(4,'a',.3)
    s.close(4,'b',-.2)
    s.mature(4)
    assert not s.outcomes
    s.mature(5)
    assert s.select(entries,'XYZ',5)[0]=='a'

def test_no_outcomes_is_deterministic():
    s=MaturedSelector()
    assert s.select([('b',.1),('a',.1)],'ABC',2)==s.select([('a',.1),('b',.1)],'ABC',2)

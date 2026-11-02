from discovery.competitive_ga.defense_replay_adapter import make_defense_callback

def test_b1_trigger_and_r1_recovery_are_criteria_driven():
    def criteria(date):
        i=int(date[-2:])
        return dict(A=False,B=False,B1=(i==3),C=False,R1_evidence=(i>=4))
    callback=make_defense_callback(criteria)
    states=[callback(f'2026-01-{i:02d}') for i in range(1,9)]
    assert states==[False,False,True,True,True,False,False,False]

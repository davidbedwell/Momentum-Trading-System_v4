from discovery.competitive_ga.multiregime_gate_trial import run

def test_six_scenarios_replay_with_and_without_abstention():
    result=run()
    assert len(result['scenarios'])==6
    for name,rows in result['scenarios'].items():
        assert len(rows)==6
        assert rows['None']['no_entry']<=rows['0.0']['no_entry']
        assert rows['0.0']['mdd']<=rows['None']['mdd']
    assert result['scenarios']['down_recovery']['0.0']['ga7_entries']>0
    assert result['scenarios']['steady_up']['0.0']['return']==result['scenarios']['steady_up']['None']['return']

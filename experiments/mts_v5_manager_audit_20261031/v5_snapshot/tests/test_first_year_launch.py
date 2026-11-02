from discovery.competitive_ga.first_year_launch import preflight


def test_preflight_never_claims_full_launch_from_component_readability():
    result=preflight()
    assert result['status']=='BLOCKED_NOT_LAUNCH_READY'
    assert result['full_experiment_started'] is False
    assert any('VIX' in b for b in result['blockers'])
    assert set(result['sources'])>={'ga6_chromosomes','ga4_feature_factory','legacy_chromosomes'}
    assert result['catalogues']['ga6_chromosomes']['chromosomes']>0

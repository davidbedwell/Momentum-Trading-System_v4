"""Contract fixtures test validation, not synthetic research evidence."""
import pandas as pd
import numpy as np
import pytest
from discovery.competitive_ga.first_year_manifest import Calendar, validate_panel, eligibility, audit_contracts, manifest, digest
from discovery.competitive_ga.first_year_parity import compare, feature_eligibility

T = tuple(f'T{i:03}' for i in range(500))
D = ('2026-01-02','2026-01-05','2026-01-06','2026-01-07')
C = Calendar(D,D[0],D[2],D[3])


def panel():
    return pd.DataFrame([(d,t,1.) for d in D[:2] for t in T], columns=['date','ticker','f'])


def gates():
    return pd.DataFrame([dict(date=D[1],ticker=t,available_at=D[1]+'T20:00:00Z',
        source_hash='fixture',security_id=t,earnings_contract='selected-native-fixture',
        member=True,earnings_clear=True,risk_clear=True,corporate_actions_verified=True,
        niche='NON_NICHE',niche_trained_through=D[0],niche_source_hash='fixture') for t in T])


def gate(rows, family='GA7'):
    return eligibility(rows,decision_date=D[1],tickers=T,family=family,decision_at=D[1]+'T21:00:00Z')


def test_complete_500_prefix_and_proof_seal():
    validate_panel(panel(),calendar=C,as_of=D[1],tickers=T)
    with pytest.raises(ValueError,match='sealed proof'):
        validate_panel(panel(),calendar=C,as_of=D[3],tickers=T)


@pytest.mark.parametrize('kind', ['missing','duplicate','future','foreign','small'])
def test_panel_rejects_incomplete_daily_universe(kind):
    p=panel()
    if kind=='missing':p=p.iloc[1:]
    if kind=='duplicate':p=pd.concat([p,p.iloc[:1]])
    if kind=='future':p.loc[0,'date']=D[2]
    if kind=='foreign':p.loc[0,'ticker']='unknown'
    with pytest.raises(ValueError):
        validate_panel(p,calendar=C,as_of=D[1],tickers=T[:499] if kind=='small' else T)


@pytest.mark.parametrize('field,value', [('member',False),('earnings_clear',False),('risk_clear',False),('corporate_actions_verified',False)])
def test_each_native_gate_blocks_entry(field,value):
    g=gates();g.loc[0,field]=value
    result=gate(g)
    assert not result[T[0]] and sum(result.values())==499


@pytest.mark.parametrize('kind', ['future','timestamp_missing','string_flag','missing_earnings','niche_future','niche_missing','coverage'])
def test_gate_fails_closed(kind):
    g=gates()
    if kind=='future':g.loc[0,'available_at']=D[1]+'T22:00:00Z'
    if kind=='timestamp_missing':g.loc[0,'available_at']=None
    if kind=='string_flag':g['member']=g.member.astype(object);g.loc[0,'member']='false'
    if kind=='missing_earnings':g=g.drop(columns='earnings_contract')
    if kind=='niche_future':g.loc[0,'niche_trained_through']=D[1]
    if kind=='niche_missing':g=g.drop(columns='niche')
    if kind=='coverage':g=g.iloc[1:]
    with pytest.raises(ValueError):gate(g)


def test_dates_and_partition_reject_ambiguity():
    for dates in (D[::-1],D+D[:1]):
        with pytest.raises(ValueError):Calendar(dates,D[0],D[2],D[3])
    with pytest.raises(ValueError):Calendar(D,D[2],D[0],D[3])
    p=panel();p.loc[0,'date']='2026-01-02T00:00:00'
    with pytest.raises(ValueError):validate_panel(p,calendar=C,as_of=D[1],tickers=T)


def test_parity_checks_nan_masks_values_and_all_500_names():
    a=panel();a.loc[0,'f']=np.nan
    stats=compare(a,a.copy(),columns=['f'],calendar=C,as_of=D[1],tickers=T)
    assert stats['warmup_values']==1 and stats['rows']==1000
    for value in (0.,np.inf):
        b=a.copy();b.loc[0,'f']=value
        with pytest.raises(ValueError):compare(a,b,columns=['f'],calendar=C,as_of=D[1],tickers=T)
    b=a.copy();b.loc[900,'f']=2
    with pytest.raises(ValueError):compare(a,b,columns=['f'],calendar=C,as_of=D[1],tickers=T)


def test_feature_warmup_does_not_override_entry_gates():
    p=panel().iloc[500:].copy();p.loc[500,'f']=np.nan
    g=dict.fromkeys(T,True);g[T[1]]=False
    e=feature_eligibility(p,['f'],g)
    assert sum(e.values())==498
    with pytest.raises(ValueError):feature_eligibility(p,['missing'],g)


def test_contracts_do_not_certify_historical_stress_or_exit_horizon():
    contracts={f:dict(source_hash='x',snapshot_hash='y',trained_through=D[0],
        feature_contract='x',eligibility_contract='y') for f in ('GA4','HORIZONS','GA6','GA7')}
    contracts['GA4']['horizon']=63
    contracts['HORIZONS']['stress_scenario_hash']='historical'
    blockers=audit_contracts(contracts,decision_date=D[1],scenario_hash='fictional')
    assert len(blockers)==2 and 'exit' in blockers[0] and 'stress' in blockers[1]
    assert any('cutoff' in b for b in audit_contracts(contracts,decision_date=D[0],scenario_hash='fictional'))


def test_manifest_inventories_every_day_and_blocks_missing_gates(tmp_path):
    source=tmp_path/'bars';source.write_text('contract fixture')
    sources=[dict(path=str(source),sha256=digest(source),role='synthetic_bars')]
    m=manifest(panel(),calendar=C,as_of=D[1],tickers=T,sources=sources,
        contracts={},gate_rows={},decision_times={})
    assert m['status']=='BLOCKED' and not m['proof_opened']
    assert len(m['daily'])==2 and m['daily'][0]['next_open']==D[1]
    assert all(v is None for d in m['daily'] for v in d['eligible'].values())
    source.write_text('changed')
    with pytest.raises(ValueError,match='digest'):manifest(panel(),calendar=C,as_of=D[1],tickers=T,sources=sources,contracts={},gate_rows={},decision_times={})


def test_daily_feed_checks_seal_and_missing_contracts_before_io():
    from discovery.competitive_ga.first_year_daily_feed import DailyFeed
    calls=[]
    feed=DailyFeed(calendar=C,tickers=T,contracts={},scenario_hash='fixture',loader=lambda **kw:calls.append(kw))
    with pytest.raises(ValueError,match='sealed proof'):feed.at_close(D[3],decision_at=None,gates={},requirements={})
    with pytest.raises(ValueError,match='blocked native'):feed.at_close(D[1],decision_at=None,gates={},requirements={})
    assert calls==[]


def test_ga7_gate_does_not_coerce_string_false():
    from discovery.competitive_ga.archived_genomes import ga7_bars
    with pytest.raises(ValueError,match='booleans'):
        ga7_bars(pd.DataFrame([dict(date=D[0],ticker='A',close=1,f=1)]),
                 decision_date=D[0],eligibility={'A':'false'},columns=['f'])


def test_daily_feed_full_family_controls_and_warmup(monkeypatch):
    from discovery.competitive_ga.first_year_daily_feed import DailyFeed
    # Explicit test contract assertions: no launch or source certification claim.
    contracts={f:dict(source_hash='fixture',snapshot_hash='fixture',trained_through='2025-12-31',
        feature_contract='fixture',eligibility_contract='fixture') for f in ('GA4','HORIZONS','GA6','GA7')}
    contracts['GA4']['exit_archive_link']='fixture'
    contracts['HORIZONS'].update(stress_scenario_hash='fixture',stress_mapping_provenance='fixture',stress_availability_contract='fixture')
    calls=[]
    def loader(*,as_of):
        calls.append(as_of)
        return {f:panel() for f in contracts}
    feed=DailyFeed(calendar=C,tickers=T,contracts=contracts,scenario_hash='fixture',loader=loader)
    gs={f:gates() for f in contracts}
    for g in gs.values():g.loc[0,'earnings_clear']=False
    result=feed.at_close(D[1],decision_at=D[1]+'T21:00:00Z',gates=gs,requirements={f:['f'] for f in contracts})
    assert calls==[D[1]] and all(sum(p.eligible)==499 for p in result.values())
    with pytest.raises(ValueError,match='skip, repeat'):feed.at_close(D[1],decision_at=None,gates=gs,requirements={})


@pytest.mark.parametrize('contract', [{},dict(kind='historical',scenario_hash='synthetic'),dict(kind='joint_synthetic_scenario',scenario_hash='different')])
def test_horizons_rejects_unlinked_stress_before_feature_calculation(contract):
    from discovery.competitive_ga.first_year_horizons import build
    with pytest.raises(ValueError,match='historical date overlap'):
        build(pd.DataFrame(),pd.DataFrame(),scenario_hash='synthetic',contract=contract,decision_times={})


def test_daily_snapshot_hash_detects_price_changes_and_ignores_row_order(tmp_path):
    source=tmp_path/'source';source.write_text('fixture')
    kwargs=dict(calendar=C,as_of=D[1],tickers=T,sources=[dict(path=str(source),sha256=digest(source),role='synthetic_bars')],contracts={},gate_rows={},decision_times={})
    a=manifest(panel(),**kwargs)
    b=manifest(panel().iloc[::-1],**kwargs)
    assert [r['input_snapshot_sha256'] for r in a['daily']]==[r['input_snapshot_sha256'] for r in b['daily']]
    changed=panel();changed.loc[0,'f']=2
    c=manifest(changed,**kwargs)
    assert a['daily'][0]['input_snapshot_sha256']!=c['daily'][0]['input_snapshot_sha256']
    assert a['daily'][1]['input_snapshot_sha256']==c['daily'][1]['input_snapshot_sha256']


def test_ga7_niche_group_filters_entries_and_drives_native_signal_decay():
    from types import SimpleNamespace
    from discovery.competitive_ga.ga7_native_daily_producer import produce
    g=SimpleNamespace(operator='AND',feature_a='a',feature_b='b',threshold_a=0,threshold_b=0,
        entry_pct=.1,stop_pct=.02,exit_rule='signal_decay',identity=lambda:'g')
    bars={t:dict(eligible=True,close=100,controlling_niche=n,features=dict(a=.8,b=.8)) for t,n in [('A','N1'),('B','N2')]}
    kwargs=dict(decision_date=D[1],trained_through=D[0],source_hash='fixture',snapshot_hash='fixture',niche_group='N1')
    assert [p.ticker for p in produce(g,bars,**kwargs)]==['A']
    held={'B':dict(entry=100,weight=.1)}
    assert [(p.ticker,p.action) for p in produce(g,bars,held=held,**kwargs)]==[('A','ENTER'),('B','EXIT')]
    del bars['B']['controlling_niche']
    with pytest.raises(ValueError,match='controlling niche'):produce(g,bars,held=held,**kwargs)


def test_ga4_build_rejects_partial_non_smoke_universe_before_native_import(monkeypatch):
    from discovery.competitive_ga.first_year_features import build
    raw=pd.DataFrame([dict(Date=pd.Timestamp(D[0]),Ticker='A',Open=1,High=1,Low=1,Close=1,Volume=1,Sector='X')])
    monkeypatch.setattr(pd,'read_parquet',lambda *a,**kw:raw)
    with pytest.raises(ValueError,match='exactly 500'):build(as_of=D[0])
    with pytest.raises(ValueError,match='incomplete daily'):build(as_of=D[0],smoke_tickers=['A','B'])


@pytest.mark.parametrize('kind',['nan_niche','duplicate_security','compact_date'])
def test_ambiguous_identity_and_niche_metadata_fail_closed(kind):
    g=gates()
    if kind=='nan_niche':g.loc[0,'niche_source_hash']=None
    if kind=='duplicate_security':g.loc[0,'security_id']=g.loc[1,'security_id']
    if kind=='compact_date':g.loc[0,'date']='20260105'
    with pytest.raises(ValueError):gate(g)

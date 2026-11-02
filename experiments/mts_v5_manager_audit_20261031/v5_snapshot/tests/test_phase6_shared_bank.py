"""Bounded end-to-end fixtures. Prices, risks and outcomes are test inputs only."""
from types import SimpleNamespace
import pytest
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.ga6_native_daily_producer import produce as ga6
from discovery.competitive_ga.ga7_native_daily_producer import produce as ga7
from discovery.competitive_ga.causal_calibration import TradeOutcome
from engines.portfolio_replay.kernel import Bar
from engines.portfolio_replay.risk import RiskSnapshot


def scenario(*, missing_reference=False, missing_held_features=False, stale_risk=False):
    dates=[f'2020-01-{i+2:02d}' for i in range(8)]
    seen=[]
    g=SimpleNamespace(operator='AND',entry_pct=.08,feature_a='a',feature_b='b',
                      threshold_a=0.,threshold_b=0.,stop_pct=.02,exit_rule='signal_decay')
    def native(date,i,bars,holdings,owners,defense,book):
        held={t:dict(shares=p.shares,entry=p.entry,peak=p.peak,
              entry_session=p.entry_session,weight=holdings[t]) for t,p in book.positions.items()}
        provenance=dict(decision_date=date,trained_through='2019-12-31',
                        source_hash='fixture-source',snapshot_hash=f'fixture-{i}')
        def evaluate(candidate,row,state,session):
            if state is None:return ('ENTER',.08) if i<5 else ('NO_ENTRY',0.)
            return ('ADD',.03) if i==3 else (('REDUCE',.5) if i==4 else ('EXIT',0.))
        proposals=ga6(object(),{'A':{'eligible':True}},session=i,chromosome_id='c6',
            held={t:p for t,p in held.items() if t=='A'},evaluator=evaluate,**provenance)
        strength=.4 if i==4 else (.1 if i>=5 else .9)
        features={} if missing_held_features and i==4 else {'a':strength,'b':strength}
        proposals+=ga7(g,{'B':dict(close=bars['B'].close,eligible=True,features=features)},
            chromosome_id='c7',held={t:p for t,p in held.items() if t=='B'},**provenance)
        seen.extend((i,p.family,p.action) for p in proposals)
        return proposals
    risks=[]
    def risk(date,i,bars,holdings):
        risks.append((date,i,dict(holdings)))
        return RiskSnapshot('2019-12-31' if stale_risk else date,
            {t:(.02,.03,t) for t in bars},reference_close={t:b.close for t,b in bars.items()
                if not (missing_reference and t=='B')})
    days=[]
    for i,date in enumerate(dates):
        close=104. if i==3 else 100.
        outcomes=[TradeOutcome(c,(f+'_ENTRY',),0,1,.1,'shadow')
                  for f,c in [('GA6','c6'),('GA7','c7')]] if i==1 else []
        days.append((date,{t:Bar(100.,close) for t in 'AB'},native,outcomes,False))
    return run(days,min_samples=1,settlement_sessions=1,max_sessions=8,
               stops_by_owner={('GA7','c7'):.02},risk_provider=risk),seen,risks


def test_two_families_share_one_bank_held_actions_and_add_evidence_gate():
    result,seen,risks=scenario()
    buys=[f for f in result['ledger'] if f[2]=='BUY']
    assert {(f[0],f[1]) for f in buys}=={('2020-01-05','A'),('2020-01-05','B')}
    assert {(f,a) for i,f,a in seen if i==3}=={('GA6','ADD'),('GA7','ADD')}
    # Positive entry outcomes cannot fund ADD; native REDUCE/EXIT bypass ranking.
    assert any(f[2]=='SELL' and f[0]=='2020-01-07' for f in result['ledger'])
    assert any(f[2]=='SELL' and f[0]=='2020-01-08' for f in result['ledger'])
    assert len(risks)==8
    assert max(abs(r['owner_residual']) for r in result['reconciliation'])<1e-7
    assert all(r['settled_cash']>=0 for r in result['reconciliation'])
    assert {owner[0] for r in result['reconciliation'] for owner in r['owner_pnl']}=={'GA6','GA7'}


def test_missing_dated_risk_reference_blocks_only_uncovered_new_name():
    result,_,_=scenario(missing_reference=True)
    assert not any(f[1]=='B' and f[2]=='BUY' for f in result['ledger'])
    assert any(f[1]=='A' and f[2]=='BUY' for f in result['ledger'])
    assert any(('B','missing risk/reference') in events for _,events,*rest in result['risk_audit'])


def test_held_feature_coverage_and_close_date_fail_closed():
    with pytest.raises(ValueError,match='missing native GA7 features'):
        scenario(missing_held_features=True)
    with pytest.raises(ValueError,match='current close risk snapshot'):
        scenario(stale_risk=True)

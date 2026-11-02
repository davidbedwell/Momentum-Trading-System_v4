from types import SimpleNamespace
import pytest
from discovery.competitive_ga.ga6_native_daily_producer import produce
from discovery.competitive_ga.shadow_accounting_v2 import ShadowLedger
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

DATE='2026-01-12'
META=dict(decision_date=DATE,session=4,chromosome_id='c',
          trained_through='2026-01-01',source_hash='s',snapshot_hash='h')

@pytest.mark.parametrize('action,amount,expected',[
    ('ADD',.03,.13),('REDUCE',.7,.07),('HOLD',0,.1),('EXIT',0,0)])
def test_ga6_native_amount_semantics(action,amount,expected):
    held={'A':dict(entry=100,peak=110,shares=5,entry_session=1,weight=.1)}
    def evaluate(candidate,row,state,session):
        assert state.entry_price==100 and session-state.entry_session==3
        return action,amount
    p=produce(None,{'A':{'close':105}},held=held,evaluator=evaluate,**META)[0]
    assert p.target_weight==pytest.approx(expected)


def proposal(action, date=DATE, cid='c'):
    return NativeProposal(date,'A','GA6',cid,action,.1 if action=='ENTER' else 0,
                          0,'entry_equity_fraction','s','h','2026-01-01')


def test_independent_rejected_shadow_gets_exit_and_matures():
    book=ShadowLedger()
    seen=[]
    def shadow(date,session,bars,defense,ledger):
        states=ledger.native_states(bars)
        seen.append(states)
        return [proposal('ENTER' if session==0 else 'EXIT',date)]
    dates=['2026-01-12','2026-01-13','2026-01-14']
    result=run([(d,{'A':Bar(100,100)},[],[],False) for d in dates],
               shadow_book=book,shadow_native=shadow)
    assert result['ledger']==[] and result['shadow_completed']==1
    assert seen[1][('GA6','c')]['A']['entry_session']==1
    assert result['matured_outcomes']==1


def test_raw_entry_separate_from_fee_basis():
    from discovery.competitive_ga.position_fill_book import FillBook
    book=FillBook()
    book.apply((DATE,'A','BUY',10,100,10),('GA7','c'),.02,session=5)
    book.apply((DATE,'A','BUY',10,110,10),('GA7','c'))
    p=book.positions['A']
    assert p.entry==105 and p.basis==106 and p.entry_session==5


def test_defense_close_does_not_cancel_prior_open_fill():
    from discovery.competitive_ga.causal_calibration import TradeOutcome
    dates=['2026-01-12','2026-01-13','2026-01-14','2026-01-15','2026-01-16']
    days=[]
    for i,d in enumerate(dates):
        outcomes=[TradeOutcome('c',('GA6_ENTRY',),0,1,.1,'shadow')] if i==1 else []
        days.append((d,{'A':Bar(100,100)},[proposal('ENTER',d)] if i==2 else [],outcomes,i==3))
    result=run(days,min_samples=1)
    assert [(f[0],f[2]) for f in result['ledger']]==[(dates[3],'BUY'),(dates[4],'SELL')]


def test_stress_sparse_dates_keep_prior_observation(tmp_path):
    import pandas as pd
    from discovery.competitive_ga.horizons_external_stress import load
    (tmp_path/'CrashMultiMarketV1').mkdir()
    (tmp_path/'CrashCausalPackV1').mkdir()
    dates=pd.bdate_range('2026-01-01',periods=6)
    pd.DataFrame({'DATE':dates.strftime('%m/%d/%Y'),'CLOSE':range(10,16)}).to_csv(tmp_path/'CrashMultiMarketV1/VIX_History.csv',index=False)
    pd.DataFrame({'DATE':dates.strftime('%m/%d/%Y'),'VVIX':range(20,26)}).to_csv(tmp_path/'CrashMultiMarketV1/VVIX_History.csv',index=False)
    pd.DataFrame({'Date':dates,'Funding':range(6),'Credit':range(10,16)}).to_csv(tmp_path/'CrashCausalPackV1/ofr_fsi_raw_20261004.csv',index=False)
    result,meta=load(['2026-01-06','2026-01-08','2026-02-01'],root=tmp_path)
    assert result.vix.tolist()==[13,15]
    assert result.funding.tolist()==[1,3]
    assert meta['excluded_dates']==1


def test_ga4_horizon_cannot_silently_become_exit():
    from discovery.competitive_ga.ga4_native_daily_producer import produce as ga4
    with pytest.raises(ValueError,match='horizon is not an exit'):
        ga4(None,[],decision_date=DATE,chromosome_id='ga4',trained_through=DATE,
            source_hash='s',snapshot_hash='h',held={'A':{'weight':.1}})


def test_shadow_orchestrator_separates_same_ticker_owners():
    from discovery.competitive_ga.native_four_family_orchestrator import produce as four
    genome=SimpleNamespace(operator='AND',entry_pct=.1,feature_a='a',feature_b='b',
        threshold_a=0.,threshold_b=0.,stop_pct=.02,exit_rule='reversal')
    states={('GA7','one'):{'A':dict(entry=100,weight=.1)},
            ('GA7','two'):{'A':dict(entry=90,weight=.1)}}
    result=four(DATE,trained_through='2026-01-01',source_hash='s',snapshot_hash='h',
        ga7_specs=[{'id':cid,'genome':genome} for cid in ('one','two')],
        ga7_bars={'A':dict(close=99,eligible=True,features={'a':.9,'b':.9})},
        held_by_owner=states)
    assert [(p.chromosome_id,p.action) for p in result]==[('one','EXIT'),('two','ADD')]

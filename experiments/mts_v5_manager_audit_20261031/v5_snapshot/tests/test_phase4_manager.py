"""Labeled contract/accounting fixtures; these are never launch evidence."""
from types import SimpleNamespace
import pandas as pd
import pytest
from engines.portfolio_replay.kernel import Replay, Bar, Signal
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.first_year_manifest import Calendar, FAMILIES
from discovery.competitive_ga.first_year_daily_feed import DailyFeed
from discovery.competitive_ga.first_year_manager import bounded_replay
from discovery.competitive_ga.native_signal_contract import NativeProposal


@pytest.mark.parametrize('lag', [1, 2])
def test_shared_settlement_and_equity_include_receivable(lag):
    r = Replay(cash=100., fees=0., cap=1., settlement_sessions=lag)
    r.pending = [Signal('A','GA6','c',1.)]
    r.day('d0', {'A':Bar(10,10)})
    r.pending = [Signal('A','GA6','c',0.), Signal('B','GA6','c',1.)]
    r.day('d1', {'A':Bar(10,10),'B':Bar(10,10)})
    assert r.cash == 0 and r.nav[-1][1] == 100 and not r.shares
    assert r.unsettled == [(1+lag,100.)]
    for i in range(2, 2+lag):
        r.pending = [Signal('B','GA6','c',1.)]
        r.day('d'+str(i), {'B':Bar(10,10)})
        if i < 1+lag:
            assert not r.shares
    assert r.shares == {'B':10.} and r.unsettled == []


def test_owner_reconciliation_includes_split_dividend_and_fee():
    dates = ('2026-01-02','2026-01-05','2026-01-06','2026-01-07','2026-01-08')
    def proposal(date, action):
        return NativeProposal(date,'A','GA6','c',action,.1 if action=='ENTER' else 0.,
            0.,'entry_equity_fraction','fixture','fixture','2025-12-31')
    from discovery.competitive_ga.causal_calibration import TradeOutcome
    days=[]
    for i,date in enumerate(dates):
        bar=Bar(50,50,.5,2) if i==3 else Bar(100 if i<3 else 50,100 if i<3 else 50)
        native=[proposal(date, 'ENTER')] if i==1 else ([proposal(date,'EXIT')] if i==3 else [])
        outcome=[TradeOutcome('c',('GA6_ENTRY',),-1,0,.1,'shadow')] if i==0 else []
        days.append((date,{'A':bar},native,outcome,False))
    result=run(days,min_samples=1,settlement_sessions=2,max_sessions=5)
    assert [f[2] for f in result['ledger']] == ['BUY','SELL']
    assert result['reconciliation'][3]['owner_pnl'][('GA6','c')] == pytest.approx(90.)
    assert result['reconciliation'][4]['receivable'] > 0
    assert all(abs(d['owner_residual']) < 1e-7 for d in result['reconciliation'])
    assert result['reconciliation'][-1]['nav'] == pytest.approx(100080.)


T=tuple(f'T{i:03}' for i in range(500))
D=tuple(pd.bdate_range('2026-01-02',periods=9).strftime('%Y-%m-%d'))
C=Calendar(D,D[5],D[7],D[8])


def fixture_feed():
    contracts={f:dict(source_hash='fixture',snapshot_hash='fixture',trained_through='2025-12-31',
        feature_contract='fixture',eligibility_contract='fixture') for f in FAMILIES}
    contracts['GA4']['exit_archive_link']='fixture'
    contracts['HORIZONS'].update(stress_scenario_hash='fixture',stress_mapping_provenance='fixture',stress_availability_contract='fixture')
    def loader(*,as_of):
        p=pd.DataFrame([(d,t,1.,100.) for d in D if d<=as_of for t in T],columns=['date','ticker','f','close'])
        return {f:p.copy() for f in FAMILIES}
    return DailyFeed(calendar=C,tickers=T,contracts=contracts,scenario_hash='fixture',loader=loader)


def control(date):
    g=pd.DataFrame([dict(date=date,ticker=t,security_id=t,source_hash='fixture',
        available_at=date+'T20:00:00Z',earnings_contract='fixture',member=True,
        earnings_clear=True,risk_clear=True,corporate_actions_verified=True,niche='NON_NICHE',
        niche_trained_through='2025-12-31',niche_source_hash='fixture') for t in T])
    return dict(decision_at=date+'T21:00:00Z',gates={f:g.copy() for f in FAMILIES},defense=date==D[4])


def kwargs(feed):
    def settings(date,panels):
        return dict(snapshot_hash='fixture',ga4_specs=[{}],horizons_specs=[{}],ga6_specs=[{}],ga7_specs=[{}],
            ga4_compiler='fixture',horizons_panel='fixture')
    return dict(feed=feed,dates=D[:7],controls=control,requirements={f:['f'] for f in FAMILIES},
        market_loader=lambda **kw:{t:Bar(105 if kw['as_of'] in (D[2],D[3]) else 100,
                                     105 if kw['as_of'] in (D[2],D[3]) else 100) for t in T},
        settings_loader=settings,owners=[('GA7','fixture')],stops_by_owner={('GA7','fixture'):.02},ga7_columns=['f'],min_samples=1)


def test_integrated_feed_bank_rejected_funded_shadow_and_defense(monkeypatch):
    import discovery.competitive_ga.first_year_manager as module
    calls=[]
    def native(date,**kw):
        calls.append((date,kw))
        if 'ga7_specs' not in kw:return []
        held=kw['held_by_owner'].get(('GA7','fixture'),{})
        action='EXIT' if T[0] in held else 'ENTER'
        return [NativeProposal(date,T[0],'GA7','fixture',action,.1 if action=='ENTER' else 0.,
                0.,'net_return_fraction','fixture','fixture','2025-12-31')]
    monkeypatch.setattr(module,'produce',native)
    monkeypatch.setattr(module,'ga7_bars',lambda panel,**kw:{})
    result=bounded_replay(**kwargs(fixture_feed()))
    assert result['native_calls']==dict.fromkeys(FAMILIES,14)
    assert result['shadow_fills'][0][0]==1  # rejected shared-bank entry still funded independently
    assert result['ledger'][0][0]==D[4] and result['ledger'][0][2]=='BUY'
    assert result['ledger'][1][0]==D[5] and result['ledger'][1][2]=='SELL'
    assert any(kw['held_by_owner'] for _,kw in calls)
    assert result['launch_ready'] is False


def test_integrated_authentic_blocker_precedes_market_io():
    feed=fixture_feed();feed.contracts={}
    kw=kwargs(feed)
    kw['market_loader']=lambda **kw:pytest.fail('blocked runner touched market')
    with pytest.raises(ValueError,match='blocked native'):bounded_replay(**kw)


@pytest.mark.parametrize('kind',['proof','gap','oversize'])
def test_integrated_bounds_and_seal_precede_io(kind):
    kw=kwargs(fixture_feed())
    kw['dates']=D[7:9] if kind=='proof' else (D[0],D[2]) if kind=='gap' else D*8
    kw['market_loader']=lambda **kw:pytest.fail('invalid runner touched market')
    with pytest.raises(ValueError):bounded_replay(**kw)


def test_experimental_exit_never_supplies_authentic_archive_link():
    from discovery.competitive_ga.experimental_exit import ExperimentalExit
    from discovery.competitive_ga.first_year_manifest import audit_contracts
    plugin=ExperimentalExit('EXPERIMENTAL_CALLBACK_V1',lambda **kw:{t:'HOLD' for t in kw['held']},'fixture')
    hook=plugin.bind(chromosome_id='c',trained_through='2025-12-31',snapshot_hash='fixture')
    assert hook(D[0],{'A':dict(weight=.1)})[0].action=='HOLD'
    assert any('exit/archive' in b for b in audit_contracts({'GA4':vars(plugin)},decision_date=D[0],scenario_hash='fixture'))
    with pytest.raises(ValueError):ExperimentalExit('APPROVED',lambda **kw:{},'fixture')


def test_integrated_entry_gates_apply_to_every_native_family(monkeypatch):
    import discovery.competitive_ga.first_year_manager as module
    def native(date,**kw):
        family='GA7' if 'ga7_specs' in kw else 'GA4' if 'ga4_specs' in kw else 'GA6' if 'ga6_specs' in kw else 'HORIZONS'
        unit='net_return_fraction' if family=='GA7' else 'entry_equity_fraction' if family=='GA6' else 'native_horizon_score'
        return [NativeProposal(date,T[0],family,'fixture','ENTER',.1,0.,unit,'fixture','fixture','2025-12-31')]
    def blocked(date):
        c=control(date)
        for g in c['gates'].values():g['member']=False
        return c
    monkeypatch.setattr(module,'produce',native)
    monkeypatch.setattr(module,'ga7_bars',lambda panel,**kw:{})
    kw=kwargs(fixture_feed());kw['controls']=blocked
    result=bounded_replay(**kw)
    assert result['shadow_fills']==[] and result['ledger']==[]


def test_independent_shadow_journal_detects_bad_fees_nav_and_split():
    from discovery.competitive_ga.funded_shadow import FundedShadow
    from discovery.competitive_ga.ledger_audit import funded_shadow as audit
    owner=('GA6','fixture');book=FundedShadow([owner],sessions=D[:4],settlement_sessions=2)
    market={D[0]:{'A':Bar(100,100)},D[1]:{'A':Bar(100,100)},
            D[2]:{'A':Bar(50,50,.5,2)},D[3]:{'A':Bar(50,50)}}
    for i,date in enumerate(D[:4]):
        book.open_session(i,market[date])
        action='ENTER' if i==0 else 'EXIT' if i==2 else None
        ps=[] if action is None else [NativeProposal(date,'A',*owner,action,.1 if action=='ENTER' else 0.,0.,'entry_equity_fraction','fixture','fixture','2025-12-31')]
        book.close_session(i,ps)
    kw=dict(owners=[owner],sessions=D[:4],bars=market,fills=book.fills,nav_history=book.nav_history,settlement_sessions=2)
    assert audit(**kw)['max_residual'] < 1e-7
    bad=list(book.fills);f=list(bad[0]);f[-1]+=1;bad[0]=tuple(f)
    with pytest.raises(ValueError,match='fee'):audit(**{**kw,'fills':bad})
    bad_nav=list(book.nav_history);f=list(bad_nav[-1]);f[-1]+=1;bad_nav[-1]=tuple(f)
    with pytest.raises(ValueError,match='ledger mismatch'):audit(**{**kw,'nav_history':bad_nav})
    bad_market={**market,D[2]:{'A':Bar(50,50,.5,1)}}
    with pytest.raises(ValueError,match='ledger mismatch'):audit(**{**kw,'bars':bad_market})


def test_authentic_integrated_runner_rejects_explicit_experimental_exit():
    from discovery.competitive_ga.experimental_exit import ExperimentalExit
    kw=kwargs(fixture_feed());original=kw['settings_loader']
    plugin=ExperimentalExit('EXPERIMENTAL_CALLBACK_V1',lambda **kw:{},'fixture')
    hook=plugin.bind(chromosome_id='fixture',trained_through='2025-12-31',snapshot_hash='fixture')
    def settings(date,panels):
        result=original(date,panels)
        result['ga4_specs']=[dict(exit_producer=hook)]
        return result
    kw['settings_loader']=settings
    with pytest.raises(ValueError,match='experimental GA4 exit'):bounded_replay(**kw)

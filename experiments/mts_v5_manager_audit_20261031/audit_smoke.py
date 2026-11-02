"""Bounded synthetic audit of the unchanged v5 snapshot. No market-data reads."""
import json, sys, pathlib, importlib.util
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'v5_snapshot'))
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar,Replay,Signal
spec=importlib.util.spec_from_file_location('fixture',HERE/'v5_snapshot/tests/test_functional_niche_manager.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
results={}
def metrics(r):
    peak=100000.;mdd=0.
    for _,nav,*_ in r['nav']:
        peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    return dict(final_nav=r['nav'][-1][1],mdd=mdd,fees=sum(f[5] for f in r['ledger']),fills=len(r['ledger']),unsettled=sum(v for _,v in r['unsettled']))
def proposal(c,t,d,h,weight=.1,action=None):
    return NativeProposal(d,t,c.family,c.chromosome_id,action or ('HOLD' if h else 'ENTER'),h['weight'] if h else weight,0.,'net_return_fraction' if c.family=='GA7' else 'entry_equity_fraction','synthetic','synthetic','2025-12-31')
def obs(t,d):return NicheObservation(d,'2025-12-31','synthetic',(('near',.1),('related',.2)))
def run(candidates,days=None,**kwargs):
    return run_slice(days or [('2026-01-01',{'A':Bar(100,100)}),('2026-01-02',{'A':Bar(100,100)})],candidates,classify=obs,eligible=lambda *a:True,native=proposal,**kwargs)
r=fixture.scenario(); results['lifecycle']=metrics(r)
assert [x['selected'][2] for x in r['decisions'][:5]]==['ENTER','HOLD','ADD','REDUCE','EXIT']
assert abs(r['nav'][-1][1]-100000-sum(x['pnl'] for x in r['realized']))<1e-7
# Independent cash+receivable+inventory identity for every fixture day.
cash=100000.;shares={};due=[];closes=[100,100,104,104,97,98]
for i,(date,nav,reported_cash,positions,_) in enumerate(r['nav']):
    cash+=sum(v for day,v in due if day==i);due=[x for x in due if x[0]!=i]
    for d,t,side,q,p,fee in r['ledger']:
        if d!=date:continue
        if side=='BUY':cash-=q*p+fee;shares[t]=shares.get(t,0)+q
        else:due.append((i+1,q*p-fee));shares[t]-=q
    assert abs(cash-reported_cash)<1e-7
    assert abs(cash+sum(v for _,v in due)+sum(q*closes[i] for q in shares.values())-nav)<1e-7
results['independent_reconciliation']='PASS'
# Fallback behavior, positive common-unit EV only.
cs=[Candidate('special','GA7','near',.02),Candidate('related','GA7','related',.02),Candidate('general','GA6',None,.02)]
r=run(cs,conditional_ev=lambda c,*a:.01 if c.chromosome_id=='special' else .9)
assert r['owners']['A']==('GA7','special');results['specialist_priority']='PASS'
r=run(cs,conditional_ev=lambda c,*a:None if c.chromosome_id=='special' else .9)
assert r['owners']['A']==('GA6','general');results['general_fallback']='PASS'
r=run([cs[1]],conditional_ev=lambda *a:.9)
assert not r['ledger'];results['related_niche_fallback']='MISSING: positive-EV related candidate excluded by tier()'
r=run(cs,conditional_ev=lambda *a:0.)
assert not r['ledger'];results['nonpositive_ev_abstention']='PASS'
# Global funding is ticker order even when later ticker has higher EV.
names=[f'A{i:02d}' for i in range(10)]+['ZZZ']
bars={t:Bar(100,100) for t in names}
r=run([cs[0]],days=[('2026-01-01',bars),('2026-01-02',bars)],conditional_ev=lambda c,t,*a:.9 if t=='ZZZ' else .01)
assert 'ZZZ' not in r['owners'];results['global_capital_ranking']={'status':'FAIL','higher_ev_unfunded':'ZZZ','funded':sorted(r['owners']),**metrics(r)}
# No stop execution if callback holds; 10% position can lose >2% equity.
r=run([cs[0]],days=[('2026-01-01',{'A':Bar(100,100)}),('2026-01-02',{'A':Bar(100,100)}),('2026-01-03',{'A':Bar(50,50)})])
assert r['nav'][-1][1]<98000
results['risk_gap_stress']={'status':'FAIL_NOT_GUARANTEED',**metrics(r),'native_action':'HOLD','stop_fraction':.02}
# All-cash return stays zero despite standalone SGOV target policy.
r=run(cs,conditional_ev=lambda *a:0.)
assert r['nav'][-1][1]==100000
results['sgov_integration']='MISSING: no SGOV trades or accrual in run_slice'
# Defense exit next open, but NAV tuple flags never show defense.
days=[(f'2026-01-0{i}',{'A':Bar(100,100)}) for i in range(1,5)]
r=run([cs[0]],days=days,defense_at_close=lambda d:d>='2026-01-02')
assert [f[0] for f in r['ledger']]==['2026-01-02','2026-01-03']
assert all(n[4] is False for n in r['nav'])
results['defense']={'next_open_exit':'PASS','nav_defense_flag':'FAIL always False',**metrics(r)}
# Explicit missing stop metadata is accepted on ordinary kernel entries.
bank=Replay();bank.pending=[Signal('A','GA7','x',.1,stop_distance=.8,gap_risk=.8)]
bank.day('2026-01-02',{'A':Bar(100,100)})
assert abs(bank.shares['A']*100/100000-.1)<1e-9
results['kernel_ordinary_entry_risk']={'status':'FAIL','modeled_equity_risk':.1*.8,'limit':.02}
# Portfolio MDD is observed, not enforced by this manager loop.
crashbars={t:Bar(50,50) for t in names}
r=run([cs[0]],days=[('2026-01-01',bars),('2026-01-02',bars),('2026-01-03',crashbars)])
assert metrics(r)['mdd']>.20
results['portfolio_mdd_guard']={'status':'MISSING: replay continues above 20% MDD',**metrics(r)}
(HERE/'smoke_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))

#!/usr/bin/env python3
"""Bounded SYNTHETIC ONLY harness; no historical/PIT authenticity or native alpha claim."""
import csv
import hashlib
import inspect
import json
import math
import traceback
from datetime import date, timedelta
from pathlib import Path
from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar, Replay, Signal

OUT = Path(__file__).resolve().parent
INITIAL = 100000.
N = 126
COSTS = dict(fees=.0005, spread=.001, slippage=.0003, impact=.0002)
FRICTION = .001
TICKERS = [f'SYN{i:02}' for i in range(10)]

def inputs():
    dates=[]; d=date(2030,1,2)
    while len(dates)<N:
        if d.weekday()<5: dates.append(d.isoformat())
        d+=timedelta(days=1)
    prev={t:80.+4*j for j,t in enumerate(TICKERS)}; days=[]
    for i,d in enumerate(dates):
        bars={}
        for j,t in enumerate(TICKERS):
            gap=.002*math.sin(i*.43+j)
            if i==62: gap-=.08
            op=prev[t]*(1+gap)
            cl=op*math.exp(.00045+.004*math.sin(i*.19+j*.6))
            bars[t]=Bar(op,cl); prev[t]=cl
        days.append((d,bars))
    return dates,days


def metrics(navs, exposures, trades):
    # Initial capital is observed before session zero; N equal session intervals.
    path=[INITIAL]+navs; peak=INITIAL; mdd=0.
    for v in path:
        peak=max(peak,v); mdd=max(mdd,1-v/peak)
    cagr=(navs[-1]/INITIAL)**(252/len(navs))-1
    return dict(final_nav=navs[-1],cagr=cagr,mdd=mdd,calmar=cagr/mdd if mdd else None,
                time_weighted_equity_exposure=sum(exposures)/len(exposures),
                min_exposure=min(exposures),max_exposure=max(exposures),trade_count=trades)


def reconcile(result,days):
    cash=INITIAL; shares={}; due=[]; basis={}; realized=0.; errors=[]; exposures=[]; rows=[]
    fills={d:[] for d,_ in days}
    for f in result['ledger']: fills[f[0]].append(f)
    for i,((d,bars),reported) in enumerate(zip(days,result['nav'])):
        cash+=sum(v for k,v in due if k<=i); due=[(k,v) for k,v in due if k>i]
        for _,t,side,q,p,fee in fills[d]:
            assert abs(p-bars[t].open*(1+FRICTION if side=='BUY' else 1-FRICTION))<1e-8
            assert abs(fee-q*p*COSTS['fees'])<1e-8
            if side=='BUY':
                cost=q*p+fee
                assert cost<=cash+1e-7, 'unsettled sale proceeds spent'
                cash-=cost; shares[t]=shares.get(t,0)+q; basis[t]=basis.get(t,0)+cost
            else:
                old=shares[t]; cost=basis[t]*q/old
                assert q<=old+1e-7
                realized+=q*p-fee-cost; basis[t]-=cost; shares[t]-=q
                due.append((i+1,q*p-fee))
        equity=sum(q*bars[t].close for t,q in shares.items()); receivable=sum(v for _,v in due)
        nav=cash+receivable+equity
        unrealized=equity-sum(basis.values())
        errors.extend([abs(nav-reported[1]),abs(cash-reported[2]),abs(nav-(INITIAL+realized+unrealized))])
        for t in TICKERS: errors.append(abs(shares.get(t,0)-reported[3].get(t,0)))
        assert cash>=-1e-7
        exposures.append(equity/nav)
        rows.append(dict(date=d,nav=nav,settled_cash=cash,unsettled_cash=receivable,equity=equity,exposure=equity/nav))
    errors.extend([abs(realized-sum(x['pnl'] for x in result['realized'])),abs(sum(v for _,v in due)-sum(v for _,v in result['unsettled']))])
    assert max(errors)<1e-6, max(errors)
    return dict(max_absolute_error=max(errors),realized_pnl=realized,unrealized_pnl=unrealized,
                final_settled_cash=cash,final_unsettled_cash=receivable,final_equity=equity),exposures,rows


def scenario(target,dates,days):
    index={d:i for i,d in enumerate(dates)}; signals=[]; evs=[]
    def classify(t,d):
        return NicheObservation(d,'2029-12-31','SYNTHETIC_ONLY_NOT_AUTHENTIC_PIT',(('synthetic',.1),))
    def native(c,t,d,h):
        i=index[d]
        # Scheduled rotations exercise exit/re-entry and deferred sale funding.
        exit_now=i%21==19 or i==N-2
        if h: action='EXIT' if exit_now else 'HOLD'; w=0. if exit_now else h['weight']
        else: action='ENTER'; w=target/len(TICKERS)
        p=NativeProposal(d,t,c.family,c.chromosome_id,action,w,.01,'net_return_fraction',
                         'SYNTHETIC_MANIFEST',f'SYNTHETIC_CLOSE_{d}_{t}','2029-12-31')
        signals.append(p.__dict__)
        return p
    def ev(c,t,d,*args):
        # A declared hypothetical 5-session net-return estimate, not fitted alpha.
        j=TICKERS.index(t); i=index[d]
        value=.012+.0003*((j+i)%10)
        evs.append(dict(date=d,ticker=t,horizon_sessions=5,marginal_net_ev=value,source='SYNTHETIC_ASSUMPTION_AFTER_COST_AND_RISK'))
        return value
    r=run_slice(days,[Candidate('SYNTHETIC_FIXED_NO_GA','GA7','synthetic',.02,.03)],
                classify=classify,eligible=lambda *args:True,native=native,conditional_ev=ev,
                max_sessions=N,max_stocks=10,**COSTS)
    rec,exposures,rows=reconcile(r,days)
    risk=max((a['modeled_equity_loss'] for a in r['risk_audit']),default=0)
    assert risk<=.02+1e-10
    assert all(f[0]>dates[0] for f in r['ledger'])
    name=f'target_{round(target*100)}'
    write_csv(name+'_daily.csv',rows)
    (OUT/(name+'_audit.json')).write_text(json.dumps(dict(signals=signals,synthetic_ev=evs,ledger=r['ledger'],decisions=r['decisions'],risk=r['risk_audit']),indent=2))
    return dict(requested_initial_equity_target=target,permitted_equity_allocation=1.,
                metrics=metrics([x[1] for x in r['nav']],exposures,len(r['ledger'])),reconciliation=rec,
                max_modeled_trade_loss=risk,mdd_policy=r['mdd_policy'],pending_unexecuted=len(r['pending']),
                note='Target applies on entries; HOLD drifts. No forced portfolio rebalance or hard 70% ceiling.')


def benchmark(dates,days):
    # Same information delay: equal dollar purchases at session 1 open, same costs.
    shares={}; cash=INITIAL; navs=[]; exps=[]; rows=[]
    for i,(d,bars) in enumerate(days):
        if i==1:
            budget=INITIAL/len(TICKERS)
            for t in TICKERS: shares[t]=budget/(bars[t].open*(1+FRICTION)*(1+COSTS['fees']))
            cash=0.
        eq=sum(q*bars[t].close for t,q in shares.items()); nav=cash+eq
        navs.append(nav); exps.append(eq/nav); rows.append(dict(date=d,nav=nav,settled_cash=cash,equity=eq,exposure=eq/nav))
    write_csv('benchmark_daily.csv',rows)
    return metrics(navs,exps,10)


def write_csv(name,rows):
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def controls():
    b=Replay(cash=0,shares={'A':1000},high_water=INITIAL,settlement_sessions=1)
    bars={'A':Bar(100,100),'B':Bar(100,100)}
    b.pending=[Signal('A','GA7','x',0),Signal('B','GA7','x',.1,stop_distance=.02,gap_risk=.03)]
    b.day('2030-01-02',bars)
    assert [f[2] for f in b.ledger]==['SELL'] and b.cash==0 and b.unsettled
    b.pending=[Signal('B','GA7','x',.1,stop_distance=.02,gap_risk=.03)]
    b.day('2030-01-03',bars); assert b.ledger[-1][2]=='BUY' and not b.unsettled
    g=Replay(); g.pending=[Signal('A','GA7','x',.1,stop_distance=.8,gap_risk=.8)]
    g.day('2030-01-02',bars); assert g.risk_audit[-1]['allowed']<.1 and g.risk_audit[-1]['modeled_equity_loss']<=.02+1e-12
    h=Replay(cash=20000,shares={'A':800},high_water=INITIAL)
    h.pending=[Signal('B','GA7','x',.1,stop_distance=.02,gap_risk=.03)]
    h.day('2030-01-02',{'A':Bar(50,50),'B':Bar(100,100)})
    assert h.admission_halted and 'B' not in h.shares
    h.pending=[Signal('A','GA7','x',0)]; h.day('2030-01-03',bars)
    assert not h.shares and h.admission_halted
    return dict(t_plus_one_no_same_open_reuse='PASS',mandatory_loss_clipping='PASS',open_gap_mdd_latch_and_exit='PASS',gap_loss_guaranteed=False)


def main():
    dates,days=inputs()
    write_csv('synthetic_prices.csv',[dict(date=d,ticker=t,open=b.open,close=b.close) for d,bars in days for t,b in bars.items()])
    sources={}
    for obj in (run_slice,Replay.day):
        p=Path(inspect.getsourcefile(obj)); assert str(p).startswith('/opt/Momentum-Trading-System_v5-alpha/')
        sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    report=dict(label='SYNTHETIC_ONLY_NOT_HISTORICAL_PERFORMANCE_NOT_AUTHENTIC_PIT',sessions=N,initial_nav=INITIAL,
                source_sha256=sources,costs=COSTS,settlement='T+1; zero cash yield',
                exposure_method='Arithmetic mean of session-close equity/NAV; equally spaced trading-session time weights.',
                annualization='252 sessions/year; includes initial capital before session zero; CAGR is scenario arithmetic, not a forecast.',
                benchmark_method='Same ten assets, capital, sessions, next-open start and buy costs; equal dollars then hold; terminal mark, no liquidation.',
                controls=controls(),scenarios={str(t):scenario(t,dates,days) for t in (.7,1.)},benchmark=benchmark(dates,days),failures=[])
    (OUT/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps(report,indent=2,allow_nan=False))

if __name__=='__main__':
    try: main()
    except Exception:
        (OUT/'FAILURE.txt').write_text(traceback.format_exc()); raise

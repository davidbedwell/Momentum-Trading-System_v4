"""Independent ledger reconstruction, causal execution checks, and policy tests."""
from comparison import *
import tempfile
P=ROOT/'artifacts';m=json.loads((P/'metrics.json').read_text());checks={}
raw=pd.read_parquet(SOURCE,columns=['date','ticker','open','close'],use_threads=False)
raw.date=raw.date.dt.strftime('%Y-%m-%d'); days=sorted(raw.date.unique());nxt=dict(zip(days[:-1],days[1:]))
for mode in m:
    p=P/mode;daily=pd.read_csv(p/'daily.csv');fills=pd.read_csv(p/'fills.csv');positions=pd.read_csv(p/'positions.csv');orders=pd.read_csv(p/'orders.csv')
    assert list(fills.date)==[nxt[d] for d in fills.signal_date]
    joined=fills.merge(raw,on=['date','ticker'],suffixes=('_fill','_raw'),validate='many_to_one')
    assert len(joined)==len(fills) and np.allclose(joined.open_fill,joined.open_raw,rtol=0,atol=1e-8)
    pg={d:x for d,x in positions.groupby('date')};fg={d:x for d,x in fills.groupby('date')}
    cash=INITIAL;due=0.;shares={};err=0.;fee=0.;slip=0.
    for r in daily.itertuples():
        cash+=due;due=0.;bought=False
        for f in fg.get(r.date,pd.DataFrame()).itertuples():
            sign=1 if f.side=='BUY' else -1
            if sign==1:bought=True
            else:assert not bought,'sells must precede buys'
            assert abs(f.price-f.open*(1+sign*SLIP))<1e-7
            assert abs(f.fee-f.notional*FEE)<1e-7
            if sign==1:cash-=f.notional+f.fee
            else:due+=f.notional-f.fee
            shares[f.ticker]=shares.get(f.ticker,0)+sign*f.shares
            fee+=f.fee;slip+=abs(f.price-f.open)*f.shares
        assert cash>=-1e-6 and all(q>=-1e-7 for q in shares.values())
        equity=0.;present=set()
        for pos in pg.get(r.date,pd.DataFrame()).itertuples():
            assert abs(shares[pos.ticker]-pos.shares)<1e-6
            equity+=pos.shares*pos.mark;present.add(pos.ticker)
        assert all(abs(q)<1e-7 or t in present for t,q in shares.items())
        e=max(abs(cash-r.cash),abs(due-r.unsettled),abs(cash+due+equity-r.nav));err=max(err,e);assert e<1e-5
    assert len(daily)==4451 and daily.iloc[0].date=='2009-01-02' and daily.iloc[-1].date=='2026-09-14'
    m[mode]['adverse_slippage_dollars']=slip
    checks[mode]={'independent_cash_nav_max_error':err,'next_global_open_all_fills':True,'sell_before_buy':True,'fees_verified':fee,'no_negative_cash_or_shares':True}
# Original manager must be numerically identical, including every fill and daily value.
old=ROOT.parent/'dev79_minimal_manager_20261101/artifacts/manager'
for name in ['daily','fills','orders','positions','decisions']:
    a=pd.read_csv(old/(name+'.csv'));b=pd.read_csv(P/'manager'/(name+'.csv'))
    pd.testing.assert_frame_equal(a,b[a.columns],check_exact=False,rtol=1e-12,atol=1e-8)
checks['original_manager_parity']='all daily/fill/order/position/decision rows match'
# Prefix/future-mutation invariance of every reconstructed indicator.
n=260;idx=pd.bdate_range('2020-01-01',periods=n);c=pd.DataFrame({'A':100*np.exp(np.arange(n)*.001),'B':100*np.exp(np.arange(n)*.0005)},index=idx)
d=type('Panel',(),{})()
for key,value in dict(close=c,open=c*.999,high=c*1.01,low=c*.99,volume=c*0+1e6).items():setattr(d,key,value.copy())
f=policy_features(d)
for key in ('close','open','high','low','volume'):getattr(d,key).iloc[230:]*=3
for key,v in policy_features(d).items():pd.testing.assert_frame_equal(f[key].iloc[:230],v.iloc[:230])
checks['future_mutation_indicators']='passed'
# Cash sale proceeds cannot fund same-session buys; next settlement releases them.
b=Ledger();b.fill('A',1e9,100);b.fill('A',-b.q['A'],100);assert b.fill('B',100,100) is None;b.settle();assert b.fill('B',100,100) is not None
checks['settlement_synthetic']='passed'
# Controlled missing-open order cancellation on isolated harness.
d.open.iloc[1,0]=np.nan;f=features(d);f.update(policy_features(d));f['close']=d.close
with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
    run('grok_dev79_approx',d,f,Path(tmp),str(idx[0].date()),str(idx[5].date()))
    o=pd.read_csv(Path(tmp)/'orders.csv');assert (o.status=='CANCEL_MISSING_NEXT_OPEN').any()
# Hand checks for active signals, 79-way targets and Claude stop/halt behavior.
f['_state']={};date=idx[220];ts=list(c.columns)
t,r=targets('grok_dev79_approx',0,date,f,ts,{},set(),INITIAL,INITIAL);assert all(abs(v-49000)<1e-8 for v in t.values())
t2,r=targets('grok_dev79_approx',1,idx[221],f,ts,{},set(),INITIAL,INITIAL);assert t2 is None
f['_state']={};t,r=targets('gemini_approx',0,date,f,ts,{},set(),INITIAL,INITIAL);assert len(t)==2 and abs(sum(t.values())-INITIAL)<1e-8
f['_state']={};t,r=targets('claude_approx',0,date,f,ts,{},set(),INITIAL,INITIAL);assert len(t)<=10 and sum(t.values())<=.70*INITIAL and max(t.values())<=.10*INITIAL
f['_state']={'risk_peak':INITIAL};t,r=targets('claude_approx',1,date,f,ts,{},set(),84000,INITIAL);assert t=={} and 'halt' in r
f['_state']={'risk_peak':INITIAL,'stops':{'A':1e6}};t,r=targets('claude_approx',1,date,f,ts,{'A':1},set(),INITIAL,INITIAL);assert 'A' not in t
checks['policy_hand_checks']='passed'
(P/'metrics.json').write_text(json.dumps(m,indent=2));(P/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))

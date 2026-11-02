#!/usr/bin/env python3
"""Exploratory fixed DEV79 universe, price-return only, close decisions/next-open fills."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','ARROW_NUM_THREADS'): os.environ[k]='1'
if hasattr(os,'sched_getaffinity'):
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from trade_accounting import TradeAccount
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
AUDITS=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518')
INITIAL=100000.; FEE=.0005; SLIP=.0005

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def features(d):
    """Only trailing, unfilled observations. Missing sessions invalidate rolling windows."""
    c=d.close; ret=c.pct_change(fill_method=None)
    f={'mom20':c/c.shift(20)-1,'mom63':c/c.shift(63)-1,
       'trend':c/c.rolling(100,min_periods=100).mean()-1,
       'vol20':ret.rolling(20,min_periods=20).std()*np.sqrt(252),
       'volume_ratio20':d.volume/d.volume.rolling(20,min_periods=20).mean(),
       'range20':((d.high-d.low)/c).rolling(20,min_periods=20).mean()}
    f['relative_strength']=f['mom63'].sub(f['mom63'].median(axis=1),axis=0)
    f['score']=.3*f['trend'].rank(axis=1,pct=True)+.3*f['mom63'].rank(axis=1,pct=True)+.2*f['relative_strength'].rank(axis=1,pct=True)-.2*f['vol20'].rank(axis=1,pct=True)
    f['eligible']=(f['trend']>0)&(f['mom20']>0)&(f['mom63']>0)&(f['vol20']<.60)&(f['volume_ratio20']>.25)&(f['range20']<.10)
    return f

class Ledger:
    def __init__(self):
        self.cash=INITIAL;self.due=0.;self.q={};self.mark={};self.accounts={};self.realized=0.;self.fees=0.;self.turnover=0.
    def settle(self): self.cash+=self.due;self.due=0.
    def nav(self,prices):return self.cash+self.due+sum(q*prices[t] for t,q in self.q.items())
    def fill(self,t,delta,op):
        buy=delta>0;p=op*(1+SLIP if buy else 1-SLIP)
        q=min(delta,self.cash/(p*(1+FEE))) if buy else min(-delta,self.q.get(t,0.))
        if q<1e-10:return None
        fee=q*p*FEE; a=self.accounts.setdefault(t,TradeAccount())
        if buy:
            self.cash-=q*p+fee;self.q[t]=self.q.get(t,0)+q;a.buy(q*p+fee,.1)
        else:
            before=a.realized;a.sell(q*p-fee,min(1.,q/self.q[t]));self.realized+=a.realized-before
            self.due+=q*p-fee;self.q[t]-=q
            if self.q[t]<1e-9:del self.q[t]
        self.fees+=fee;self.turnover+=q*op
        assert self.cash>=-1e-7
        return dict(ticker=t,side='BUY' if buy else 'SELL',shares=q,open=op,price=p,fee=fee,notional=q*p)

def targets(mode,i,date,f,ts,held,seen,nav,peak):
    if mode=='buy_hold':return {t:INITIAL/len(ts) for t in ts if t not in seen and pd.notna(f['close'].at[date,t])},'fixed_initial_allocation'
    if mode=='momentum' and i%21:return None,'hold_between_21_session_rebalances'
    if mode=='momentum':
        m=f['mom63'].loc[date];chosen=list(m[m>0].sort_values(ascending=False,kind='stable').head(10).index)
        return {t:nav*.09 for t in chosen},'positive_63_session_momentum_top10'
    row=f['eligible'].loc[date];chosen=list(f['score'].loc[date][row].sort_values(ascending=False,kind='stable').head(10).index)
    # Observable cross-sectional trend breadth and portfolio drawdown throttle exposure.
    breadth=(f['trend'].loc[date].dropna()>0).mean()
    gross=.9 if breadth>=.5 else .45
    if nav/peak-1<-.15:gross=min(gross,.30)
    weights={t:min(.10,.02/max(float(f['vol20'].at[date,t]),.10)) for t in chosen}
    total=sum(weights.values());scale=min(1.,gross/total) if total else 1.
    return {t:nav*w*scale for t,w in weights.items()},f'breadth={breadth:.6f};gross_budget={gross};vol_target=.02;drawdown={nav/peak-1:.6f}'

def run(mode,d,f,out,start,end):
    ts=list(d.close.columns);dates=list(d.close.loc[start:end].index);book=Ledger();pending=[];seen=set();peak=INITIAL;daily=[];positions=[];fills=[];orders=[];decisions=[];stales=[];maxerr=0.
    for i,date in enumerate(dates):
        book.settle();ops=d.open.loc[date].dropna().to_dict();closes=d.close.loc[date].dropna().to_dict()
        openmarks={**book.mark,**ops};open_nav=book.nav(openmarks)
        # Orders carry yesterday's close dollar targets; no next-bar ranking or sizing input.
        work=[]
        for o in pending:
            t=o['ticker'];r={**o,'execution_date':str(date.date())}
            if t not in ops:r['status']='CANCEL_MISSING_NEXT_OPEN';orders.append(r);continue
            delta=o['target_dollars']/ops[t]-book.q.get(t,0.)
            work.append((delta,t,o,r))
        for delta,t,o,r in sorted(work,key=lambda x:(x[0]>0,x[1])):
            if delta>0 and mode!='buy_hold':
                # Open-price cap and cash reserve apply to admission; existing gap/drift can exceed cap.
                equity=sum(q*openmarks[x] for x,q in book.q.items())
                delta=min(delta,max(0.,.10*open_nav-book.q.get(t,0.)*ops[t])/ops[t],max(0.,.90*open_nav-equity)/ops[t])
            fill=book.fill(t,delta,ops[t]) if abs(delta*ops[t])>.01 else None
            r['status']='FILLED_OR_CASH_CLIPPED' if fill else 'NO_FILL';orders.append(r)
            if fill:
                fills.append({**fill,'date':str(date.date()),'signal_date':o['signal_date'],'order_id':o['order_id']})
                if fill['side']=='BUY':seen.add(t)
        book.mark.update(closes)
        for t in book.q:
            if t not in closes:stales.append(dict(date=str(date.date()),ticker=t,mark=book.mark[t],reason='last_observed_close_valuation_only'))
        nav=book.nav(book.mark);peak=max(peak,nav);equity=sum(q*book.mark[t] for t,q in book.q.items())
        unreal=equity-sum(a.open_cost for a in book.accounts.values())
        err=abs(nav-(INITIAL+book.realized+unreal));maxerr=max(maxerr,err)
        assert err<1e-6 and nav>0 and book.cash>=-1e-7
        daily.append(dict(date=str(date.date()),nav=nav,cash=book.cash,unsettled=book.due,equity=equity,exposure=equity/nav,drawdown=1-nav/peak,realized_pnl=book.realized,unrealized_pnl=unreal,reconciliation_error=err))
        for t,q in sorted(book.q.items()):positions.append(dict(date=str(date.date()),ticker=t,shares=q,mark=book.mark[t],value=q*book.mark[t],weight=q*book.mark[t]/nav,stale=t not in closes))
        target,reason=targets(mode,i,date,f,ts,book.q,seen,nav,peak);pending=[]
        for t in ts:
            current=book.q.get(t,0.)*book.mark.get(t,0.)
            desired=current if target is None else target.get(t,current if mode=='buy_hold' else 0.)
            diff=desired-current
            # Daily manager ignores small drift, but always exits deselected holdings.
            trade=abs(diff)>(25. if mode=='buy_hold' else max(25.,.005*nav)) or (desired==0 and current>0)
            if t not in closes:trade=False;why='missing_current_bar'
            else:why=reason
            action=('enter' if current==0 else 'add') if diff>0 else ('exit' if desired==0 else 'reduce')
            if not trade:action='hold' if current else 'abstain'
            decisions.append(dict(date=str(date.date()),ticker=t,action=action,current_dollars=current,target_dollars=desired,reason=why))
            if trade:
                o=dict(order_id=f'{mode}-{i}-{t}',signal_date=str(date.date()),ticker=t,target_dollars=desired,action=action)
                if i<len(dates)-1:pending.append(o)
                else:orders.append({**o,'execution_date':'','status':'UNEXECUTED_END_OF_SAMPLE'})
    out.mkdir(parents=True,exist_ok=True)
    for name,rows in [('daily',daily),('positions',positions),('orders',orders),('fills',fills),('decisions',decisions),('stale_marks',stales)]:
        pd.DataFrame(rows,columns=(['date','ticker','mark','reason'] if name=='stale_marks' else None)).to_csv(out/(name+'.csv'),index=False)
    values=np.array([INITIAL]+[x['nav'] for x in daily]);rets=values[1:]/values[:-1]-1
    years=len(dates)/252;cagr=(values[-1]/INITIAL)**(1/years)-1;mdd=max(x['drawdown'] for x in daily)
    return dict(start=daily[0]['date'],end=daily[-1]['date'],sessions=len(dates),final_nav=values[-1],total_return=values[-1]/INITIAL-1,cagr=cagr,max_drawdown=mdd,calmar=cagr/mdd if mdd else None,annual_vol=float(rets.std(ddof=1)*np.sqrt(252)),sharpe_zero_rf=float(rets.mean()/rets.std(ddof=1)*np.sqrt(252)) if rets.std(ddof=1)>0 else None,fills=len(fills),fees=book.fees,turnover_over_initial=book.turnover/INITIAL,mean_exposure=float(np.mean([r['exposure'] for r in daily])),stale_valuation_rows=len(stales),max_reconciliation_error=maxerr,final_cash=book.cash,final_unsettled=book.due,final_positions=len(book.q),actions=pd.Series([r['action'] for r in decisions]).value_counts().to_dict())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--start',default='2009-01-01');ap.add_argument('--end',default='2026-09-14');args=ap.parse_args()
    cols=['date','ticker','security_id','open','high','low','close','volume','dividends','stock_splits']
    raw=pd.read_parquet(SOURCE,columns=cols,use_threads=False);raw.date=pd.to_datetime(raw.date)
    assert not raw.duplicated(['date','ticker']).any() and raw.ticker.nunique()==79
    assert raw.volume.notna().all() and (raw.volume>=0).all()
    assert np.isfinite(raw[['open','high','low','close']]).all().all()
    assert (raw[['open','high','low','close']]>0).all().all()
    assert (raw.high>=raw[['open','close','low']].max(axis=1)-1e-6).all()
    assert (raw.low<=raw[['open','close','high']].min(axis=1)+1e-6).all()
    d=type('Panel',(),{})()
    for c in cols[3:]:setattr(d,c,raw.pivot(index='date',columns='ticker',values=c).sort_index())
    f=features(d);f['close']=d.close
    output=ROOT/'artifacts';output.mkdir(exist_ok=True)
    audit=pd.concat({k:v.stack(future_stack=True) for k,v in f.items()},axis=1).reset_index();audit=audit[(audit.date>=args.start)&(audit.date<=args.end)];audit.to_csv(output/'features.csv.gz',index=False,compression='gzip')
    provenance=dict(status='EXPLORATORY_FIXED_UNIVERSE_NON_PIT_PRICE_RETURN_ONLY',source=str(SOURCE),sha256=digest(SOURCE),rows=len(raw),tickers=sorted(raw.ticker.unique()),source_date_range=[str(raw.date.min()),str(raw.date.max())],missing_volume=int(raw.volume.isna().sum()),split_events=int((raw.stock_splits>0).sum()),dividend_rows=int((raw.dividends>0).sum()),source_columns_used=cols,learned_features_used=False,source_selection='Raw archive traced by launch_exploratory_79.py; enriched panel volume is a transformed feature and is deliberately not used',costs=dict(fee_bps=5,adverse_slippage_bps=5),settlement='T+1 session scenario throughout, no same-day proceeds reuse; not historical settlement reconstruction',price_basis='split_adjusted per existing 2009-2018 audit; no share split multiplier; later basis not independently vendor certified',dividends='excluded for every arm: payment dates and per-share adjusted basis unverified; price-return only',limitations=['Retrospective survivor universe, not historical membership; no alpha/OOS/certification claim','No independent vendor receipts or as-of publication timestamps; present-day split adjustment may restate history','No sector/earnings/PIT labels or synthetic predictor imported','Missing bar cancels next-open order; held shares marked last observed close and logged; no fabricated fills','No terminal liquidation; final NAV marked close; fractional shares; no taxes/borrow/market impact calibration','Volume gate is current share volume divided by trailing 20-session mean > 0.25; no absolute adjusted-price or dollar-volume threshold; missing volume blocks entries','Equal-weight buy-hold allocates initial capital/79 after first observed close for each ticker; delayed listings retain reserved cash','Risk constraints are sizing/scenario controls, not guarantees; price gaps may breach exposure limits'],reuse='TradeAccount copied unchanged from 20261031 audit snapshot; close/next-open queue, settlement, independent PnL reconciliation adapted from 20261101 synthetic_cash harness accounting only',audits={})
    for name in ['ga6_ga7_dev79_provenance_gate_20261028.md','ga6_ga7_split_basis_dev79_audit_20261028.json']:
        p=AUDITS/name;provenance['audits'][str(p)]=digest(p);(output/name).write_bytes(p.read_bytes())
    (output/'provenance.json').write_text(json.dumps(provenance,indent=2))
    results={mode:run(mode,d,f,output/mode,args.start,args.end) for mode in ['manager','buy_hold','momentum']}
    (output/'metrics.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
if __name__=='__main__':main()

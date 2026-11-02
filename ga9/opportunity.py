"""GA9-A: causal stock opportunity distributions and a GA9-B adapter.

All return fields are fractions, net of 5bp slippage + 1bp fees per side.
Forecast labels use next-open entry and next-open exit after the horizon.
"""
from dataclasses import asdict, dataclass, replace
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, replay, scores

ENTRY = 1.0005 * 1.0001
EXIT = .9995 * .9999
BOUNDARIES = [-1., 0., .5, 1., 2.]


def discovery(close, eligible, top_k=150):
    """Refresh rolling discovery daily; rank is a discovery filter only."""
    c = pd.DataFrame(close)
    parts = [c/c.shift(h)-1 for h in (20, 60, 120)]
    score = sum(x.where(eligible).rank(axis=1, pct=True) for x in parts)/3
    valid = eligible & np.isfinite(score.to_numpy())
    rank = score.where(valid).rank(axis=1, ascending=False, method='first')
    return score.to_numpy(), rank.le(top_k).to_numpy()


def load_synthetic(prices, membership):
    """Read the existing synthetic scenario; rebuild features from raw prices."""
    d = pd.read_parquet(prices)
    m = pd.read_parquet(membership, columns=['date','ticker','eligible','sector_id'])
    d = d.merge(m, on=['date','ticker'], validate='one_to_one')
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(d.date).unique()))
    symbols = sorted(d.ticker.unique())
    def wide(key):
        return d.pivot(index='date',columns='ticker',values=key).reindex(index=dates,columns=symbols)
    c, o, v = wide('close'), wide('open'), wide('volume')
    if not np.isfinite(c).all().all() or not np.isfinite(o).all().all() or (c<=0).any().any() or (o<=0).any().any():
        raise ValueError('Complete positive synthetic execution marks required')
    eligible = wide('eligible').eq(True).to_numpy()
    r = c.pct_change(); trend=c/c.rolling(50).mean()-1; mom=c/c.shift(20)-1
    vol=r.rolling(20).std(); breadth=(trend.gt(0)&eligible).sum(axis=1)/pd.DataFrame(eligible,index=c.index).sum(axis=1).replace(0,np.nan)
    f=dict(trend=trend/.05,momentum=mom/.08,volatility=(.025-vol)/.015,
           volume=v/v.rolling(20).mean()-1,recursive=(c/c.ewm(span=20,min_periods=50).mean()-1)/.04,
           relative_strength=(c/c.shift(60)-1).where(eligible).rank(axis=1,pct=True)*2-1,
           breadth=pd.DataFrame(np.repeat(((breadth-.5)*2).to_numpy()[:,None],len(symbols),axis=1),index=c.index,columns=c.columns))
    score,pool=discovery(c.to_numpy(),eligible)
    sectors=tuple(str(d[d.ticker==s].sector_id.iloc[0]) for s in symbols)
    return Panel(dates,symbols,o.to_numpy(),c.to_numpy(),np.zeros(c.shape),r.to_numpy(),
                 {k:x.to_numpy() for k,x in f.items()},np.zeros(c.shape,dtype=int),breadth.to_numpy(),
                 sectors=sectors,eligible=eligible,screen_score=score,screen_mask=pool,synthetic_benchmark_fixture=True)


@dataclass(frozen=True)
class Strategy:
    family: str = 'momentum'
    horizon: int = 20
    threshold: float = 0.
    add: float = .008
    reduce: float = -.008
    trailing: float = .05
    def gene(self):
        return Gene(self.family,threshold=0.,hold_sessions=self.horizon-1,add=self.add,reduce=self.reduce,
                    trailing=self.trailing,exit_threshold=-1e30,hold_threshold=-1e30,weight=.06)


def outcomes(p, h, cutoff):
    """Only fully matured labels; path downside includes every intervening close."""
    n,k=p.close.shape
    y=np.full((n,k),np.nan); down=y.copy()
    for t in range(min(n-h-1,cutoff-h-1)):
        entry=p.open[t+1]*ENTRY
        y[t]=p.open[t+h+1]*EXIT/entry-1
        down[t]=np.minimum(0,np.minimum(p.close[t+1:t+h+1].min(axis=0),p.open[t+h+1])*EXIT/entry-1)
    return y,down



def strategy_outcomes(p, strategy, cutoff):
    """Isolated committed-capital sleeves executing the stock action rules.

    Two thirds enters next open; one third is reserved for one add. Reductions
    and exits execute after the triggering close. Portfolio funding is B's job.
    """
    n,k=p.close.shape; h=strategy.horizon
    y=np.full((n,k),np.nan); downside=y.copy()
    for t in range(min(n-h-1,cutoff-h-1)):
        base=p.open[t+1]; q=(2/3)/(base*ENTRY); cash=np.full(k,1/3.)
        peak=base*1.0005; entry=base*1.0005
        added=np.zeros(k,bool); reduced=added.copy(); worst=np.ones(k)
        for step in range(1,h+1):
            day=t+step; px=p.close[day]; peak=np.maximum(peak,px)
            worst=np.minimum(worst,cash+q*px)
            gain=px/entry-1; active=q>0
            exit_now=active & ((gain<=-.02)|(px<peak*(1-strategy.trailing))|~p.eligible[day]|(step==h))
            reduce=active & ~exit_now & ~reduced & (gain<=strategy.reduce)
            add=active & ~exit_now & ~reduce & ~added & (gain>=strategy.add)
            execution=p.open[day+1]
            sold=np.where(exit_now,q,np.where(reduce,q/2,0.))
            cash+=sold*execution*EXIT; q-=sold; reduced|=reduce
            z=p.features[strategy.family][day]
            add &= np.isfinite(z)&(z>=strategy.threshold)&p.eligible[day+1]
            bought=np.where(add,cash/(execution*ENTRY),0.)
            entry=np.where(bought>0,(entry*q+execution*1.0005*bought)/np.maximum(q+bought,1e-30),entry)
            cash-=bought*execution*ENTRY;q+=bought;added|=add
            worst=np.minimum(worst,cash+q*execution)
        y[t]=cash-1; downside[t]=np.minimum(0,worst-1)
    return y,downside


def fit(p, strategy, train_end=504, calibration_end=756):
    z=p.features[strategy.family]; ix=np.digitize(z,BOUNDARIES)
    y,down=strategy_outcomes(p,strategy,calibration_end)
    valid=p.eligible & p.screen_mask & np.isfinite(z) & (z>=strategy.threshold)
    rows=[]
    for b in range(6):
        mask=valid & (ix==b) & np.isfinite(y)
        train=mask.copy(); train[train_end-strategy.horizon-1:]=False
        cal=mask.copy(); cal[:train_end]=False
        # Separate later calibration dates; shrink small date samples to train mean.
        a=y[train]; c=y[cal]; days=int(np.count_nonzero(cal.any(axis=1)))
        weight=days/(days+30) if len(c) else 0.
        mean=(1-weight)*(float(a.mean()) if len(a) else 0.)+weight*(float(c.mean()) if len(c) else 0.)
        sample=y[mask]; adverse=down[mask]
        rows.append(dict(expected_net_return=mean,downside_p10=float(np.quantile(adverse,.1)) if len(adverse) else None,
                         probability_positive=float(np.mean(sample>0)) if len(sample) else None,
                         confidence=min(1.,days/max(1,3*strategy.horizon)),calibration_dates=days,
                         samples=len(sample),supported=bool(len(a)>=100 and days>=20)))
    return dict(label_basis='stock_policy_committed_capital_2_3_entry_1_3_add_reserve',strategy=asdict(strategy),cutoff=str(p.dates[calibration_end].date()),bins=rows)


def arrays(p, model):
    s=Strategy(**model['strategy']); z=p.features[s.family]; ix=np.digitize(z,BOUNDARIES)
    mean=np.array([r['expected_net_return'] for r in model['bins']])[ix]
    supported=np.array([r['supported'] for r in model['bins']])[ix]
    valid=np.isfinite(z)&supported&(z>=s.threshold)&p.eligible
    # Existing capital avoids charging the sunk entry cost again.
    hold=np.where(valid,((mean+1)*ENTRY-1)/s.horizon,np.nan)
    signal=np.where(valid & (mean>0),mean/s.horizon,-np.inf)
    return signal[None],hold[None]


def allocate(p, model, start, end, detail=True):
    """GA9-B compatibility: absolute net expected return/session competes for cash.

    A emits no portfolio weights. B owns slots, correlation, settlement and caps.
    """
    s=Strategy(**model['strategy']); signal,hold=arrays(p,model)
    return replay(p,[s.gene()],Manager(slots=10,reserve=.1,risk_cap=.008,replacement=.0001),
                  p.dates[start],p.dates[end-1]+pd.Timedelta(days=1),detail=detail,
                  signal=signal,hold_signal=hold,edge_mode=True,absolute_edges=True)


def opportunity(p, model, t, j):
    s=Strategy(**model['strategy']); z=p.features[s.family][t,j]
    row=model['bins'][int(np.digitize(z,BOUNDARIES))]
    return dict(as_of=str(p.dates[t].date()),ticker=p.symbols[j],strategy=asdict(s),
                execution='NEXT_SESSION_OPEN',horizon_sessions=s.horizon,return_unit='fraction_of_committed_capital',
                confidence_basis='calibration_date_support_not_probability_of_profit',**row,
                entry_eligible=bool(p.eligible[t,j] and p.screen_mask[t,j] and np.isfinite(z) and z>=s.threshold and row['supported'] and row['expected_net_return']>0),
                action_policy=dict(entry='positive supported net forecast in discovery pool',
                                   hold='positive remaining net forecast; original horizon expiry applies',
                                   add=f'gain >= {s.add}; positive new-capital forecast; once per position',
                                   reduce=f'gain <= {s.reduce}; half position once',
                                   exit='nonpositive remaining forecast, horizon, membership, 2% loss or trailing stop'))

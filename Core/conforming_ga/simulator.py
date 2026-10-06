"""Integrated deterministic simulator path used by conformance and future GA."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .schema import Genome
from .model import opportunity_values,claims_from_values
from .valuation import asset_values
from .ledger import AssetState,move_ledger
from .costs import one_way_cost,borrow_fee

@dataclass(frozen=True)
class SessionInput:
    when:str
    market:dict
    sector:dict
    stock:dict
    open_t1:dict
    open_t2:dict
    high_t:dict
    low_t:dict
    close_t:dict
    volume_t:dict
    dividends_t1_t2:dict
    daily_safe:float
    daily_borrow:dict
    uncertainty:dict|None=None
    downside:dict|None=None

@dataclass
class SimResult:
    equity:np.ndarray
    weights:list[dict[str,float]]
    turnover:np.ndarray
    safe_weight:np.ndarray
    decisions:list[list]
    costs:np.ndarray

def simulate(genome:Genome,sessions:list[SessionInput],*,initial_equity:float=100000.0,
             spread_bps:float=5.0,baseline_borrow_annual:float=.003)->SimResult:
    eq=float(initial_equity); equity=[eq]; prev={}; wh=[]; turns=[]; safe=[]; decisions=[]; costs=[]
    for s in sessions:
        E=opportunity_values(genome,market=s.market,sector=s.sector,stock=s.stock)
        unc=s.uncertainty or {}; dwn=s.downside or {}
        long_values={}; short_values={}
        states={"SAFE":AssetState(0.0,0.0,0.0,0.0)}
        for t,e in E.items():
            u=float(unc.get(t,1.0)); b=float(s.daily_borrow.get(t,baseline_borrow_annual/365.0))
            av=asset_values(float(e),u,genome.lifecycle.lambda_u,s.daily_safe,b,genome.short_policy.extra_hurdle)
            long_values[t]=av.long
            short_values[t]=av.short
        long_claims=claims_from_values(genome,long_values,unc,dwn)
        short_claims=claims_from_values(genome,short_values,unc,dwn) if genome.short_policy.enabled else {k:0.0 for k in E}
        # Long and short are competing signed risky claims. Resolve any same-name conflict by larger value.
        target={}
        for t in E:
            lc=float(long_claims.get(t,0)); sc=float(short_claims.get(t,0))
            if lc>0 and sc>0:
                if long_values[t]>=short_values[t]: sc=0.0
                else: lc=0.0
            target[t]=lc-sc
            chosen=long_values[t] if target[t]>=0 else short_values[t]
            states[t]=AssetState(chosen,float(unc.get(t,1.0)),0.0,0.0)
        gross=sum(abs(v) for v in target.values())
        if gross>1: target={k:v/gross for k,v in target.items()}
        cur,moves=move_ledger(prev,target,states,kappa=genome.lifecycle.kappa,lambda_u=genome.lifecycle.lambda_u)
        tc=0.0; turnover=0.0
        for t in set(prev)|set(cur):
            delta=cur.get(t,0)-prev.get(t,0)
            if abs(delta)<1e-15:continue
            notion=abs(delta)*eq; px=s.open_t1.get(t,np.nan)
            if not np.isfinite(px) or px<=0: raise ValueError(f"missing execution price {t}")
            shares=notion/px
            is_sell=(delta<0)
            tc+=one_way_cost(s.when,notion,shares,px,is_sell=is_sell,spread_slippage_bps=spread_bps)
            turnover+=abs(delta)
        eq-=tc
        pnl=0.0
        for t,w in cur.items():
            p1=s.open_t1.get(t,np.nan);p2=s.open_t2.get(t,np.nan)
            if not (np.isfinite(p1) and np.isfinite(p2) and p1>0 and p2>0): raise ValueError(f"missing return price {t}")
            total_ret=(p2+s.dividends_t1_t2.get(t,0.0))/p1-1.0
            pnl+=eq*w*total_ret
            if w<0:
                pnl-=borrow_fee(eq*abs(w),baseline_borrow_annual,1)
        sw=max(0.0,1.0-sum(abs(v) for v in cur.values()))
        pnl+=eq*sw*s.daily_safe
        eq+=pnl
        equity.append(eq);prev=dict(cur);wh.append(dict(cur));turns.append(turnover);safe.append(sw);decisions.append(moves);costs.append(tc)
    return SimResult(np.array(equity),wh,np.array(turns),np.array(safe),decisions,np.array(costs))

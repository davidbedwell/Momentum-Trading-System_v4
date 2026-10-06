"""Integrated deterministic simulator path used by conformance and future GA."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .schema import Genome
from .model import opportunity_values,claims_from_values
from .valuation import asset_values
from .ledger import AssetState,move_ledger
from .costs import one_way_cost,borrow_fee,spread_bps_from_hlc,impact_bps,regulatory_sell_fee

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
    adv_dollars_t:dict|None=None
    execute_when:str|None=None
    calendar_days:int=1
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
             spread_bps:float|None=None,spread_cap_bps:float=50.0,
             impact_coefficient:float=10.0,baseline_borrow_annual:float=.003)->SimResult:
    eq=float(initial_equity); equity=[eq]; prev={}; wh=[]; turns=[]; safe=[]; decisions=[]; costs=[]
    for s in sessions:
        E=opportunity_values(genome,market=s.market,sector=s.sector,stock=s.stock)
        unc=s.uncertainty or {}; dwn=s.downside or {}
        long_values={}; short_values={}
        states={"SAFE":AssetState(0.0,0.0,0.0,0.0)}
        period_safe=(1.0+s.daily_safe)**int(s.calendar_days)-1.0
        for t,e in E.items():
            u=float(unc.get(t,1.0)); b=float(s.daily_borrow.get(t,baseline_borrow_annual/365.0))*int(s.calendar_days)
            av=asset_values(float(e),u,genome.lifecycle.lambda_u,period_safe,b,genome.short_policy.extra_hurdle)
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
        gross=sum(abs(v) for v in target.values())
        if gross>1: target={k:v/gross for k,v in target.items()}
        exec_when=s.execute_when or s.when
        # E.4 compares opportunity against the same prospective friction later charged in cash.
        # Production ADV is the causal trailing-20-session dollar-volume tape supplied by experiment.py.
        adv=s.adv_dollars_t or {t:max(float(s.close_t.get(t,0))*float(s.volume_t.get(t,0)),1.0) for t in E}
        for t in E:
            chosen=long_values[t] if target[t]>=0 else short_values[t]
            sbps=float(spread_bps) if spread_bps is not None else spread_bps_from_hlc(
                float(s.high_t[t]),float(s.low_t[t]),float(s.close_t[t]),cap_bps=spread_cap_bps)
            entry_notional=max(0.0,abs(target.get(t,0.0))-abs(prev.get(t,0.0)))*eq
            exit_notional=max(0.0,abs(prev.get(t,0.0))-abs(target.get(t,0.0)))*eq
            entry=(sbps+impact_bps(entry_notional,float(adv.get(t,0.0)),impact_coefficient))/10000.0 if entry_notional>0 else 0.0
            exitc=(sbps+impact_bps(exit_notional,float(adv.get(t,0.0)),impact_coefficient))/10000.0 if exit_notional>0 else 0.0
            px=float(s.open_t1.get(t,np.nan))
            if entry_notional>0 and target.get(t,0.0)<0:
                entry+=regulatory_sell_fee(exec_when,entry_notional,entry_notional/px,px)/entry_notional
            if exit_notional>0 and prev.get(t,0.0)>0:
                exitc+=regulatory_sell_fee(exec_when,exit_notional,exit_notional/px,px)/exit_notional
            states[t]=AssetState(chosen,float(unc.get(t,1.0)),exitc,entry)
        cur,moves=move_ledger(prev,target,states,kappa=genome.lifecycle.kappa,lambda_u=genome.lifecycle.lambda_u)
        tc=0.0; turnover=0.0
        for t in set(prev)|set(cur):
            delta=cur.get(t,0)-prev.get(t,0)
            if abs(delta)<1e-15:continue
            notion=abs(delta)*eq; px=s.open_t1.get(t,np.nan)
            if not np.isfinite(px) or px<=0: raise ValueError(f"missing execution price {t}")
            shares=notion/px
            is_sell=(delta<0)
            sbps=float(spread_bps) if spread_bps is not None else spread_bps_from_hlc(
                float(s.high_t[t]),float(s.low_t[t]),float(s.close_t[t]),cap_bps=spread_cap_bps)
            ibps=impact_bps(notion,float(adv.get(t,0.0)),impact_coefficient)
            tc+=one_way_cost(exec_when,notion,shares,px,is_sell=is_sell,
                             spread_slippage_bps=sbps,impact_bps_value=ibps)
            turnover+=abs(delta)
        eq-=tc
        pnl=0.0
        for t,w in cur.items():
            p1=s.open_t1.get(t,np.nan);p2=s.open_t2.get(t,np.nan)
            if not (np.isfinite(p1) and np.isfinite(p2) and p1>0 and p2>0): raise ValueError(f"missing return price {t}")
            total_ret=(p2+s.dividends_t1_t2.get(t,0.0))/p1-1.0
            pnl+=eq*w*total_ret
            if w<0:
                pnl-=borrow_fee(eq*abs(w),baseline_borrow_annual,int(s.calendar_days))
        sw=max(0.0,1.0-sum(abs(v) for v in cur.values()))
        pnl+=eq*sw*period_safe
        eq+=pnl
        equity.append(eq);prev=dict(cur);wh.append(dict(cur));turns.append(turnover);safe.append(sw);decisions.append(moves);costs.append(tc)
    return SimResult(np.array(equity),wh,np.array(turns),np.array(safe),decisions,np.array(costs))

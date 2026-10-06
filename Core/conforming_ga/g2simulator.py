"""Production MTS-GA-G2 simulator using side-explicit lifecycle and approved costs."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
import numpy as np,pandas as pd
from .g2schema import GenomeG2
from .g2features import G2Tape
from .g2model import evaluate_g2_fields
from .g2ledger import SideState,G2Move,SAFE,side_id,parse_side,move_ledger_assets,alloc_to_signed
from .costs import spread_bps_from_hlc,impact_bps,one_way_cost,regulatory_sell_fee,borrow_fee

class UnapprovedKappaCombination(RuntimeError):pass
class UnsupportedOpportunityMap(RuntimeError):pass

@dataclass
class G2SimResult:
    equity:np.ndarray
    weights:list[dict[str,float]]
    allocations:list[dict[str,float]]
    turnover:np.ndarray
    safe_weight:np.ndarray
    decisions:list[list[G2Move]]
    costs:np.ndarray
    session_returns:np.ndarray
    short_share:np.ndarray

def _claim(v,u,d,mode,tau,q,gamma,eta):
    x=max(float(v)-float(q),0.0)
    if mode=="equal":g=float(eta) if v>q else 0.0
    elif mode=="strength":g=x**float(gamma)
    elif mode=="uncertainty":g=(x/max(float(u),1e-12))**float(gamma)
    elif mode=="downside":g=(x/max(float(d),1e-12))**float(gamma)
    else:raise ValueError(mode)
    return max(0.0,float(tau))*g

def _targets(g,fields,t,safe_rate,borrow_daily,days):
    E=np.asarray(fields["E"][t],float);u=np.asarray(fields["uncertainty"][t],float);dn=np.asarray(fields["downside"][t],float)
    q=np.asarray(fields["q"])[t];tau=np.asarray(fields["tau"])[t];sg=np.asarray(fields["short_gate"][t],float)
    if np.asarray(q).ndim: raise RuntimeError("q must be market scalar")
    if np.asarray(tau).ndim: raise RuntimeError("tau must be market scalar")
    short_allowed=bool(g.short_policy.enabled)
    raw={}
    vals={}
    for i in range(len(E)):
        if not np.isfinite(E[i]):continue
        uu=float(u[i]) if np.isfinite(u[i]) else 1.0
        dd=float(dn[i]) if np.isfinite(dn[i]) and dn[i]>0 else 1.0
        lv=float(E[i])-g.lifecycle.lambda_u*uu
        bv=float(borrow_daily[i])*days
        sv=-float(E[i])-2*safe_rate-bv-g.lifecycle.lambda_u*uu-g.short_policy.extra_hurdle
        lg=_claim(lv,uu,dd,g.allocation.mode,float(tau),float(q),g.allocation.gamma,g.allocation.eta)
        sh=0.0
        if short_allowed and np.isfinite(sg[i]):
            sh=_claim(sv,uu,dd,g.allocation.mode,float(tau)*float(np.clip(sg[i],0,1)),float(q),g.allocation.gamma,g.allocation.eta)
        if lg>0 and sh>0:
            if lv>=sv:sh=0.0
            else:lg=0.0
        if lg>0:raw[side_id(i,"LONG")]=lg;vals[side_id(i,"LONG")]=(lv,uu)
        if sh>0:raw[side_id(i,"SHORT")]=sh;vals[side_id(i,"SHORT")]=(sv,uu)
    total=sum(raw.values())
    if total>1:raw={k:v/total for k,v in raw.items()}
    return raw,vals


def simulate_g2(g:GenomeG2,tape:G2Tape,*,initial_equity:float=100000.0,
                spread_cap_bps:float=50.0,impact_coefficient:float=10.0,
                baseline_borrow_annual:float=.003)->G2SimResult:
    """Causal T decision -> T+1 open execution -> T+2 open mark production loop."""
    fields=evaluate_g2_fields(g,tape)
    ex=tape.execution; T=len(tape.dates); N=len(tape.tickers)
    eq=float(initial_equity); equity=[eq]; prev={}; wh=[]; ah=[]; turns=[]; safe=[]; dec=[]; costs=[]; rets=[]; shorts=[]
    for t in range(T-2):
        d0=pd.Timestamp(tape.dates[t]);d1=pd.Timestamp(tape.dates[t+1]);d2=pd.Timestamp(tape.dates[t+2])
        days=max(1,int((d2-d1).days))
        safe_daily=float(ex["safe_daily"][t]) if np.isfinite(ex["safe_daily"][t]) else 0.0
        period_safe=(1.0+safe_daily)**days-1.0
        borrow_daily=np.full(N,baseline_borrow_annual/365.0)
        target,vals=_targets(g,fields,t,period_safe,borrow_daily,days)
        k=np.asarray(fields["kappa"][t],float)
        if k.ndim>0:
            finite=k[np.isfinite(k)]
            if len(finite)==0:raise ValueError("nonfinite kappa")
            if np.nanmax(finite)-np.nanmin(finite)>1e-12:raise UnapprovedKappaCombination("stock-varying kappa requires move-pair rule")
            kappa=float(finite[0])
        else:kappa=float(k)
        if not np.isfinite(kappa) or kappa<0:raise ValueError("bad kappa")
        states={}
        adv=np.asarray(ex["adv_dollars"][t],float)
        for aid in set(prev)|set(target):
            i_s,side=parse_side(aid); i=int(i_s)
            value,u=vals.get(aid,(0.0,1.0))
            old=float(prev.get(aid,0.0));new=float(target.get(aid,0.0))
            ent_notional=max(0.0,new-old)*eq;exit_notional=max(0.0,old-new)*eq
            sbps=spread_bps_from_hlc(float(ex["high"][t,i]),float(ex["low"][t,i]),float(ex["close"][t,i]),cap_bps=spread_cap_bps)
            ent=0.0;out=0.0;px=float(ex["open"][t+1,i])
            if ent_notional>0:
                ent=(sbps+impact_bps(ent_notional,float(adv[i]),impact_coefficient))/10000.0
                if side=="SHORT":ent+=regulatory_sell_fee(d1.date(),ent_notional,ent_notional/px,px)/ent_notional
            if exit_notional>0:
                out=(sbps+impact_bps(exit_notional,float(adv[i]),impact_coefficient))/10000.0
                if side=="LONG":out+=regulatory_sell_fee(d1.date(),exit_notional,exit_notional/px,px)/exit_notional
            states[aid]=SideState(float(value),float(u),out,ent)
        cur,moves=move_ledger_assets(prev,target,states,kappa=kappa,lambda_u=float(g.lifecycle.lambda_u))
        tc=0.0;turn=0.0
        for aid in set(prev)|set(cur):
            delta=float(cur.get(aid,0.0)-prev.get(aid,0.0))
            if abs(delta)<1e-15:continue
            i_s,side=parse_side(aid);i=int(i_s);notional=abs(delta)*eq;px=float(ex["open"][t+1,i])
            if not np.isfinite(px) or px<=0:raise ValueError("missing execution price")
            sbps=spread_bps_from_hlc(float(ex["high"][t,i]),float(ex["low"][t,i]),float(ex["close"][t,i]),cap_bps=spread_cap_bps)
            ibps=impact_bps(notional,float(adv[i]),impact_coefficient)
            is_sell=(side=="LONG" and delta<0) or (side=="SHORT" and delta>0)
            tc+=one_way_cost(d1.date(),notional,notional/px,px,is_sell=is_sell,spread_slippage_bps=sbps,impact_bps_value=ibps)
            turn+=abs(delta)
        eq0=eq;eq-=tc;pnl=0.0
        for aid,w in cur.items():
            i_s,side=parse_side(aid);i=int(i_s);p1=float(ex["open"][t+1,i]);p2=float(ex["open"][t+2,i])
            if not(np.isfinite(p1) and np.isfinite(p2) and p1>0 and p2>0):raise ValueError("missing return price")
            div=float(ex["dividends"][t+2,i]) if np.isfinite(ex["dividends"][t+2,i]) else 0.0
            r=(p2+div)/p1-1.0
            pnl+=eq*w*(r if side=="LONG" else -r)
            if side=="SHORT":
                pnl-=borrow_fee(eq*w,baseline_borrow_annual,days)
        sw=max(0.0,1.0-sum(cur.values()));pnl+=eq*sw*period_safe;eq+=pnl
        equity.append(eq);prev=dict(cur);ah.append(dict(cur));signed=alloc_to_signed(cur);wh.append(signed)
        turns.append(turn);safe.append(sw);dec.append(moves);costs.append(tc);rets.append(eq/eq0-1.0);shorts.append(sum(v for a,v in cur.items() if parse_side(a)[1]=="SHORT"))
    return G2SimResult(np.asarray(equity),wh,ah,np.asarray(turns),np.asarray(safe),dec,np.asarray(costs),np.asarray(rets),np.asarray(shorts))

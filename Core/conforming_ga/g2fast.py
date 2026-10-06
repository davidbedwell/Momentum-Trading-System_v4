"""Numba production fitness core for MTS-GA-G2; same E.4 ledger semantics."""
from __future__ import annotations
import numpy as np,pandas as pd
from numba import njit
from .g2model import evaluate_g2_fields
from .costs import sec31_rate,taf_rate_cap

@njit(cache=True)
def _claim(v,u,d,mode,tau,q,gamma,eta):
    x=max(v-q,0.0)
    if mode==0:g=eta if v>q else 0.0
    elif mode==1:g=x**gamma
    elif mode==2:g=(x/max(u,1e-12))**gamma
    else:g=(x/max(d,1e-12))**gamma
    return max(0.0,tau)*g

@njit(cache=True)
def _core(E,U,D,q,tau,sg,kappa,opn,high,low,close,div,adv,safe_daily,days,sec,taf_rate,taf_cap,
          mode,gamma,eta,lambda_u,short_enabled,extra_hurdle,borrow_annual,spread_cap,impact_coef):
    TT,N=E.shape;T=TT-2;A=2*N
    prev=np.zeros(A);equity=np.empty(T+1);equity[0]=100000.0
    turn=np.zeros(T);safe=np.zeros(T);shortshare=np.zeros(T);costs=np.zeros(T);rets=np.zeros(T);hhi=np.zeros(T);grossout=np.zeros(T)
    for t in range(T):
        eq=equity[t];period_safe=(1.0+safe_daily[t])**days[t]-1.0
        want=np.zeros(A);val=np.zeros(A);unc=np.zeros(A)
        for i in range(N):
            u=U[t,i] if np.isfinite(U[t,i]) else 1.0;d=D[t,i] if np.isfinite(D[t,i]) and D[t,i]>0 else 1.0
            lv=E[t,i]-lambda_u*u
            sv=-E[t,i]-2.0*period_safe-(borrow_annual/365.0)*days[t]-lambda_u*u-extra_hurdle
            lg=_claim(lv,u,d,mode,tau[t],q[t],gamma,eta);sh=0.0
            if short_enabled:sh=_claim(sv,u,d,mode,tau[t]*min(1.0,max(0.0,sg[t,i])),q[t],gamma,eta)
            if lg>0.0 and sh>0.0:
                if lv>=sv:sh=0.0
                else:lg=0.0
            want[i]=lg;want[N+i]=sh;val[i]=lv;val[N+i]=sv;unc[i]=u;unc[N+i]=u
        tot=np.sum(want)
        if tot>1.0:want/=tot
        ent=np.zeros(A);out=np.zeros(A)
        for a in range(A):
            i=a if a<N else a-N
            en=max(0.0,want[a]-prev[a])*eq;ex=max(0.0,prev[a]-want[a])*eq
            sbps=10000.0*(high[t,i]-low[t,i])/close[t,i]/2.0
            sbps=min(spread_cap,max(2.0,sbps));px=opn[t+1,i];ad=adv[t,i]
            if en>0.0:
                ib=impact_coef*np.sqrt(en/ad) if ad>0 else 1e9;ent[a]=(sbps+ib)/10000.0
                if a>=N:
                    fee=en*sec[t]+min((en/px)*taf_rate[t],taf_cap[t]) if px>=taf_rate[t] else en*sec[t]
                    ent[a]+=fee/en
            if ex>0.0:
                ib=impact_coef*np.sqrt(ex/ad) if ad>0 else 1e9;out[a]=(sbps+ib)/10000.0
                if a<N:
                    fee=ex*sec[t]+min((ex/px)*taf_rate[t],taf_cap[t]) if px>=taf_rate[t] else ex*sec[t]
                    out[a]+=fee/ex
        cur=prev.copy()
        # E.4 is separable: best destination score minus lowest source score.
        for _ in range(A+2):
            safe_now=max(0.0,1.0-np.sum(cur));safe_want=max(0.0,1.0-np.sum(want))
            src=-1;src_amt=0.0;src_score=1e300
            for a in range(A):
                x=cur[a]-want[a]
                if x>1e-15:
                    score=val[a]+kappa[t]*out[a]+lambda_u*unc[a]
                    if score<src_score:src_score=score;src=a;src_amt=x
            if safe_now>safe_want+1e-15 and 0.0<src_score:src=A;src_score=0.0;src_amt=safe_now-safe_want
            dst=-1;dst_amt=0.0;dst_score=-1e300
            for b in range(A):
                x=want[b]-cur[b]
                if x>1e-15:
                    score=val[b]-kappa[t]*ent[b]-lambda_u*unc[b]
                    if score>dst_score:dst_score=score;dst=b;dst_amt=x
            if safe_now<safe_want-1e-15 and 0.0>dst_score:dst=A;dst_score=0.0;dst_amt=safe_want-safe_now
            if src<0 or dst<0 or dst_score-src_score<=0.0:break
            amt=min(src_amt,dst_amt)
            if src<A:cur[src]-=amt
            if dst<A:cur[dst]+=amt
        tc=0.0;tv=0.0
        for a in range(A):
            delta=cur[a]-prev[a]
            if abs(delta)<=1e-15:continue
            i=a if a<N else a-N;notional=abs(delta)*eq;px=opn[t+1,i]
            sbps=10000.0*(high[t,i]-low[t,i])/close[t,i]/2.0;sbps=min(spread_cap,max(2.0,sbps))
            ib=impact_coef*np.sqrt(notional/adv[t,i]) if adv[t,i]>0 else 1e9
            fee=notional*(sbps+ib)/10000.0
            is_sell=(a<N and delta<0) or (a>=N and delta>0)
            if is_sell:
                fee+=notional*sec[t]
                if px>=taf_rate[t]:fee+=min((notional/px)*taf_rate[t],taf_cap[t])
            tc+=fee;tv+=abs(delta)
        base=eq;eq-=tc;pnl=0.0;gross=0.0;shgross=0.0;sumsq=0.0
        for i in range(N):
            wl=cur[i];ws=cur[N+i];gross+=wl+ws;shgross+=ws;sumsq+=wl*wl+ws*ws
            if wl+ws>0.0:
                p1=opn[t+1,i];p2=opn[t+2,i];dv=div[t+2,i] if np.isfinite(div[t+2,i]) else 0.0
                rr=(p2+dv)/p1-1.0;pnl+=eq*(wl*rr-ws*rr)
        pnl-=eq*shgross*borrow_annual*days[t]/365.0
        sw=max(0.0,1.0-gross);pnl+=eq*sw*period_safe;eq+=pnl
        equity[t+1]=eq;turn[t]=tv;safe[t]=sw;shortshare[t]=shgross;costs[t]=tc;rets[t]=eq/base-1.0
        grossout[t]=gross;hhi[t]=sumsq/(gross*gross) if gross>0 else 0.0;prev=cur
    return equity,rets,turn,safe,shortshare,costs,grossout,hhi

def fast_simulate_g2(g,tape,*,initial_equity=100000.0,spread_cap_bps=50.0,impact_coefficient=10.0,baseline_borrow_annual=.003):
    if initial_equity!=100000.0:raise ValueError("fast core registered at $100k initial equity")
    f=evaluate_g2_fields(g,tape);T=len(tape.dates)-2
    dates=[pd.Timestamp(tape.dates[t+1]).date() for t in range(T)]
    sec=np.array([sec31_rate(d) for d in dates],float);tr=[];tc=[]
    for d in dates:
        a,b=taf_rate_cap(d);tr.append(a);tc.append(b)
    days=np.array([max(1,(pd.Timestamp(tape.dates[t+2])-pd.Timestamp(tape.dates[t+1])).days) for t in range(T)],np.int64)
    mode={"equal":0,"strength":1,"uncertainty":2,"downside":3}[g.allocation.mode]
    ex=tape.execution
    return _core(np.asarray(f["E"],float),np.asarray(f["uncertainty"],float),np.asarray(f["downside"],float),
      np.asarray(f["q"],float),np.asarray(f["tau"],float),np.asarray(f["short_gate"],float),np.asarray(f["kappa"],float),
      np.asarray(ex["open"],float),np.asarray(ex["high"],float),np.asarray(ex["low"],float),np.asarray(ex["close"],float),
      np.asarray(ex["dividends"],float),np.asarray(ex["adv_dollars"],float),np.asarray(ex["safe_daily"],float),days,
      sec,np.asarray(tr,float),np.asarray(tc,float),mode,float(g.allocation.gamma),float(g.allocation.eta),
      float(g.lifecycle.lambda_u),bool(g.short_policy.enabled),float(g.short_policy.extra_hurdle),float(baseline_borrow_annual),
      float(spread_cap_bps),float(impact_coefficient))

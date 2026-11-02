"""Experiment-local frozen models and separate causal reliability policy."""
from reference import *

def predictors(days, sensors):
    out=[]
    for i in range(252):
        rows=[]
        for j,t in enumerate(s.TICKERS):
            returns=[];sector=[];market=[]
            for h in range(max(1,i-19),i+1):
                def ret(q):
                    try:return days[h][1][q].close/days[h-1][1][q].close-1
                    except (KeyError,ZeroDivisionError):return 0.
                returns.append(ret(t));sector.append(st.mean(ret(q) for q in s.TICKERS[(j//6)*6:(j//6+1)*6]));market.append(st.mean(ret(q) for q in s.TICKERS))
            vol=max(.005,st.pstdev(returns)) if returns else .005
            trend=st.mean(returns) if returns else 0.
            relative=trend-(st.mean(sector) if sector else 0.)
            residual=trend-(st.mean(market) if market else 0.)
            price=[relative/.01,residual/.01,trend/vol,vol/.01]
            rows.append([1.]+[float(sensors[i][j]==c) for c in range(4)]+price)
        out.append(rows)
    return out

def solve(rows, cols):
    n=len(cols);a=[[float(x==y) for y in range(n)] for x in range(n)];v=[0.]*n
    for x,y in rows:
        z=[x[c] for c in cols]
        for h in range(n):
            v[h]+=z[h]*y
            for q in range(n):a[h][q]+=z[h]*z[q]
    for h in range(n):
        pivot=a[h][h]
        for q in range(h,n):a[h][q]/=pivot
        v[h]/=pivot
        for z in range(n):
            if z==h:continue
            f=a[z][h]
            for q in range(h,n):a[z][q]-=f*a[h][q]
            v[z]-=f*v[h]
    return v

def forecast(beta,x,cols):return sum(b*x[c] for b,c in zip(beta,cols))

def fit(days,x,cols):
    rows=[(x[i][j],observed(days,i,j)) for i in range(20,78) for j in range(24)]
    beta=solve(rows,cols)
    # Independent date-cluster residual bias; five-date block uncertainty.
    residual=[st.mean(observed(days,i,j)-forecast(beta,x[i][j],cols) for j in range(24)) for i in range(80,122)]
    blocks=[st.mean(residual[i:i+5]) for i in range(0,40,5)]
    bias=abs(st.mean(blocks));se=st.stdev(blocks)/len(blocks)**.5
    # Include training date residual SE, without treating stocks as dates.
    tr=[st.mean(observed(days,i,j)-forecast(beta,x[i][j],cols) for j in range(24)) for i in range(20,78)]
    radius=bias+2.58*math.hypot(se,st.stdev(tr)/len(tr)**.5)
    return dict(beta=beta,cols=cols,radius=radius,bias=bias)

def gate(disagreement,recent,drift,latched=False):
    reason='DETERIORATION' if recent is not None and abs(recent)>.004 else 'FEATURE_DRIFT' if drift>4 else 'FORECAST_DISAGREEMENT' if disagreement>.004 else 'RELIABLE'
    return not latched and reason=='RELIABLE',reason,latched or reason in ('DETERIORATION','FEATURE_DRIFT')

def predict(days,sensors):
    x=predictors(days,sensors);models=None;states={k:[] for k in ('iteration4','ungated','sensor_only','price_only')};ledger=[];alarms=[];latched=False
    center=[st.mean(x[i][j][c] for i in range(20,78) for j in range(24)) for c in range(9)]
    scale=[max(.1,st.pstdev(x[i][j][c] for i in range(20,78) for j in range(24))) for c in range(9)]
    for now in range(252):
        for row in ledger[max(0,(now-3)*24):max(0,(now-2)*24)]:
            if row['index']!=now-3:continue
            try:row.update(realized_net=observed(days,row['index'],row['j']),available_index=now,missingness='OBSERVED')
            except (KeyError,IndexError):row['missingness']='MISSING'
        if now==126:models={name:fit(days,x,cols) for name,cols in [('full',list(range(9))),('sensor',list(range(5))),('price',[0,5,6,7,8])]}
        recentrows=[z for z in ledger if now-8<=z['index']<now-2 and z['index']>=126 and z['realized_net'] is not None]
        datebias={}
        for z in recentrows:datebias.setdefault(z['index'],[]).append(z['realized_net']-z['inferred_net'])
        recent=st.mean(st.mean(v) for v in datebias.values()) if len(datebias)>=3 else None
        current={k:[] for k in states}
        for j in range(24):
            preds={k:forecast(v['beta'],x[now][j],v['cols']) for k,v in models.items()} if models else dict(full=0.,sensor=0.,price=0.)
            drift=max(abs(x[now][j][c]-center[c])/scale[c] for c in range(5,9)) if now>=126 else 0.
            ok,reason,latch=gate(max(preds.values())-min(preds.values()),recent,drift,latched)
            if latch and not latched:alarms.append(dict(index=now,reason=reason,last_signal=now-3));latched=True
            for variant,key in [('iteration4','full'),('ungated','full'),('sensor_only','sensor'),('price_only','price')]:
                mu=preds[key];radius=models[key]['radius'] if models else 1.
                label=infer(mu,radius,58 if models else 0,42 if models else 0)
                if variant=='iteration4' and not ok:label='UNKNOWN'
                current[variant].append(dict(mean=mu,radius=radius,label=label,reason=reason if variant=='iteration4' else 'UNGATED',latest_outcome_signal=now-3,reliability=float(ok),ntrain=58 if models else 0,ncal=42 if models else 0))
            if now<250:ledger.append(dict(index=now,j=j,execution_index=now+1,maturity_index=now+2,available_index=None,realized_net=None,missingness='PENDING',inferred_net=preds['full'],features=x[now][j],feature_latest_index=now,feature_source='close<=decision; fixed six-symbol synthetic sector proxy',volume=None,revisions=None,inferred_tier=current['iteration4'][-1]['label'],gate_reason=reason))
        for key in states:states[key].append(current[key])
    return states,ledger,alarms

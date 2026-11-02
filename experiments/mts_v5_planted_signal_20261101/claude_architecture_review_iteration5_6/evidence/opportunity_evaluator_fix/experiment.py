#!/usr/bin/env python3
"""Frozen five-tier diagnostic. Standard library; experiment-local MTS seam only."""
import sys,json,time,math,random,statistics as st,hashlib,csv,gzip,importlib.util,subprocess,unittest
from pathlib import Path
from dataclasses import replace
OUT=Path(__file__).resolve().parent
PRIOR=OUT.parent/'scaling_robustness'
sys.path.insert(0,str(OUT.parent/'scaling_blocker_audit'))
import audit as a
r=a.r;s=r.s1

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
m=load('discovery.competitive_ga.five_tier_manager',PRIOR/'corrected_manager.py')
k=load('five_tier_kernel',PRIOR/'corrected_kernel.py');m.Replay=k.Replay
TIERS=('TERRIBLE','POOR','AVERAGE','GOOD','GREAT');EDGES=(-.006,-.002,.002,.006)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def tier(x):return TIERS[sum(x>=b for b in EDGES)]
def infer(mean,radius,ntrain,ncal):
    return tier(mean) if min(ntrain,ncal)>=20 and tier(mean-radius)==tier(mean+radius) else 'UNKNOWN'
def se(v):return st.stdev(v)/len(v)**.5 if len(v)>1 else float('inf')

def generate(seed,scenario):
    rng=random.Random(seed);features=[];pred=[];truth=[];rets=[]
    mu=(-.012,-.004,0.,.004,.012)
    for i in range(252):
        common=rng.gauss(0,.003);ff=[];pp=[];tt=[];rr=[]
        for j in range(24):
            z=rng.randrange(5)
            # Observable noisy measurement, never an oracle class or forward return.
            f=z if rng.random()<.8 else rng.randrange(5)
            if scenario=='null':f=rng.randrange(5)
            if scenario=='reversal' and i>=126:f=4-f
            guessed=mu[f]
            predicted=(.010-guessed if scenario in ('misleading','null','reversal') else guessed)
            # Exact execution net return: gross-to-net uses full multiplicative costs.
            net=mu[z]+common+rng.gauss(0,.008)
            gross=(1+net)*(1+s.FRICTION)*(1+s.COSTS['fees'])/((1-s.FRICTION)*(1-s.COSTS['fees']))-1
            ff.append(f);pp.append(predicted);tt.append(mu[z]);rr.append(gross)
        features.append(ff);pred.append(pp);truth.append(tt);rets.append(rr)
    prices=[100.+j for j in range(24)];days=[]
    for i,d in enumerate(s.DATES):
        if i>=2:prices=[v*(1+rr) for v,rr in zip(prices,rets[i-2])]
        days.append((d,{t:k.Bar(prices[j],prices[j]) for j,t in enumerate(s.TICKERS)}))
    return days,features,pred,truth

def observed(days,i,j):
    t=s.TICKERS[j]
    return days[i+2][1][t].open*(1-s.FRICTION)*(1-s.COSTS['fees'])/(days[i+1][1][t].open*(1+s.FRICTION)*(1+s.COSTS['fees']))-1

def fit(days,features,cutoff=126):
    cells=[]
    for cell in range(5):
        groups=[]
        for lo,hi in ((0,78),(80,122)):
            values=[]
            for i in range(lo,hi):
                assert i+2<cutoff
                row=[observed(days,i,j) for j in range(24) if features[i][j]==cell]
                if row:values.append(st.mean(row))
            groups.append(values)
        train,cal=groups;mean=st.mean(train)
        radius=max(2.58*se(train),abs(st.mean(cal)-mean)+2.58*se(cal))
        cells.append(dict(mean=mean,radius=radius,ntrain=len(train),ncal=len(cal),label=infer(mean,radius,len(train),len(cal))))
    return cells

def callbacks(features,pred,cells,variant,days):
    idx={d:i for i,d in enumerate(s.DATES)}
    def value(t,d):
        i=idx[d];j=int(t[3:]);cell=cells[features[i][j]]
        return pred[i][j] if variant=='existing_ev10' else (cell['mean'] if cell['label'] in ('GOOD','GREAT') else -1.)
    def native(c,t,d,h):
        i=idx[d];j=int(t[3:]);v=value(t,d)
        if h:action='EXIT' if v<=0 else 'HOLD'
        else:action='ENTER' if v>0 else None
        if action is None:return None
        target=0. if action=='EXIT' else h['weight'] if h else .10
        # Conditional scaling needs GREAT plus actual native evidence, never truth.
        if h and action=='HOLD' and variant in ('tier15','tier20') and cells[features[i][j]]['label']=='GREAT':
            target=.15 if variant=='tier15' else .20
            if h['weight']<target-1e-6:action='ADD'
        return r.NativeProposal(d,t,c.family,c.chromosome_id,action,target,v+s.ROUND_TRIP,'net_return_fraction','FROZEN_CAUSAL_CELLS','FIVE_TIER','2029-12-31')
    def evidence(c,t,d,h,realized,nav):
        # Filter strictly earlier closes, including exclusion of same-close exits.
        past=[z for z in realized if z['date']<d];folds={}
        for z in past:folds.setdefault(idx[z['date']]//42,[]).append(z['return'])
        positive_folds=sum(f<idx[d]//42 and st.mean(v)>0 for f,v in folds.items())
        peak=s.INITIAL;mdd=0
        for row in nav:
            if row[0]>=d:continue
            peak=max(peak,row[1]);mdd=max(mdd,1-row[1]/peak)
        confirmed=cells[features[idx[d]][int(t[3:])]]['label']=='GREAT'
        return r.ScaleEvidence(len(past),positive_folds,bool(past) and st.mean(z['return'] for z in past)>0,mdd,confirmed,dict(days)[d][t].close>h['entry']*(1+s.COSTS['fees']),False)
    return dict(classify=lambda t,d:m.NicheObservation(d,'2029-12-31','PIT_NOISY_MEASUREMENT',(('synthetic',.1),)),eligible=lambda c,t,d:c.chromosome_id==t,native=native,conditional_ev=lambda c,t,d,*args:value(t,d),scaling_evidence=evidence if variant in ('tier15','tier20') else None)

def causal_predictions(days,features,pred):
    """Sequential close clock: publish matured outcomes, then predict all eligibles.

    No truth, scenario, oracle regime, portfolio selection or holdout label input.
    Evaluation outcomes enter only after their predeclared execution horizon matures.
    """
    ledger=[];states=[];alarms=[];quarantine=-1
    for now in range(252):
        for row in ledger:
            if row['maturity_index'] < now and row['missingness']=='PENDING':
                try:
                    row['realized_net']=observed(days,row['index'],row['j'])
                    row['missingness']='OBSERVED'
                    row['available_index']=now
                except (KeyError,IndexError,TypeError):row['missingness']='MISSING_BARS'
        matured=[z for z in ledger if z['missingness']=='OBSERVED' and z['index']>=now-63]
        groups=[];drift=[]
        for cell in range(5):
            dates={}
            for z in matured:
                if z['signal']==cell:dates.setdefault(z['index'],[]).append(z['realized_net'])
            grouped=[(d,st.mean(v)) for d,v in sorted(dates.items())]
            old=[v for d,v in grouped if d<now-11];recent=[v for d,v in grouped if d>=now-11]
            alarm=len(old)>=30 and len(recent)>=7 and abs(st.mean(recent)-st.mean(old))>max(.004,3*(se(old)**2+se(recent)**2)**.5)
            if alarm:drift.append(cell)
            train=[v for d,v in grouped if d<now-23];cal=[v for d,v in grouped if d>=now-23]
            mean=st.mean(cal) if cal else 0.
            radius=max(2.58*se(cal),abs(st.mean(train)-mean)+2.58*se(train)) if train and cal else 1.
            outcomes=[z['realized_net'] for z in matured if z['signal']==cell]
            downside=sorted(outcomes)[int(.05*len(outcomes))] if outcomes else -1.
            groups.append(dict(mean=mean,radius=radius,ntrain=len(train),ncal=len(cal),label=infer(mean,radius,len(train),len(cal)),downside05=downside))
        if drift and now>quarantine:
            alarms.append(dict(index=now,date=s.DATES[now],cells=drift));quarantine=now+20
        # Explicit absence of identifiable conditional signal must never mean AVERAGE.
        identifiable=max(z['mean'] for z in groups)-min(z['mean'] for z in groups)>=.003
        for z in groups:
            reason='CONFIDENT'
            if now<=quarantine:reason='DRIFT_QUARANTINE'
            elif not identifiable:reason='NO_IDENTIFIABLE_SIGNAL'
            elif z['downside05']<(-.03 if z['label'] in ('GOOD','GREAT') else -.05):reason='OUTCOME_RISK'
            elif z['label']=='UNKNOWN':reason='INSUFFICIENT_OR_BOUNDARY_UNCERTAINTY'
            if reason!='CONFIDENT':z['label']='UNKNOWN'
            z['reason']=reason
        states.append(groups)
        if now<250:
            for j,t in enumerate(s.TICKERS):
                c=groups[features[now][j]]
                ledger.append(dict(index=now,j=j,ticker=t,decision_timestamp=s.DATES[now],execution_index=now+1,
                    maturity_index=now+2,maturation_timestamp=s.DATES[now+2],available_index=None,
                    horizon='open(k+1) to open(k+2)',signal=features[now][j],predicted_net=pred[now][j],
                    inferred_net=c['mean'],radius=c['radius'],inferred_tier=c['label'],reason=c['reason'],
                    context={'measurement_cell':features[now][j],'clock_window_start':max(0,now-63),'drift_quarantine':now<=quarantine},
                    costs=dict(s.COSTS),friction=s.FRICTION,realized_net=None,missingness='PENDING',eligible=True))
    return states,ledger,alarms

# Existing native seam, with a PIT state selected on each callback date.
_frozen_callbacks=callbacks
def callbacks(features,pred,cells,variant,days):
    if not isinstance(cells[0],list):return _frozen_callbacks(features,pred,cells,variant,days)
    def dispatch(name,*args):
        # All callbacks have date as third positional argument.
        date=args[2];i=s.DATES.index(date)
        return _frozen_callbacks(features,pred,cells[i],variant,days)[name](*args)
    kw=_frozen_callbacks(features,pred,cells[0],variant,days)
    for name in ('native','conditional_ev','scaling_evidence'):
        if kw[name] is not None:kw[name]=lambda *args,_name=name:dispatch(_name,*args)
    return kw

def discrimination(days,features,pred,truth,cells):
    rows=[];mat=[[0]*5 for _ in range(5)];realmat=[[0]*5 for _ in range(5)];unknown=[0]*5;unknown_real=[0]*5
    for i in range(126,250):
        for j in range(24):
            cell=(cells[i] if isinstance(cells[0],list) else cells)[features[i][j]];actual=observed(days,i,j);true=tier(truth[i][j]);label=cell['label']
            row=dict(index=i,ticker=s.TICKERS[j],signal=features[i][j],predicted_net=pred[i][j],inferred_net=cell['mean'],radius=cell['radius'],inferred_tier=label,true_ev=truth[i][j],true_ev_tier=true,realized_net=actual,realized_tier=tier(actual))
            rows.append(row)
            if label=='UNKNOWN':unknown[TIERS.index(true)]+=1;unknown_real[TIERS.index(tier(actual))]+=1
            else:mat[TIERS.index(true)][TIERS.index(label)]+=1;realmat[TIERS.index(tier(actual))][TIERS.index(label)]+=1
    assigned=[z for z in rows if z['inferred_tier']!='UNKNOWN'];counts={t:sum(z['inferred_tier']==t for z in rows) for t in (*TIERS,'UNKNOWN')}
    means={t:st.mean(z['realized_net'] for z in rows if z['inferred_tier']==t) if counts[t] else None for t in (*TIERS,'UNKNOWN')}
    recalls={t:mat[h][h]/sum(z['true_ev_tier']==t for z in rows) for h,t in enumerate(TIERS)}
    accuracy=sum(z['true_ev_tier']==z['inferred_tier'] for z in assigned)/len(assigned) if assigned else None
    monotone=all(means[t] is not None for t in TIERS) and all(means[TIERS[i]]<means[TIERS[i+1]] for i in range(4))
    false=mat[0][4]/sum(z['true_ev_tier']=='TERRIBLE' for z in rows)
    x=[z['inferred_net'] for z in rows];y=[z['realized_net'] for z in rows];px=[z['predicted_net'] for z in rows]
    def calibration(xx):
        slope=s.corr(xx,y);variance=st.pvariance(xx)
        b=sum((v-st.mean(xx))*(w-st.mean(y)) for v,w in zip(xx,y))/len(xx)/variance if variance else None
        return dict(bias=st.mean(w-v for v,w in zip(xx,y)),rmse=math.sqrt(st.mean((v-w)**2 for v,w in zip(xx,y))),slope=b,intercept=st.mean(y)-b*st.mean(xx) if b is not None else None,rank_correlation=s.corr(s.ranks(xx),s.ranks(y)))
    passed=len(assigned)/len(rows)>=.5 and all(counts[t]>=20 for t in TIERS) and (accuracy or 0)>=.7 and min(recalls.values())>=.5 and false<=.01 and monotone
    return dict(status='PASS' if passed else 'FAIL',n=len(rows),coverage=len(assigned)/len(rows),counts=counts,true_ev_counts={t:sum(z['true_ev_tier']==t for z in rows) for t in TIERS},conditional_accuracy=accuracy,recall_including_abstain=recalls,forward_realized_net_by_tier=means,monotonic=monotone,false_great_on_terrible_rate=false,false_great_on_terrible_count=mat[0][4],great_precision=mat[4][4]/counts['GREAT'] if counts['GREAT'] else None,calibration=calibration(x),raw_prediction_calibration=calibration(px),confusion_ev=mat,confusion_realized=realmat,unknown_by_ev_tier=unknown,unknown_by_realized_tier=unknown_real,cells=cells[-1] if isinstance(cells[0],list) else cells),rows

def main():
    start=time.monotonic();plan=json.loads((OUT/'preregister.json').read_text());frozen=sha(OUT/'preregister.json')
    # Mandatory tests execute before generating any full experiment tape or replay.
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(OUT),'-p','test_*.py'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        (OUT/'report.json').write_text(json.dumps(dict(status='STOP_TEST_FAILURE',full_portfolio_replays=0)))
        raise SystemExit(result.returncode)
    sources=list(a.SOURCES)+[PRIOR/'corrected_manager.py',PRIOR/'corrected_kernel.py',PRIOR/'source.patch',OUT.parent/'run.py']
    before={str(p):sha(p) for p in sources};metrics=[];scores=[];tapes=[];attempts=0
    with gzip.open(OUT/'replays.jsonl.gz','wt') as archive,gzip.open(OUT/'opportunities.jsonl.gz','wt') as opportunities:
        for seed in plan['seeds']:
            for scenario in plan['scenarios']:
                assert time.monotonic()-start<plan['max_seconds']
                days,features,pred,truth=generate(seed,scenario);cells,ledger,alarms=causal_predictions(days,features,pred)
                frozen_cells=sha_bytes(json.dumps(cells).encode());score,rows=discrimination(days,features,pred,truth,cells)
                scores.append(dict(seed=seed,scenario=scenario,drift_alarms=alarms,drift_detection_delay=(next((z['index']-126 for z in alarms if z['index']>=126),None) if scenario=='reversal' else None),**score));tapes.append(dict(seed=seed,scenario=scenario,sha256=sha_bytes(json.dumps([features,pred,truth,[(d,{t:vars(b) for t,b in bars.items()}) for d,bars in days]]).encode()),frozen_cells_sha256=frozen_cells))
                for z in ledger:opportunities.write(json.dumps(dict(seed=seed,scenario=scenario,**z))+'\n')
                for variant in plan['policies']:
                    assert attempts<64 and time.monotonic()-start<plan['max_seconds']
                    attempts+=1;(OUT/'attempts.json').write_text(json.dumps(dict(attempts=attempts,seed=seed,scenario=scenario,variant=variant)))
                    kw=callbacks(features,pred,cells,variant,days)
                    evdays=days[126:252]
                    candidates=[m.Candidate(t,'GA7','synthetic',.02,s.GAPS[j]) for j,t in enumerate(s.TICKERS)]
                    result=m.run_slice(evdays,candidates,max_sessions=126,max_stocks=24,**s.COSTS,**kw)
                    metric,daily=s.measure(result,evdays)
                    # measure's legacy annualization assumes 252 sessions; correct locally.
                    metric['total_return']=metric['final_nav']/s.INITIAL-1
                    metric['cagr']=(metric['final_nav']/s.INITIAL)**(252/len(evdays))-1
                    metric['annualized_turnover']=metric['turnover']*252/len(evdays)
                    metric['calmar']=metric['cagr']/metric['mdd'] if metric['mdd'] else None
                    metric['fees']=sum(f[5] for f in result['ledger'])
                    metric['spread_slippage_impact_cost']=sum(f[3]*abs(f[4]-dict(evdays)[f[0]][f[1]].open) for f in result['ledger'])
                    fills=a.scaling_fills(result,evdays,.15 if variant=='tier15' else .20) if variant in ('tier15','tier20') else []
                    metrics.append(dict(seed=seed,scenario=scenario,variant=variant,scaled_fills=len(fills),full_target_fills=sum(z['full'] for z in fills),**metric))
                    archive.write(json.dumps(dict(seed=seed,scenario=scenario,variant=variant,ledger=result['ledger'],nav=result['nav'],risk=result['risk_audit'],decisions=result['decisions'],scaled_fills=fills))+'\n')
                    assert sha_bytes(json.dumps(cells).encode())==frozen_cells
                print(f'seed={seed} scenario={scenario} replays={attempts}/64 elapsed={time.monotonic()-start:.1f}s',flush=True)
    paired=[]
    for z in metrics:
        base=next(b for b in metrics if b['seed']==z['seed'] and b['scenario']==z['scenario'] and b['variant']=='existing_ev10')
        ten=next(b for b in metrics if b['seed']==z['seed'] and b['scenario']==z['scenario'] and b['variant']=='tier10')
        paired.append(dict(seed=z['seed'],scenario=z['scenario'],variant=z['variant'],total_return_delta_vs_ev10=z['total_return']-base['total_return'],total_return_delta_vs_tier10=z['total_return']-ten['total_return'],mdd_delta_vs_ev10=z['mdd']-base['mdd']))
    for score in scores:
        for kind,key,uk in [('ev','confusion_ev','unknown_by_ev_tier'),('realized','confusion_realized','unknown_by_realized_tier')]:
            with (OUT/f"confusion_{score['seed']}_{score['scenario']}_{kind}.csv").open('w') as f:
                w=csv.writer(f);w.writerow(['true / predicted',*TIERS,'UNKNOWN'])
                for i,t in enumerate(TIERS):w.writerow([t,*score[key][i],score[uk][i]])
    assert all(sha(p)==h for p,h in before.items());assert sha(OUT/'preregister.json')==frozen
    report=dict(status='PASS' if all(z['status']=='PASS' for z in scores) else 'FAIL',execution_status='COMPLETE',full_portfolio_replays=attempts,elapsed_seconds=time.monotonic()-start,preregister_sha256=frozen,production_sources_unchanged=True,source_sha256=before,discrimination=scores,portfolio_runs=metrics,paired=paired,tapes=tapes,minimum_engineering_change='Add a horizon-specific causal outcome ledger for all eligible opportunities, date-clustered calibrated absolute net-EV intervals and explicit abstention at the manager admission seam; independently validate native PIT features across forward regimes before enabling five-tier claims or tier scaling.',limitations=['No production quality classifier exists at this seam; this is a frozen experiment-local estimator.','Frozen algorithm updates only with strictly matured realized outcomes; evaluation truth and oracle regimes never enter inference.','Synthetic noisy measurements are artificially informative in learnable/misleading; no historical or native-alpha claim.','Unannounced reversal is detectable only after delayed noisy outcomes; rolling detection cannot guarantee immediate safety.','EV ground truth is evaluator-only generative conditional mean; realized outcome tiers also reported separately.','SE intervals are date-clustered diagnostics; not formal simultaneous/dependence-robust coverage.','No terminal liquidation; NAV includes open positions and receivables, costs reported on executed fills.','Portfolio tests cover 126 sessions, four seeds; no statistical robustness claim.','Native funded-exit scale gates may prevent every scaled add; no fabricated fills.'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(report['status'],flush=True)

def sha_bytes(x):return hashlib.sha256(x).hexdigest()
if __name__=='__main__':main()

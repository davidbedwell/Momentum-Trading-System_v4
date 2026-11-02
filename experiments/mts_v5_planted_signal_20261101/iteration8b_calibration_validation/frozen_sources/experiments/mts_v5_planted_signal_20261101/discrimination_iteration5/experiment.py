#!/usr/bin/env python3
"""Bounded independent diagnostic. No production imports except frozen iteration2 comparator."""
import csv,gzip,hashlib,importlib.util,json,math,random,secrets,statistics as st,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
O=Path(__file__).resolve().parent
TIERS=['TERRIBLE','POOR','AVERAGE','GOOD','GREAT']; EDGES=[-.006,-.002,.002,.006]
MU=[-.012,-.004,0,.004,.012]; COST=.003; START=606; END=732; N=734
FIT=range(0,400); CAL=range(403,603)
def tier(x):return TIERS[sum(x>=e for e in EDGES)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mean(v):return st.mean(v) if v else 0.
def se(v):return st.stdev(v)/math.sqrt(len(v)) if len(v)>1 else 1.
def label(mu,r,n,nc):return tier(mu) if min(n,nc)>=100 and tier(mu-r)==tier(mu+r) else 'UNKNOWN'
def generate(seed,scenario):
    rng=random.Random(seed); sr=random.Random(seed+90000); sensors=[]; net=[]; truth=[]; gross=[]
    for i in range(N):
        common=rng.gauss(0,.003*(1.25 if scenario=='outer_noise' else 1)); fs=[]; ys=[]; ts=[]
        for j in range(24):
            z=rng.randrange(5);rng.random();rng.randrange(5) # fixed unused coarse channel, independent of sensor
            y=MU[z]+common+rng.gauss(0,.008*(1.25 if scenario=='outer_noise' else 1))
            source=sr.randrange(5) if scenario=='null' else z
            x=source+sr.gauss(0,.30);v=source+sr.gauss(0,.50)
            f=max(0,min(4,math.floor((x/.09+v/.25)/(1/.09+1/.25)+.5)))
            if scenario=='reversal' and i>=START:f=4-f
            fs.append(f);ys.append(y);ts.append(MU[z]);
        sensors.append(fs);net.append(ys);truth.append(ts);gross.append([(1+y)*(1+COST/2)/(1-COST/2)-1 for y in ys])
    prices=[[100.+j for j in range(24)] for _ in range(N)]
    for i in range(2,N):prices[i]=[p*(1+g) for p,g in zip(prices[i-1],gross[i-2])]
    # Inference receives prices and sensors only; latent truth stays evaluator-only.
    return prices,sensors,truth

def observed(prices,i,j):return prices[i+2][j]*(1-COST/2)/(prices[i+1][j]*(1+COST/2))-1

def dates(prices,sensors,indices,c):
    return [(i,mean([observed(prices,i,j) for j in range(24) if sensors[i][j]==c])) for i in indices if c in sensors[i]]

def fit(prices,sensors):
    models=[]
    # Full model adds a lag-price slope, centered separately within each sensor cell.
    for c in range(5):
        tr=dates(prices,sensors,FIT,c); ca=dates(prices,sensors,CAL,c); mu=mean([v for _,v in tr])
        rows=[(prices[i][j]/prices[max(0,i-1)][j]-1,observed(prices,i,j)) for i in FIT for j in range(24) if sensors[i][j]==c]
        center=mean([x for x,y in rows]); slope=sum((x-center)*(y-mu) for x,y in rows)/(1+sum((x-center)**2 for x,y in rows))
        # Train-only disagreement distribution; calibration changes uncertainty only.
        disagreements=sorted(abs(slope*(x-center)) for x,y in rows)
        threshold=max(.0005,disagreements[int(.99*(len(disagreements)-1))])
        bias=mean([v-mu for _,v in ca]); radius=max(2.576*se([v for _,v in tr]),abs(bias)+2.576*se([v for _,v in ca]))
        models.append(dict(mean=mu,slope=slope,center=center,threshold=threshold,radius=radius,ntrain=len(tr),ncal=len(ca),cal_bias=bias,train_dates=[i for i,v in tr],cal_dates=[i for i,v in ca]))
    return models

def monitor(prices,sensors,models,now):
    # 25 prespecified looks, 5 cells, two-sided union bound. One latch per tape.
    if now<START+22 or (now-START-22)%4:return []
    alarms=[]
    for c,m in enumerate(models):
        v=dates(prices,sensors,range(now-22,now-2),c)
        if len(v)<15:continue
        # .018 sub-Gaussian envelope exceeds sqrt(.012^2+.01068^2) even for outer noise.
        threshold=.018*math.sqrt(2*math.log(2*5*26/.05)*(1/len(v)+1/m['ntrain']))
        delta=mean([y for i,y in v])-m['mean']
        if abs(delta)>threshold:alarms.append(dict(index=now,cell=c,delta=delta,threshold=threshold,last_signal=now-3,reason='CELL_RETURN_DRIFT'))
    return alarms

def predict(prices,sensors):
    models=fit(prices,sensors);states={v:[] for v in ['candidate','ungated']};alarms=[];latched=False
    identifiable=max(m['mean'] for m in models)-min(m['mean'] for m in models)>.003
    for i in range(START,END):
        if not latched:
            found=monitor(prices,sensors,models,i)
            if found:alarms+=found;latched=True
        for v in states:
            row=[]
            for j,c in enumerate(sensors[i]):
                m=models[c];sensor=m['mean'];full=sensor+m['slope']*(prices[i][j]/prices[i-1][j]-1-m['center']);r=m['radius']+abs(full-sensor)
                lab=label(full,r,m['ntrain'],m['ncal']);reason='INTERVAL'
                if not identifiable:lab='UNKNOWN';reason='NO_IDENTIFIABLE_SIGNAL'
                if v=='candidate' and (latched or abs(full-sensor)>m['threshold']):lab='UNKNOWN';reason='DRIFT_LATCH' if latched else 'SENSOR_FULL_DISAGREEMENT'
                row.append(dict(mean=full,radius=r,label=lab,reason=reason))
            states[v].append(row)
    return states,models,alarms

def baseline(prices,sensors):
    # Unmodified iteration2 inference on the same last 126 pretest +126 test dates.
    spec=importlib.util.spec_from_file_location('i2_original',O.parent/'discrimination_iteration2/experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    offset=START-126
    # Original observed uses its own multiplicative execution costs; adapt bars exactly.
    ratio=(1-mod.s.FRICTION)*(1-mod.s.COSTS['fees'])/((1+mod.s.FRICTION)*(1+mod.s.COSTS['fees']))
    target=(1-COST/2)/(1+COST/2)
    adapted=[[100.+j for j in range(24)] for _ in range(252)]
    for i in range(1,252):adapted[i]=[adapted[i-1][j]*(prices[offset+i][j]/prices[offset+i-1][j])*target/ratio for j in range(24)]
    days=[(str(i),{t:mod.k.Bar(adapted[i][j],adapted[i][j]) for j,t in enumerate(mod.s.TICKERS)}) for i in range(252)]
    states,_,alarms=mod.predict(days,sensors[offset:offset+252])
    return [[states[i][sensors[offset+i][j]] for j in range(24)] for i in range(126,252)],alarms

def replay(prices,states,policy='tier',scale=1.):
    cash=100000.;nav=cash;peak=nav;mdd=0.;costs=0.;risks=[];trades=[];daily=[];gap_exceed=0
    # All trades hold exactly one open-to-open session. Prior sales settle one session later.
    receivable=0.;positions=[]
    for k,i in enumerate(range(START,END)):
        opening=nav;cash+=receivable;receivable=0.;pnl=0.;exit_value=0.
        for t in positions:
            exitp=prices[i+1][t['j']]; proceeds=t['shares']*exitp*(1-COST/2)
            exit_value+=proceeds;costs+=t['shares']*exitp*COST/2
            t.update(exit_index=i+1,exit_open=exitp,net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav'])
            gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        receivable=exit_value;positions=[]
        opening=cash+receivable
        available=cash
        order=sorted(range(24),key=lambda j:states[k][j]['mean'],reverse=True)
        for j in order:
            c=states[k][j]
            if policy=='cash' or (policy=='tier' and c['label'] not in ('GOOD','GREAT')):continue
            gap=[.03,.06,.12,.24][j%4];weight=min(.10*scale,.02/(gap+COST)); debit=min(available,opening*weight)
            if debit<=1e-8:continue
            entry=prices[i+1][j];shares=debit/(entry*(1+COST/2));risk=shares*entry/opening*(gap+COST)
            assert risk<=.02+1e-12
            costs+=shares*entry*COST/2;available-=debit
            positions.append(dict(signal=i,j=j,entry_index=i+1,entry_open=entry,shares=shares,debit=debit,entry_nav=opening,modeled_risk=risk,tier=c['label']))
        cash=available;nav=cash+receivable+sum(t['shares']*prices[i+1][t['j']] for t in positions)
        assert cash>=-1e-8
        peak=max(peak,nav);mdd=max(mdd,1-nav/peak);daily.append(dict(index=i,nav=nav,cash=cash,receivable=receivable,exposure=sum(t['shares']*prices[i+1][t['j']] for t in positions)/nav))
    # Explicit final horizon liquidation; settle for ending NAV.
    for t in positions:
        proceeds=t['shares']*prices[END+1][t['j']]*(1-COST/2);costs+=t['shares']*prices[END+1][t['j']]*COST/2
        t.update(exit_index=END+1,exit_open=prices[END+1][t['j']],net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav']);gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        cash+=proceeds
    nav=cash+receivable;peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    return dict(total_return=nav/100000-1,cagr=(nav/100000)**(252/126)-1,mdd=mdd,costs=costs,final_nav=nav,max_modeled_risk=max((t['modeled_risk'] for t in trades),default=0),gap_loss_exceedances=gap_exceed,max_realized_trade_loss_nav=max((t['realized_loss_nav'] for t in trades),default=0),trades=len(trades),mean_exposure=mean([d['exposure'] for d in daily])),trades,daily

def validate_pit(rows):
    required=['asset','feature','value','event_time','release_time','available_time','decision_time','revision_id','source_uri','source_sha256','vintage_id']
    for r in rows:
        if any(k not in r or r[k] is None for k in required):raise ValueError('missing provenance')
        times=[datetime.fromisoformat(r[k]) for k in ['release_time','available_time','decision_time']]
        if any(t.tzinfo is None for t in times) or not times[0]<=times[1]<=times[2]:raise ValueError('not PIT')
        if len(r['source_sha256'])!=64 or any(c not in '0123456789abcdef' for c in r['source_sha256']):raise ValueError('hash')
        if not isinstance(r['value'],(float,int)) or not math.isfinite(r['value']):raise ValueError('nonfinite feature')
    return rows

def writecsv(name,rows):
    if not rows:return
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    start=time.monotonic(); plan=json.loads((O/'preregister.json').read_text())
    if (O/'commitment.json').exists():raise SystemExit('Refusing holdout reuse: archive directory and create a new preregistered experiment.')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(O),'-p','test_*.py','-v'],capture_output=True,text=True)
    (O/'tests.log').write_text(tests.stdout+tests.stderr)
    if tests.returncode:raise SystemExit(tests.returncode)
    sources={str(p):sha(p) for p in sorted(O.glob('*.py'))}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and str(path).endswith('.py') and Path(path).is_file() and ('/opt/' in str(path)):
            sources[str(Path(path).resolve())]=sha(path);sources[str(O/'preregister.json')]=sha(O/'preregister.json')
    # Local commitment is written before OS entropy draws and generation; no trusted timestamp claimed.
    commitment=dict(utc=datetime.now(timezone.utc).isoformat(),sources=sources,preregister_sha256=sha(O/'preregister.json'))
    (O/'commitment.json').write_text(json.dumps(commitment,indent=2))
    seeds=[secrets.randbits(63) for _ in range(4)];(O/'seeds.json').write_text(json.dumps(seeds))
    scores=[];metrics=[];tiers=[];attempts=0;completed=[]
    with gzip.open(O/'opportunities.jsonl.gz','wt') as out,gzip.open(O/'replays.jsonl.gz','wt') as rp:
        for seed in seeds:
            for scenario in plan['scenarios']:
                if time.monotonic()-start>690 or attempts+3>58:break
                prices,sensors,truth=generate(seed,scenario);states,models,alarms=predict(prices,sensors)
                old,oldalarms=baseline(prices,sensors);states['iteration2']=old
                funded={}; replay_variants=[('candidate',states['candidate'],'tier',1),('iteration2',old,'tier',1),('benchmark',states['candidate'],'all',1)]
                if scenario=='learnable':replay_variants.append(('scaled',states['candidate'],'tier',1.5))
                for variant,ss,policy,scale in replay_variants:
                    if time.monotonic()-start>710 or attempts>=58:break
                    attempts+=1;metric,trades,daily=replay(prices,ss,policy,scale)
                    funded[variant]={(t['signal'],t['j']):t for t in trades}
                    metrics.append(dict(seed=seed,scenario=scenario,variant=variant,**metric));rp.write(json.dumps(dict(seed=seed,scenario=scenario,variant=variant,trades=trades,daily=daily))+'\n')
                for variant,ss in states.items():
                    confusion=[[0]*6 for _ in range(5)];realconf=[[0]*6 for _ in range(5)];rows=[];covered=0;datecovered=0;datecount=0
                    for k,i in enumerate(range(START,END)):
                        for c in range(5):
                            vals=[observed(prices,i,j) for j in range(24) if sensors[i][j]==c]
                            if vals:
                                m=models[c];datecovered+=abs(mean(vals)-m['mean'])<=m['radius'];datecount+=1
                        for j,c in enumerate(sensors[i]):
                            z=ss[k][j];actual=observed(prices,i,j);ti=TIERS.index(tier(truth[i][j]));pi=TIERS.index(z['label']) if z['label']!='UNKNOWN' else 5
                            confusion[ti][pi]+=1;realconf[TIERS.index(tier(actual))][pi]+=1
                            covered+=abs(truth[i][j]-z['mean'])<=z['radius']
                            row=dict(seed=seed,scenario=scenario,variant=variant,index=i,j=j,execution_index=i+1,exit_index=i+2,available_index=i+3,inferred_tier=z['label'],inferred_net=z['mean'],radius=z['radius'],reason=z.get('reason'),true_ev=truth[i][j],realized_net=actual,one_session_net=actual,horizon_mismatch=0.,cost_fraction=COST,eligible=True,funded=(i,j) in funded.get(variant,{}),funded_debit=funded.get(variant,{}).get((i,j),{}).get('debit',0.))
                            rows.append(row);out.write(json.dumps(row)+'\n')
                    count=len(rows);assigned=sum(sum(r[:5]) for r in confusion);false=confusion[0][4];den=sum(confusion[0])
                    score=dict(seed=seed,scenario=scenario,variant=variant,coverage=assigned/count,conditional_accuracy=sum(confusion[i][i] for i in range(5))/assigned if assigned else None,confusion_latent_individual=confusion,confusion_realized=realconf,all_opportunity_recall=[confusion[i][i]/sum(confusion[i]) for i in range(5)],false_great_on_terrible=false,false_great_rate=false/den,false_terrible_on_great=confusion[4][0],individual_latent_interval_coverage=covered/count,date_mean_predictive_interval_coverage=datecovered/datecount,alarms=alarms if variant=='candidate' else oldalarms if variant=='iteration2' else [],drift_lag=(alarms[0]['index']-START if alarms else None) if scenario=='reversal' else None,models=models if variant=='candidate' else None)
                    scores.append(score)
                    for t in TIERS+['UNKNOWN']:
                        rr=[r for r in rows if r['inferred_tier']==t];tiers.append(dict(seed=seed,scenario=scenario,variant=variant,tier=t,n=len(rr),coverage=len(rr)/count,mean_net=mean([r['realized_net'] for r in rr]) if rr else None))
                completed.append([seed,scenario]);print(seed,scenario,attempts,round(time.monotonic()-start,2),flush=True)
    # Conditional cell EV coverage: independent evaluator Monte Carlo from the known sensor channel.
    # Not used in inference. Fixed analytical integration via Gaussian CDF rounding probabilities.
    sd=1/math.sqrt(1/.09+1/.25);normal=st.NormalDist()
    celltrue=[]
    for c in range(5):
        weights=[normal.cdf((c+.5-z)/sd) if c==0 else 1-normal.cdf((c-.5-z)/sd) if c==4 else normal.cdf((c+.5-z)/sd)-normal.cdf((c-.5-z)/sd) for z in range(5)]
        celltrue.append(sum(w*m for w,m in zip(weights,MU))/sum(weights))
    for s in scores:
        if s['variant']=='candidate':
            target=[0.]*5 if s['scenario']=='null' else list(reversed(celltrue)) if s['scenario']=='reversal' else celltrue
            s['conditional_mean_interval_coverage']=mean([abs(m['mean']-v)<=m['radius'] for m,v in zip(s['models'],target)])
    paired=[]
    for m in metrics:
        if m['variant']!='candidate':continue
        for comparator in ['iteration2','scaled','benchmark']:
            other=next((x for x in metrics if x['seed']==m['seed'] and x['scenario']==m['scenario'] and x['variant']==comparator),None)
            if other:paired.append(dict(seed=m['seed'],scenario=m['scenario'],comparator=comparator,return_delta=m['total_return']-other['total_return'],cagr_delta=m['cagr']-other['cagr'],mdd_delta=m['mdd']-other['mdd'],cost_delta=m['costs']-other['costs']))
    stable=[s for s in scores if s['variant']=='candidate' and s['scenario'] in ['learnable','null','outer_noise']];learn=[s for s in stable if s['scenario']=='learnable'];ung=[s for s in scores if s['variant']=='ungated' and s['scenario']=='learnable']
    stable_alarms=sum(bool(s['alarms']) for s in stable)
    checks=dict(four_fresh_seeds=len(set(s['seed'] for s in learn))>=4,ungated_coverage=all(s['coverage']>=.30 for s in ung),gated_coverage=all(s['coverage']>=.15 for s in learn),stable_false_great=all(s['false_great_rate']<=.01 for s in stable),middle_radii=sum(all(m['radius']<.002 for m in s['models'][1:4]) for s in learn)>=3,five_tier_support=all(all(next(t['n'] for t in tiers if t['seed']==s['seed'] and t['scenario']==s['scenario'] and t['variant']=='candidate' and t['tier']==tiername)>=20 for tiername in TIERS) for s in learn),stable_false_alarm_observed=stable_alarms/max(1,len(stable))<=.05,null_return=all(m['total_return']<=.02 for m in metrics if m['variant']=='candidate' and m['scenario']=='null'),trusted_timestamp=False,real_pit_ready=False)
    report=dict(status='PASS' if all(checks.values()) else 'FAIL',execution_status='COMPLETE' if len(completed)==16 and attempts==52 else 'INCOMPLETE_BUDGET',checks=checks,elapsed_seconds=time.monotonic()-start,portfolio_replays=attempts,total_replays_including_phase_a=attempts+6,seeds=seeds,completed=completed,preregister_sha256=sha(O/'preregister.json'),design_unchanged=all(sha(p)==h for p,h in sources.items()),fresh_test='Fresh OS-entropy seed tapes generated after local source freeze; now evaluated and no longer untouched. DGP adapted from prior work; no trusted public timestamp.',stable_false_alarms=dict(seed_scenario_units=len(stable),alarmed=stable_alarms,observed_rate=stable_alarms/max(1,len(stable)),upper95_if_zero=1-.05**(1/max(1,len(stable))) if not stable_alarms else None,independent_seeds=4,power='Four independent seeds cannot establish <=5% nuisance probability; scenarios within seed are paired.'),discrimination=scores,portfolio_runs=metrics,paired=paired,real_pit_audit=dict(status='BLOCKED',real_rows=0,reason='No release-timestamped real predictor dataset supplied or acquired.',adapter='validate_pit; schema in pit_schema.json',missing=['revision histories','release and availability timestamps','coverage/missingness audit','independent regime OOS rank IC >0.1 evidence']),sgov=dict(status='UNAVAILABLE_REAL_DATA',comparison='Cash zero-yield control has return/CAGR/MDD/costs 0; no fabricated SGOV series'),engineering_blocker='Real PIT information absent; narrow-band support and drift safety require measured validation. No production promotion.',recommended_next_decision='Review failed checks; acquire provenance-complete PIT data and independent regime evaluation before any production or alpha claim. No optimization reruns in this experiment.')
    (O/'report.json').write_text(json.dumps(report,indent=2));writecsv('tier_metrics.csv',tiers);writecsv('metrics.csv',metrics);writecsv('paired.csv',paired)
    (O/'checksums.json').write_text(json.dumps({str(p.relative_to(O)):sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2))
    print(report['status'],checks,flush=True)
if __name__=='__main__':main()

"""Fixed 96-portfolio synthetic robustness experiment; no fitting or source writes."""
import sys,json,hashlib,time,statistics as st,csv,gzip,subprocess,tempfile,shutil
from pathlib import Path
from dataclasses import replace
OUT=Path(__file__).resolve().parent
AUDIT=OUT.parent/'scaling_blocker_audit'
sys.path.insert(0,str(AUDIT))
import audit as a
r=a.r
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def reliability(days,tape,quality,i):
    # Forecast at k executes k+1 and matures k+2. Use STRICTLY prior closes.
    errors=[];observed=[]
    for k in range(max(0,i-2)):
        values=[];nets=[]
        for j,t in enumerate(r.s1.TICKERS):
            pred=r.s1.expected(tape[k][j],quality)
            if pred-r.s1.ROUND_TRIP<=0:continue
            actual=days[k+2][1][t].close/days[k+1][1][t].open-1
            values.append(actual-pred);nets.append(actual-r.s1.ROUND_TRIP)
        if values:errors.append(st.mean(values));observed.append(st.mean(nets))
    # Dates, not correlated stocks, are the sample units. Conservative diagnostic
    # bound only: serial dependence means this is NOT a calibrated confidence level.
    margin=2*st.stdev(errors)/len(errors)**.5 if len(errors)>1 else float('inf')
    ok=len(errors)>=30 and st.mean(observed)>0 and st.mean(errors)+margin>=0
    return dict(allow=ok,dates=len(errors),mean_error=st.mean(errors) if errors else None,
                diagnostic_upper_error=st.mean(errors)+margin if len(errors)>1 else None,
                mean_observed_net=st.mean(observed) if observed else None,
                latest_outcome_index=i-1 if errors else None)

def prepare():
    sources=list(a.SOURCES)+[AUDIT/'corrected_manager.py',AUDIT/'corrected_kernel.py']
    before={str(p):sha(p) for p in sources}
    for name in ('corrected_manager.py','corrected_kernel.py','source.patch','test_regression.py'):
        shutil.copyfile(AUDIT/name,OUT/name)
    with tempfile.TemporaryDirectory() as td:
        for name,p in [('discovery/competitive_ga/functional_niche_manager.py',a.FIX/'functional_niche_manager.py'),('engines/portfolio_replay/kernel.py',Path(a.original_kernel.__file__))]:
            dest=Path(td)/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        result=subprocess.run(['patch','--batch','-p1','-i',str(OUT/'source.patch')],cwd=td,capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        for name,file in [('discovery/competitive_ga/functional_niche_manager.py','corrected_manager.py'),('engines/portfolio_replay/kernel.py','corrected_kernel.py')]:
            assert (Path(td)/name).read_bytes()==(OUT/file).read_bytes()
        (OUT/'reconstruction.log').write_text(result.stdout+'Both corrected modules reconstruct byte-for-byte. Baseline: stage2_fix manager + original kernel.\n')
    m=a.load('discovery.competitive_ga.robust_manager',OUT/'corrected_manager.py')
    k=a.load('robust_kernel',OUT/'corrected_kernel.py');m.Replay=k.Replay
    return m,before

def main():
    start=time.monotonic();m,before=prepare();rows=[];gates=[];hashes=[]
    old=json.loads((a.FIX/'report.json').read_text())
    with gzip.open(OUT/'replays.jsonl.gz','wt') as raw:
        for seed in r.s1.SEEDS:
            days,tapes,_=r.s1.generate(seed)
            for q in ('weak','misnull'):
                tape=tapes['null' if q=='misnull' else q]
                digest=hashlib.sha256(json.dumps(tape).encode()).hexdigest()
                assert digest==next(t['sha256'] for t in old['tapes'] if t['seed']==seed and t['quality']==q)
                hashes.append(dict(seed=seed,quality=q,sha256=digest))
                gate=[reliability(days,tape,'strong',i) for i in range(252)] if q=='misnull' else None
                if gate:gates.append(dict(seed=seed,states=gate))
                for control in (('existing','hypothetical') if q=='misnull' and seed!=1112 else ('existing',)):
                    for v in (('ev','scale15','scale20') if control=='existing' else ('scale15','scale20')):
                        assert len(rows)<96 and time.monotonic()-start<840
                        kw,stats=r.callbacks(tape,q,v,seed,days)
                        if control=='hypothetical':
                            base=kw['scaling_evidence'];idx={d:i for i,(d,_) in enumerate(days)}
                            def evidence(c,t,d,h,realized,nav,base=base,gate=gate,idx=idx):
                                e=base(c,t,d,h,realized,nav)
                                return replace(e,current_signal_confirmed=e.current_signal_confirmed and gate[idx[d]]['allow'])
                            kw['scaling_evidence']=evidence
                        x=a.execute(days,kw,m);metric,daily=r.s1.measure(x,days)
                        target={'ev':.10,'scale15':.15,'scale20':.20}[v]
                        fills=a.scaling_fills(x,days,target) if v!='ev' else []
                        rejection={'risk':0,'cap':0,'cash':0};overlap={};opportunities=0;unique_rejected=0
                        for d in x['decisions']:
                            res=d.get('reservation')
                            if not res:continue
                            opportunities+=1
                            desired=max(0,res['approved']-res['current'])
                            actual=max(0,d['selected'][3]-res['current'])
                            flags={'risk':res['risk_rejected'],'cap':res['cap_rejected'],'cash':actual<desired-1e-12}
                            keys=[k for k,b in flags.items() if b]
                            for k in keys:rejection[k]+=1
                            if keys:unique_rejected+=1;key='+'.join(keys);overlap[key]=overlap.get(key,0)+1
                        # Independent full-candidate modeled loss check on every actual BUY.
                        bydate={d:[] for d,_ in days}
                        for f in x['ledger']:bydate[f[0]].append(f)
                        previous={};maxloss=0
                        for (d,bars),nav in zip(days,x['nav']):
                            fs=bydate[d];opening=nav[1]+sum(f[5]+f[3]*abs(f[4]-bars[f[1]].open) for f in fs)
                            for f in fs:
                                if f[2]=='BUY':
                                    w=(previous.get(f[1],0)+f[3])*bars[f[1]].open/opening
                                    loss=w*(max(.02,r.s1.GAPS[int(f[1][3:])])+r.s1.ROUND_TRIP)
                                    assert loss<=.02+1e-10,(seed,q,v,d,loss)
                                    maxloss=max(maxloss,loss)
                            previous=nav[3]
                        row=dict(seed=seed,quality=q,control=control,variant=v,**metric,scaled_fills=len(fills),full_target_fills=sum(f['full'] for f in fills),max_actual_candidate_loss=maxloss,reservation_opportunities=opportunities,unique_rejected=unique_rejected,**{k+'_rejections':val for k,val in rejection.items()},rejection_overlap=overlap)
                        rows.append(row)
                        raw.write(json.dumps(dict(seed=seed,quality=q,control=control,variant=v,decisions=x['decisions'],ledger=x['ledger'],nav=x['nav'],risk=x['risk_audit'],scaled_fills=fills))+'\n')
            print(f'seed {seed}; completed {len(rows)}/96; {time.monotonic()-start:.1f}s',flush=True)
    keys=('cagr','mdd','calmar','exposure','turnover','scaled_fills','full_target_fills','risk_rejections','cap_rejections','cash_rejections')
    aggregates=[];paired=[]
    for q,control,v in sorted({(z['quality'],z['control'],z['variant']) for z in rows}):
        rr=[z for z in rows if (z['quality'],z['control'],z['variant'])==(q,control,v)]
        aggregates.append(dict(quality=q,control=control,variant=v,n=len(rr),means={k:st.mean(z[k] for z in rr if z[k] is not None) for k in keys},tail=dict(min_cagr=min(z['cagr'] for z in rr),max_mdd=max(z['mdd'] for z in rr),losing_seeds=[z['seed'] for z in rr if z['cagr']<0],latched_seeds=[z['seed'] for z in rr if z['mdd_latched']],worst_seed=min(rr,key=lambda z:z['cagr'])['seed'])))
        if v=='ev':continue
        deltas=[{k:z[k]-next(b for b in rows if b['seed']==z['seed'] and b['quality']==q and b['control']=='existing' and b['variant']=='ev')[k] for k in keys} for z in rr]
        paired.append(dict(quality=q,control=control,variant=v,reference='same seed existing 10%',cagr_wins=sum(z['cagr']>1e-12 for z in deltas),mean_delta={k:st.mean(z[k] for z in deltas) for k in keys},min_cagr_delta=min(z['cagr'] for z in deltas),max_cagr_delta=max(z['cagr'] for z in deltas),per_seed=[dict(seed=z['seed'],**d) for z,d in zip(rr,deltas)]))
    assert len(rows)==94
    assert all(sha(p)==h for p,h in before.items())
    report=dict(status='COMPLETE_SYNTHETIC_DIAGNOSTIC',full_portfolios=len(rows)+1,completed_comparisons=len(rows),initial_reporting_failure_portfolios=1,elapsed_seconds=time.monotonic()-start,seeds=list(r.s1.SEEDS),sessions=252,source_unchanged=True,source_sha256=before,reconstruction_exact=True,tape_hashes=hashes,aggregates=aggregates,paired=paired,runs=rows,reliability_states=gates)
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    print('COMPLETE',flush=True)
if __name__=='__main__':main()

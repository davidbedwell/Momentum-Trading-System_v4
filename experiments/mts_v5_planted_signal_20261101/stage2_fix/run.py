#!/usr/bin/env python3
import support as r
import hashlib,json,time,statistics as st,csv,subprocess
from pathlib import Path
from engines.portfolio_replay.kernel import Replay,Signal,Bar
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.monotonic(); rows=[];tapes=[]; executions=[]
    paths=[Path(r.original.__file__),r.ROOT/'engines/portfolio_replay/kernel.py',r.ROOT/'discovery/competitive_ga/progressive_scaling.py']
    before={str(p):sha(p) for p in paths}
    oldreport=json.loads((OUT.parent/'stage2/report.json').read_text())
    assert before==oldreport['source_sha256']
    oldrows=list(csv.DictReader((OUT.parent/'stage2/runs.csv').open()))
    # Two sanity portfolios: T+1 sale proceeds cannot fund same-day purchase;
    # and MDD latch must preserve native exits.
    bars={'A':Bar(100,100),'B':Bar(100,100)}
    p=Replay(cash=0,shares={'A':1000},high_water=100000,settlement_sessions=1,**r.s1.COSTS)
    p.pending=[Signal('A','GA7','a',0),Signal('B','GA7','b',.1,stop_distance=.02,gap_risk=.03)]
    p.day('2030-01-02',bars);assert not p.shares and p.cash==0 and p.unsettled
    p.pending=[Signal('B','GA7','b',.1,stop_distance=.02,gap_risk=.03)]
    p.day('2030-01-03',bars);assert 'B' in p.shares and not p.unsettled
    p=Replay(cash=20000,shares={'A':800},high_water=100000,**r.s1.COSTS)
    p.pending=[Signal('B','GA7','b',.1,stop_distance=.02,gap_risk=.03)]
    p.day('2030-01-02',{'A':Bar(50,50),'B':bars['B']});assert p.admission_halted and 'B' not in p.shares
    p.pending=[Signal('A','GA7','a',0)];p.day('2030-01-03',bars);assert not p.shares
    for seed in r.s1.SEEDS:
        assert time.monotonic()-start<800
        days,tt,_=r.s1.generate(seed)
        for q in r.QUALITIES:
            tape=tt['null' if q=='misnull' else q]
            h=hashlib.sha256(json.dumps(tape).encode()).hexdigest()
            assert h==next(t['sha256'] for t in oldreport['tapes'] if t['seed']==seed and t['quality']==q)
            tapes.append(dict(seed=seed,quality=q,sha256=h))
            for v in ('ev','scale15','scale20'):
                kw,stats=r.callbacks(tape,q,v,seed,days)
                x=r.execute(days,kw);mm,daily=r.s1.measure(x,days)
                if v=='ev':
                    old=next(z for z in oldrows if int(z['seed'])==seed and z['quality']==q and z['variant']=='ev')
                    for k in ('cagr','mdd','exposure','turnover','final_nav'):assert abs(mm[k]-float(old[k]))<1e-10,(seed,q,k)
                audits=[a['reservation'] for a in x['decisions'] if 'reservation' in a]
                cap=sum(a['cap_rejected'] for a in audits);risk=sum(a['risk_rejected'] for a in audits)
                fills=0;full=0;maxweight=0
                prev_nav=100000.;prev_shares={};prev_prices={}
                for i,((d,bars),nav) in enumerate(zip(days,x['nav'])):
                    oe=prev_nav+sum(z*(bars[t].open-prev_prices[t]) for t,z in prev_shares.items())
                    for f in x['ledger']:
                        if f[0]!=d or f[2]!='BUY':continue
                        t=f[1];w=(prev_shares.get(t,0)+f[3])*bars[t].open/oe
                        if t in prev_shares and w>.10001:
                            fills+=1;maxweight=max(maxweight,w)
                            full+=int(w>= (.15 if v=='scale15' else .20)-1e-9)
                            executions.append(dict(seed=seed,quality=q,variant=v,date=d,ticker=t,weight=w,quantity=f[3],price=f[4],fee=f[5]))
                    prev_nav=nav[1];prev_shares=nav[3];prev_prices={t:b.close for t,b in bars.items()}
                rows.append(dict(seed=seed,quality=q,variant=v,**mm,**stats,cap_rejections=cap,risk_rejections=risk,executed_scale_fills=fills,full_target_fills=full,max_executed_weight=maxweight))
                if seed==1101:
                    r.write(f'{q}_{v}_daily.csv',daily)
                    r.write(f'{q}_{v}_fills.csv',[dict(date=f[0],ticker=f[1],side=f[2],quantity=f[3],price=f[4],fee=f[5]) for f in x['ledger']])
                    (OUT/f'{q}_{v}_audit.json').write_text(json.dumps(x['decisions']))
        print(f'seed {seed}: {len(rows)} comparisons; {time.monotonic()-start:.1f}s',flush=True)
    agg=[];paired=[]
    for q in r.QUALITIES:
        for v in ('ev','scale15','scale20'):
            rr=[a for a in rows if a['quality']==q and a['variant']==v]
            agg.append(dict(quality=q,variant=v,n=12,**{k:st.mean(a[k] for a in rr) for k in ('cagr','mdd','exposure','turnover')},**{k:sum(a[k] for a in rr) for k in ('cap_rejections','risk_rejections','executed_scale_fills','full_target_fills')}))
            if v!='ev':
                dd={k:[] for k in ('cagr','mdd','exposure','turnover')}
                for a in rr:
                    b=next(z for z in rows if z['seed']==a['seed'] and z['quality']==q and z['variant']=='ev')
                    for k in dd:dd[k].append(a[k]-b[k])
                paired.append(dict(quality=q,variant=v,n=12,**{k+'_delta':st.mean(z) for k,z in dd.items()}))
    assert all(sha(p)==before[str(p)] for p in paths)
    # Validate BOTH original -> Stage2 and original -> exact tested fix locally.
    import difflib,tempfile
    original=Path(r.original.__file__).read_text();fixed=(OUT/'functional_niche_manager.py').read_text()
    patch=''.join(difflib.unified_diff(original.splitlines(True),fixed.splitlines(True),fromfile='a/discovery/competitive_ga/functional_niche_manager.py',tofile='b/discovery/competitive_ga/functional_niche_manager.py'))
    (OUT/'source.patch').write_text(patch)
    reconstruction={}
    for label,patchpath,target in [('stage2',OUT.parent/'stage2/source.patch',OUT.parent/'stage2/functional_niche_manager.py'),('stage2_fix',OUT/'source.patch',OUT/'functional_niche_manager.py')]:
        with tempfile.TemporaryDirectory(dir='/tmp') as td:
            dst=Path(td)/'discovery/competitive_ga/functional_niche_manager.py';dst.parent.mkdir(parents=True);dst.write_text(original)
            proc=subprocess.run(['patch','--batch','-p1','-i',str(patchpath)],cwd=td,capture_output=True,text=True)
            assert proc.returncode==0 and dst.read_bytes()==target.read_bytes()
            reconstruction[label]=dict(sha256=sha(dst),exact=True,patch_output=proc.stdout)
    r.write('runs.csv',rows);r.write('aggregate.csv',agg);r.write('paired.csv',paired);r.write('executed_scaling.csv',executions)
    blocked=not all(a['full_target_fills'] for a in agg if a['variant']!='ev')
    report=dict(status='STOP_SCALING_BLOCKED_NO_PERFORMANCE_CLAIMS' if blocked else 'BOUNDED_COMPLETE_SYNTHETIC_ONLY',comparison_portfolios=108,regression_replays=7,sanity_portfolios=2,total_replays=118,discarded_probe_attempts=1,hard_cap=120,elapsed_seconds=time.monotonic()-start,seeds=list(r.s1.SEEDS),sessions=252,aggregates=agg,paired=paired,tapes=tapes,baseline_identical_to_stage2=True,source_sha256=before,source_unchanged=True,reconstruction=reconstruction,tests=dict(pre_fix_expected_failures=2,fixed_passes=5),sanity_probes=['T+1 settlement','MDD latch preserves exits'],scaling_blocked=blocked,limits=['Synthetic diagnostics only; no historic-alpha or investment performance claim.','Evidence endogenous; aggregate other-position risk often exhausts 2% budget.','Execution-time kernel checks retained. Close reservation uses current prices; future gaps can change funding.','2% modeled loss is not a guaranteed loss bound. Ordinary admission gate is per position.','No GA, parameter search, source application, or terminal liquidation.'])
    report['artifact_sha256']={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name not in ('report.json','execution.log','README.md')}
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(status=report['status'],aggregates=agg),indent=2))
if __name__=='__main__':main()

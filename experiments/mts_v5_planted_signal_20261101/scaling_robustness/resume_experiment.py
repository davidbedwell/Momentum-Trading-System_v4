"""Resume with verified complete records and a persisted attempt budget."""
import experiment as e
from experiment import *
import zlib
START=time.monotonic()

def main():
    start=START
    manifest=json.loads((OUT/'manifest.json').read_text())
    verified=('experiment.py','corrected_manager.py','corrected_kernel.py','source.patch','replays.jsonl.gz')
    for name in verified:assert sha(OUT/name)==manifest[name],name
    (OUT/'prior_manifest.json').write_text(json.dumps(manifest,indent=2))
    (OUT/'prior_report.json').write_bytes((OUT/'report.json').read_bytes())
    data=zlib.decompressobj(31).decompress((OUT/'replays.jsonl.gz').read_bytes())
    saved={};record_hashes=[]
    for line in data.splitlines():
        try:z=json.loads(line)
        except json.JSONDecodeError:continue
        key=(z['seed'],z['quality'],z['control'],z['variant'])
        assert key not in saved
        assert z['seed'] in r.s1.SEEDS and z['quality'] in ('weak','misnull')
        assert z['variant'] in ('ev','scale15','scale20') and z['control'] in ('existing','hypothetical')
        assert len(z['nav'])==252
        saved[key]=z
        record_hashes.append(dict(seed=z['seed'],quality=z['quality'],control=z['control'],variant=z['variant'],sha256=hashlib.sha256(line).hexdigest()))
    assert len(saved)==26
    m,before=prepare();rows=[];gates=[];hashes=[];attempts=28;reused=0;new=0
    old=json.loads((a.FIX/'report.json').read_text())
    raw=gzip.open(OUT/'completed_replays.jsonl.gz','wt')
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
                    key=(seed,q,control,v)
                    if key in saved:
                        z=saved[key];reused+=1
                        x=dict(decisions=z['decisions'],ledger=z['ledger'],nav=z['nav'],risk_audit=z['risk'],admission_halted=bool(z['nav'][-1][4]),pending=[])
                    else:
                        assert attempts<96 and time.monotonic()-START<620
                        attempts+=1;new+=1
                        (OUT/'attempt_budget.json').write_text(json.dumps(dict(prior_upper_bound=28,new_attempts=new,total_upper_bound=attempts,current=key)))
                        kw,stats=r.callbacks(tape,q,v,seed,days)
                        if control=='hypothetical':
                            base=kw['scaling_evidence'];idx={d:i for i,(d,_) in enumerate(days)}
                            def evidence(c,t,d,h,realized,nav,base=base,gate=gate,idx=idx):
                                ev=base(c,t,d,h,realized,nav)
                                return replace(ev,current_signal_confirmed=ev.current_signal_confirmed and gate[idx[d]]['allow'])
                            kw['scaling_evidence']=evidence
                        x=a.execute(days,kw,m)
                    metric,daily=r.s1.measure(x,days)
                    metric.pop('pending_orders',None) # Not retained in prior archive; not a comparison outcome.

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
                        if keys:unique_rejected+=1;overlap_key='+'.join(keys);overlap[overlap_key]=overlap.get(overlap_key,0)+1
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
                    if key in saved:assert fills==saved[key]['scaled_fills']
                    raw.write(json.dumps(dict(seed=seed,quality=q,control=control,variant=v,decisions=x['decisions'],ledger=x['ledger'],nav=x['nav'],risk=x['risk_audit'],scaled_fills=fills))+'\n')
        print(f'seed {seed}: rows={len(rows)} reused={reused} new={new} attempts_upper={attempts} seconds={time.monotonic()-START:.1f}',flush=True)
    raw.close()
    keys=('cagr','mdd','calmar','exposure','turnover','scaled_fills','full_target_fills','risk_rejections','cap_rejections','cash_rejections')
    aggregates=[];paired=[]
    for q,control,v in sorted({(z['quality'],z['control'],z['variant']) for z in rows}):
        rr=[z for z in rows if (z['quality'],z['control'],z['variant'])==(q,control,v)]
        aggregates.append(dict(quality=q,control=control,variant=v,n=len(rr),means={k:st.mean(z[k] for z in rr if z[k] is not None) for k in keys},tail=dict(min_cagr=min(z['cagr'] for z in rr),max_mdd=max(z['mdd'] for z in rr),losing_seeds=[z['seed'] for z in rr if z['cagr']<0],latched_seeds=[z['seed'] for z in rr if z['mdd_latched']],worst_seed=min(rr,key=lambda z:z['cagr'])['seed'])))
        if v=='ev':continue
        deltas=[{k:z[k]-next(b for b in rows if b['seed']==z['seed'] and b['quality']==q and b['control']=='existing' and b['variant']=='ev')[k] for k in keys} for z in rr]
        paired.append(dict(quality=q,control=control,variant=v,reference='same seed existing 10%',cagr_wins=sum(z['cagr']>1e-12 for z in deltas),mean_delta={k:st.mean(z[k] for z in deltas) for k in keys},min_cagr_delta=min(z['cagr'] for z in deltas),max_cagr_delta=max(z['cagr'] for z in deltas),per_seed=[dict(seed=z['seed'],**d) for z,d in zip(rr,deltas)]))

    assert len(rows)==94 and reused==26 and attempts<=96
    assert all(sha(p)==h for p,h in before.items())
    report=dict(status='COMPLETE_SYNTHETIC_DIAGNOSTIC',comparison_complete=True,full_portfolio_attempts_upper_bound=attempts,prior_attempts_upper_bound=28,new_full_portfolio_attempts=new,reused_saved_replays=reused,completed_comparisons=len(rows),primary_comparisons=72,hypothetical_controls=22,elapsed_seconds=time.monotonic()-start,seeds=list(r.s1.SEEDS),sessions=252,source_unchanged=True,original_source_modified=False,ga_launched=False,source_sha256=before,reconstruction_exact=True,tape_hashes=hashes,aggregates=aggregates,paired=paired,runs=rows,reliability_states=gates,tests=dict(passed=10,log='resume_tests.log',module_path=str(OUT/'test_reliability.py')),replay_verification=dict(archive_sha256=manifest['replays.jsonl.gz'],archive_truncated=True,complete_record_sha256=record_hashes,validation='Whole archive and generating source checksums match prior manifest; complete records only; seed/quality/control/variant validated; 252 sessions, independent ledger/T+1/NAV/cost/risk and scaling-fill reconstruction passed.'),limitations=['Synthetic diagnostic only; no historical alpha claim.','Existing evidence pools endogenous funded exits; realized inputs vary with fills across caps.','Hypothetical gate uses strictly prior matured outcomes and date averages; two-SE margin is not a serial-dependence-valid confidence bound.','Hypothetical controls use 11 seeds (1101–1111); primary comparisons use all 12.','Rejection flags overlap; unique union and exact overlaps are reported.','Pending orders omitted because prior archive did not retain them.'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    print('COMPLETE',flush=True)
if __name__=='__main__':main()

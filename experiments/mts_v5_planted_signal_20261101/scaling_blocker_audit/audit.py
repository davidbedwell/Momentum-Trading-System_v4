#!/usr/bin/env python3
"""Bounded diagnostic: 72 instrumented original replays + 36 corrected strong replays.
No production writes. No fitting, GA or evidence relaxation.
"""
import sys, importlib.util, json, hashlib, time, csv, gzip, difflib, subprocess, tempfile
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent
FIX=OUT.parent/'stage2_fix'
sys.path.insert(0,str(FIX))
import support as r
from engines.portfolio_replay import kernel as original_kernel
START=time.monotonic()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCES=[Path(r.original.__file__),Path(original_kernel.__file__),r.ROOT/'discovery/competitive_ga/progressive_scaling.py',FIX/'functional_niche_manager.py',FIX/'support.py',OUT.parent/'run.py']
BEFORE={str(p):sha(p) for p in SOURCES}

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def once(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)

def prepare():
    manager=(FIX/'functional_niche_manager.py').read_text()
    kernel=Path(original_kernel.__file__).read_text()
    corrected=once(manager,'                    remaining_risk = max(0., bank.max_equity_risk - signal.other_equity_risk - reserved_loss)\n                    risk_cap = min(risk_cap, remaining_risk / per_dollar_loss if per_dollar_loss else 0.)\n','                    # Mandatory limit is per trade (entire candidate position), not portfolio aggregate.\n')
    corrected_kernel=once(kernel,'other_equity_risk=max(s.other_equity_risk,reserved_risk),max_equity_risk=self.max_equity_risk)','other_equity_risk=0.,max_equity_risk=self.max_equity_risk)')
    corrected_kernel=corrected_kernel.replace('        # Reserve portfolio risk across all evidence-based additions in score order.\n        # The caller-supplied other_equity_risk remains a separate floor.','        # Per-trade loss limit; other holdings do not consume this trade budget.\n        # Any aggregate portfolio guard must be a separately configured policy.')
    (OUT/'corrected_manager.py').write_text(corrected);(OUT/'corrected_kernel.py').write_text(corrected_kernel)
    patches=[]
    for name,old,new in [('discovery/competitive_ga/functional_niche_manager.py',manager,corrected),('engines/portfolio_replay/kernel.py',kernel,corrected_kernel)]:
        patches.append(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
    (OUT/'source.patch').write_text(''.join(patches))
    with tempfile.TemporaryDirectory(dir='/tmp') as td:
        for name,txt in [('discovery/competitive_ga/functional_niche_manager.py',manager),('engines/portfolio_replay/kernel.py',kernel)]:
            p=Path(td)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(txt)
        p=subprocess.run(['patch','--batch','-p1','-i',str(OUT/'source.patch')],cwd=td,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert (Path(td)/'discovery/competitive_ga/functional_niche_manager.py').read_text()==corrected
        assert (Path(td)/'engines/portfolio_replay/kernel.py').read_text()==corrected_kernel
        (OUT/'reconstruction.log').write_text(p.stdout+'Exact byte equality verified for both corrected modules.\n')
    mods=[]
    for label,txt in [('original',manager),('corrected',corrected)]:
        txt=once(txt,'            if selected:\n',"            audit['context'] = dict(held=None if held is None else dict(held), nav=nav, cash=bank.cash, unsettled=list(bank.unsettled), admission_halted=bank.admission_halted)\n            if selected:\n")
        txt=once(txt,'                funded = min(desired, remaining / ((1 + bank.friction) * (1 + bank.fees)))',"                funded = min(desired, remaining / ((1 + bank.friction) * (1 + bank.fees)))\n                audit['reservation_detail'] = dict(other_equity_risk=signal.other_equity_risk, reserved_loss=reserved_loss, per_dollar_loss=per_dollar_loss, risk_cap=risk_cap, remaining_cash_weight=remaining, initial_cash_weight=bank.cash/nav, desired=desired, funded=funded, unsettled_weight=sum(v for _,v in bank.unsettled)/nav, other_positions={t:dict(weight=pos.shares*bars[t].close/nav, loss=max(by_owner[pos.owner].stop,by_owner[pos.owner].gap_risk)+bank.round_trip_cost) for t,pos in book.positions.items() if t!=signal.ticker})")
        # 'audit' loop variable at this point is the matching decision from reverse search.
        path=OUT/f'{label}_instrumented_manager.py';path.write_text(txt)
        mods.append(load('discovery.competitive_ga.blocker_'+label,path))
    k=load('blocker_corrected_kernel',OUT/'corrected_kernel.py');mods[1].Replay=k.Replay
    return mods,k


def execute(days,kw,manager):
    kw=dict(kw); classify=kw["classify"]
    kw["classify"]=lambda t,d:manager.NicheObservation(**vars(classify(t,d)))
    return r.execute(days,kw,manager)

def evidence_fail(e,target):
    if e is None:return ['scaling_evidence_missing']
    fail=[]
    for key in ('position_profitable','current_signal_confirmed','positive_net_ev'):
        if not e[key]:fail.append(key)
    if e['matured_trades']<(50 if target>.15 else 30):fail.append('matured_trades')
    if target>.15:
        if e['forward_folds']<2:fail.append('forward_folds')
        if e['historical_mdd']>.20:fail.append('historical_mdd')
    return fail


def extract(x,days,seed,q,v,tape):
    records=[];ctx_by={};dayidx={d:i for i,(d,b) in enumerate(days)}
    risk={(a['date'],a['ticker']):a for a in x['risk_audit']}
    fills=defaultdict(list)
    for f in x['ledger']:fills[f[0],f[1]].append(f)
    for a in x['decisions']:
        c=a.get('context',{});h=c.get('held')
        if not h:continue
        d,t=a['date'],a['ticker'];i=dayidx[d];ev=r.s1.expected(tape[i][int(t[3:])],'strong' if q=='misnull' else q)-r.s1.ROUND_TRIP
        if ev<=0:continue
        target=.15 if v=='scale15' else .20
        native=next((ac for owner,ac,w in a.get('actions',[]) if ac in ('ADD','HOLD','EXIT','REDUCE')),None)
        add=native=='ADD';res=a.get('reservation');detail=a.get('reservation_detail',{});e=a.get('scaling_evidence')
        fail=evidence_fail(e,target) if add else []
        current=h['weight'];per=max(.02,r.s1.GAPS[int(t[3:])])+r.s1.ROUND_TRIP
        standalone=target*per;other=detail.get('other_equity_risk',0);reserved=detail.get('reserved_loss',0)
        requested_risk=target*per
        B=add and bool(fail)
        # Separate raw counterfactual constraints from operative funding constraints.
        C_own=add and requested_risk>.02+1e-12
        C_other=add and other+requested_risk>.02+1e-12 and not C_own
        C_queue=add and other+requested_risk<=.02+1e-12 and other+reserved+requested_risk>.02+1e-12
        need=max(0,min(target,.02/per)-current)
        cost=(1+r.s1.FRICTION)*(1+r.s1.COSTS['fees'])
        initial=detail.get('initial_cash_weight',c['cash']/c['nav'])
        remaining=detail.get('remaining_cash_weight',initial)
        E=add and initial+1e-12<need*cost
        F=add and remaining+1e-12<need*cost and remaining<initial-1e-12
        # D is a policy concentration cap distinct from B's failed prerequisites.
        effective_cap=.10
        if e and not evidence_fail(e,.15):effective_cap=.15
        if e and not evidence_fail(e,.20):effective_cap=.20
        D=add and target>effective_cap+1e-12
        cats=[k for k,b in [('A',not add),('B',B),('C',C_own or C_other or C_queue),('D',D),('E',E),('F',F)] if b]
        future=None;exitdate=None;realized=None
        for z in x['realized']:
            if z['ticker']==t and z['date']>d:
                exitdate=z['date'];realized=z['return'];break
        if exitdate:
            end=dayidx[exitdate];future=days[end][1][t].open/days[min(i+1,len(days)-1)][1][t].open-1
        nextd=days[i+1][0] if i+1<len(days) else None
        record=dict(seed=seed,quality=q,variant=v,date=d,ticker=t,native_action=native,net_ev=ev,current=current,requested=target,evidence=e,evidence_failed_fields=fail,standalone_target_loss=standalone,other_equity_risk=other,reserved_loss=reserved,per_dollar_loss=per,other_exhausts=C_other,standalone_exceeds=C_own,queue_risk_exhausts=C_queue,categories=cats,concentration_cap=effective_cap,nav=c['nav'],cash=c['cash'],unsettled=c['unsettled'],reservation=res,reservation_detail=detail,next_open_risk=risk.get((nextd,t)),next_open_fills=fills.get((nextd,t),[]),diagnostic_forward_return_to_next_native_exit=future,diagnostic_next_exit=exitdate,diagnostic_whole_trade_realized_return=realized)
        records.append(record)
    return records


def count(rows):
    adds=[z for z in rows if z['native_action']=='ADD']
    return dict(unique_positive_ev_incumbent_stock_dates=len(rows),unique_native_add_stock_dates=len(adds),categories=dict(Counter(k for z in rows for k in z['categories'])),exact_overlap=dict(Counter('+'.join(z['categories']) or 'none' for z in adds)),evidence_failed_fields=dict(Counter(k for z in adds for k in z['evidence_failed_fields'])),other_exhausts=sum(z['other_exhausts'] for z in adds),standalone_exceeds=sum(z['standalone_exceeds'] for z in adds),queue_risk_exhausts=sum(z['queue_risk_exhausts'] for z in adds),evidence_valid_adds=sum(not z['evidence_failed_fields'] for z in adds),evidence_valid_other_blocked=sum(not z['evidence_failed_fields'] and z['other_exhausts'] for z in adds),evidence_valid_other_blocked_cash_sufficient=sum(not z['evidence_failed_fields'] and z['other_exhausts'] and 'E' not in z['categories'] for z in adds))


def scaling_fills(x,days,target):
    previous={};out=[]
    for (d,bars),nav in zip(days,x['nav']):
        # Same DGP open==close; opening NAV before costs = close NAV plus net execution costs.
        fs=[f for f in x['ledger'] if f[0]==d]
        oe=nav[1]+sum(f[5]+f[3]*abs(f[4]-bars[f[1]].open) for f in fs)
        for f in fs:
            t=f[1]
            if f[2]=='BUY' and t in previous:
                w=(previous[t]+f[3])*bars[t].open/oe
                if w>.10001:out.append(dict(date=d,ticker=t,weight=w,full=w>=target-1e-9))
        previous=nav[3]
    return out


def main():
    (old,new),kernel=prepare()
    allrows=[];metrics=[];rawpath=OUT/'original_decision_risk.jsonl.gz'
    oldruns=list(csv.DictReader((FIX/'runs.csv').open()))
    oldreport=json.loads((FIX/'report.json').read_text())
    with gzip.open(rawpath,'wt') as raw:
        for seed in r.s1.SEEDS:
            assert time.monotonic()-START<600
            days,tapes,_=r.s1.generate(seed)
            for q in r.QUALITIES:
                tape=tapes['null' if q=='misnull' else q]
                assert hashlib.sha256(json.dumps(tape).encode()).hexdigest()==next(t['sha256'] for t in oldreport['tapes'] if t['seed']==seed and t['quality']==q)
                for v in ('scale15','scale20'):
                    kw,stats=r.callbacks(tape,q,v,seed,days);x=execute(days,kw,old);m,_=r.s1.measure(x,days)
                    ref=next(z for z in oldruns if int(z['seed'])==seed and z['quality']==q and z['variant']==v)
                    for key in ('cagr','mdd','exposure','turnover','final_nav'):assert abs(m[key]-float(ref[key]))<1e-10,(seed,q,v,key)
                    if seed==1101:
                        saved=json.loads((FIX/f'{q}_{v}_audit.json').read_text());clean=[{k:w for k,w in z.items() if k not in ('context','reservation_detail')} for z in x['decisions']]
                        assert json.loads(json.dumps(clean))==saved,'Instrumentation changed recorded decisions'
                    raw.write(json.dumps(dict(seed=seed,quality=q,variant=v,decisions=x['decisions'],risk=x['risk_audit'],nav=x['nav'],ledger=x['ledger'],realized=x['realized']))+'\n')
                    allrows.extend(extract(x,days,seed,q,v,tape))
            # Corrected run deliberately restricted to calibrated strong signal quality.
            for v in ('ev','scale15','scale20'):
                kw,stats=r.callbacks(tapes['strong'],'strong',v,seed,days);x=execute(days,kw,new);m,daily=r.s1.measure(x,days)
                if v=='ev':
                    ref=next(z for z in oldruns if int(z['seed'])==seed and z['quality']=='strong' and z['variant']==v)
                    for key in ('cagr','mdd','exposure','turnover','final_nav'):assert abs(m[key]-float(ref[key]))<1e-10
                fs=scaling_fills(x,days,.15 if v=='scale15' else .20)
                metrics.append(dict(seed=seed,quality='strong',variant=v,**m,scaled_fills=len(fs),full_target_fills=sum(f['full'] for f in fs),max_scaled_weight=max((f['weight'] for f in fs),default=0),**stats))
                if seed==1101:
                    (OUT/f'corrected_{v}_audit.json').write_text(json.dumps(dict(decisions=x['decisions'],risk=x['risk_audit'],scaled_fills=fs)))
            print(f'seed {seed}: original {6*(seed-1100)}, corrected {3*(seed-1100)}; {time.monotonic()-START:.2f}s',flush=True)
    with gzip.open(OUT/'unique_opportunities.jsonl.gz','wt') as f:
        for z in allrows:f.write(json.dumps(z)+'\n')
    bygroup={q+'_'+v:count([z for z in allrows if z['quality']==q and z['variant']==v]) for q in r.QUALITIES for v in ('scale15','scale20')}
    dedup={}
    for z in allrows:
        key=(z['seed'],z['quality'],z['date'],z['ticker'])
        if key not in dedup:dedup[key]=dict(z,categories=list(z['categories']))
        else:dedup[key]['categories']=sorted(set(dedup[key]['categories']+z['categories']))
    # Case selection is diagnostic ONLY, after all fixed-policy replays.
    cases=[z for z in allrows if z['quality']=='strong' and z['variant']=='scale15' and z['native_action']=='ADD' and not z['evidence_failed_fields'] and z['other_exhausts'] and 'E' not in z['categories'] and (z['diagnostic_forward_return_to_next_native_exit'] or 0)>.03]
    cases.sort(key=lambda z:z['net_ev'],reverse=True)
    chosen=[];seen=set()
    for z in cases:
        key=(z['seed'],z['ticker'],z['diagnostic_next_exit'])
        if key in seen:continue
        seen.add(key);chosen.append(z)
        if len(chosen)==8:break
    assert len(chosen)>=5,len(chosen)
    import statistics as st
    aggregates=[]
    for v in ('ev','scale15','scale20'):
        rr=[z for z in metrics if z['variant']==v]
        aggregates.append(dict(variant=v,n=len(rr),**{k:st.mean(z[k] for z in rr) for k in ('cagr','mdd','exposure','turnover')},scaled_fills=sum(z['scaled_fills'] for z in rr),full_target_fills=sum(z['full_target_fills'] for z in rr),max_scaled_weight=max(z['max_scaled_weight'] for z in rr)))
    report=dict(status='COMPLETE_DIAGNOSTIC_SYNTHETIC_ONLY',elapsed_seconds=time.monotonic()-START,original_instrumented_replays=72,corrected_replays=36,total_comparison_replays=108,original_metrics_identical=True,first_seed_original_decisions_identical=True,original_sources_sha256=BEFORE,source_unchanged=all(sha(p)==BEFORE[str(p)] for p in SOURCES),reconstruction_exact=True,groups=bygroup,all_variant_observations=count(allrows),deduplicated_across_targets=dict(stock_dates=len(dedup),category_union_counts=dict(Counter(k for z in dedup.values() for k in z['categories']))),cases=chosen,corrected_strong_aggregates=aggregates,limitations=['Synthetic assets only, not historical stocks or native model alpha.','ScaleEvidence is endogenous pooled funded exits, not verified independent trades.','Categories are simultaneous counterfactual constraints on target; evidence failure and evidence-implied concentration cap overlap.','A counted over positive-EV incumbents; B-F over native ADDs; per-group keys are seed/quality/variant/date/ticker.','F means prior ranked commitments reduce available cash; no claim alternate queue improves outcomes.','Future return used only for post-run case selection, never callbacks.','Corrected rerun restricted to strong quality; weak and misnull only audited, not retuned.'])
    assert report['source_unchanged']
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    with (OUT/'corrected_runs.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
    print(json.dumps(dict(groups=bygroup,corrected=aggregates,cases=len(chosen)),indent=2))
if __name__=='__main__':main()

"""Authentic-library integration diagnostic. Fail closed before performance study.

This module never equates original GA6 niches to chronological GA7 niches.
Its diagnostic is explicitly NOT a joint evolution or certified PIT experiment.
"""
import argparse
import hashlib
import json
import sqlite3
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from .functional_niche_manager import Candidate, NicheObservation, run_slice
from .ga6_native_daily_producer import decision as ga6_decision
from .ga7_native_daily_producer import decision as ga7_decision
from .native_signal_contract import NativeProposal
from .genome_identity import GenomeIdentityRegistry
from engines.portfolio_replay.kernel import Bar

OUT=Path('/opt/mts/ga7-deploy/experiments/codex_full_ga7')
DB=Path('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite')
COHORT=Path('/opt/mts/ga7-deploy/ga7_audit_v2/validation/handoff/frozen_cohort.json')
NATIVE=Path('/opt/mts/ga7-deploy/ga7_unbounded')
PANELS=Path('/opt/mts/synthetic-market-lab/runs/causal_native_features')

def dump(name,obj):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False))

def library():
    # Selection uses identity only, no discovery EV, trades, returns or panel data.
    with sqlite3.connect(f'file:{DB}?mode=ro',uri=True) as db:
        records=db.execute("""select id,definition from (
          select id,definition,row_number() over (
            partition by json_extract(definition,'$.genome.niche') order by id) r
          from chromosomes) where r<=2 order by id""").fetchall()
    result=[]
    for cid,record in records:
        definition=json.loads(record)
        result.append(('GA6',cid,definition['genome']['niche'],definition))
    cohort=json.loads(COHORT.read_text())['cohort']
    for niche,members in sorted(cohort.items()):
        for r in sorted(members,key=lambda x:x['identity'])[:2]:
            result.append(('GA7',r['identity'],niche,r['genome']))
    return result

def preflight(records):
    manifest=json.loads((NATIVE/'niche_pit_manifest.json').read_text())
    original=Path('/opt/mts/ga5_redesign/stocks31_40_corrected_v2/checkpoint.json')
    original_meta=Path(str(original)+'.pit.json')
    blockers=[]
    ga6_niches={n for f,_,n,_ in records if f=='GA6'}
    if ga6_niches-set(manifest['ids']):
        blockers.append({'code':'GA6_PIT_NICHE_IDENTITY_UNRESOLVED',
          'detail':'Every GA6 original NICHE-* group is absent from chronological PIT-NICHE-* IDs. Manifest explicitly says these identities differ. No authenticated mapping located.',
          'evidence':str(NATIVE/'niche_pit_manifest.json')})
    if not original_meta.exists():
        blockers.append({'code':'GA6_ORIGINAL_CENTERS_PIT_METADATA_MISSING',
          'detail':'Native pit_niche_guard requires training_end and frozen_at in this exact sidecar; original recognizer warns centers are retrospective.',
          'evidence':str(original_meta)})
    if manifest['status']!='PIT_VERIFIED':
        blockers.append({'code':'GA7_SOURCE_PIT_UNVERIFIED','detail':manifest['status'],
                         'evidence':str(NATIVE/'niche_pit_audit.json')})
    blockers.append({'code':'NATIVE_FEATURE_VALUE_PARITY_UNVERIFIED',
      'detail':'Existing readiness establishes feature-name coverage only, explicitly not native scaling/evaluator parity. Diagnostic uses existing panel values without alteration.',
      'evidence':'/opt/mts/synthetic-market-lab/reports/synthetic_native_readiness.json'})
    report={'status':'BLOCKED_BEFORE_FULL_STUDY','blockers':blockers,
      'library_size':len(records),'representation':dict(Counter(f+':'+n for f,_,n,_ in records)),
      'selection':'Two lexicographically smallest authentic identities per family/source niche. No performance filtering. 26 GA6 + 28 GA7; original definitions unchanged.',
      'library':[{'family':f,'id':cid,'niche':n,'definition':g} for f,cid,n,g in records],
      'source_hashes':{'cohort_sha256':hashlib.sha256(COHORT.read_bytes()).hexdigest(),
        'pit_manifest_sha256':hashlib.sha256((NATIVE/'niche_pit_manifest.json').read_bytes()).hexdigest()},
      'predeclared_full_protocol':{'scenarios':[1,2,3,4,5],'stocks':500,'sessions':1260,
        'checkpoints':[252,504,756,1008],'holdout_sessions':[1008,1259],
        'capital':100000,'annual_metrics':['CAGR','MDD','matured net trade EV'],
        'controls':['frozen native library and manager','learning and joint evolution'],
        'stop_conditions':['any unresolved provenance gate','missing held native feature','nonfinite NAV','negative cash','fill ownership mismatch','future maturity in learning','invalid action'],
        'execution':'Next open; one shared funded bank per scenario/arm; 10% entry cap; T+1 sales settlement; 10bp per side. Native shadow independent from funded selection.',
        'learning':'Only native exited outcomes matured strictly before decision. No fixed-horizon proxy or discovery EV.',
        'evolution':'Not implemented/validated in this diagnostic. No full-study claim until joint chromosome and manager evolution is integrated and gated.'},
      'full_study_launched':False,'full_study_eta':None}
    dump('preflight.json',report)
    return report

def diagnostic(records,scenario=1,start=300,sessions=40, exploratory=None):
    from ga5_feature_adapter import LEGACY
    from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
    from .synthetic_native_feature_gate import leaves
    started=time.monotonic()
    # No final-year rows loaded, scored, selected or evolved.
    all_dates=sorted(pd.read_parquet(PANELS/f'universe_{scenario}_eight_family.parquet',columns=['date']).date.unique())
    if exploratory is None and start+sessions>1008:raise ValueError('diagnostic must not touch final year')
    dates=all_dates[start:start+sessions]
    earliest=all_dates[max(0,start-40)]
    models=json.loads((NATIVE/'niche_pit_models.json').read_text())
    nf=json.loads(Path('/opt/mts/ga5_redesign/chronological_memory_corrected_v2/memory.json').read_text())['features']
    needed=set(nf)|{'date','ticker','eligible','open','high','low','close'}
    objects={};required={};genomes={};registry=GenomeIdentityRegistry();candidates=[]
    for family,cid,niche,definition in records:
        key=(family,cid)
        if family=='GA6':
            obj=StructuralCandidate.restore(definition)
            req={getattr(obj.genome,k) for k in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')}|leaves(obj.entry_tree)
            # Stop metadata is unused by native_action, whose actual frozen stop remains unchanged.
            stop=min(.02,obj.genome.stop_loss)
        else:
            obj=SimpleNamespace(**definition)
            req={obj.feature_a,obj.feature_b};stop=obj.stop_pct
        objects[key]=obj;required[key]=req;needed|={LEGACY.get(x,x) for x in req}
        genomes[key]=definition;registry.register(family,cid,definition)
        candidates.append(Candidate(cid,family,None if niche=='NON_NICHE' else (exploratory.mapping.get(niche,niche) if exploratory else niche),stop))
    if exploratory is not None:
        def register_descendant(family, definition, niche):
            if family=='GA6':
                obj=StructuralCandidate.restore(definition);cid=obj.identity()
                stop=min(.02,obj.genome.stop_loss)
                req={getattr(obj.genome,k) for k in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')}|leaves(obj.entry_tree)
            else:
                obj=SimpleNamespace(**definition)
                cid=hashlib.sha256(json.dumps(definition,sort_keys=True).encode()).hexdigest()
                stop=obj.stop_pct;req={obj.feature_a,obj.feature_b}
            key=(family,cid)
            if key in genomes:return key
            if not {LEGACY.get(x,x) for x in req} <= needed:
                raise ValueError('descendant introduced unloaded features')
            objects[key]=obj;required[key]=req;genomes[key]=definition
            registry.register(family,cid,definition)
            candidates.append(Candidate(cid,family,niche,stop))
            return key
        exploratory.bind(genomes,candidates,register_descendant)
    parts=[]
    filters=[('date','>=',pd.Timestamp(earliest)),('date','<=',pd.Timestamp(dates[-1]))]
    for suffix in ('eight_family','ga4_native'):
        path=PANELS/f'universe_{scenario}_{suffix}.parquet'
        cols=set(pq.read_schema(path).names)&needed
        parts.append(pd.read_parquet(path,columns=sorted(cols|{'date','ticker'}),filters=filters))
    a,b=parts
    frame=a.merge(b[['date','ticker']+[x for x in b if x not in a]],on=['date','ticker'],validate='one_to_one')
    parts=[]
    for _,g in frame.groupby('ticker',sort=False):
        g=g.sort_values('date').copy();v=g.close;delta=v.diff();flip=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
        for w in (10,20,40):
            net=(v-v.shift(w)).abs()
            g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum()).clip(0,1)
            g[f'reversal_rate_{w}']=flip.rolling(w).mean()
            g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w))
        g['range_width_20']=(g.high.rolling(20).max()-g.low.rolling(20).min())/v
        parts.append(g)
    frame=pd.concat(parts).replace([np.inf,-np.inf],np.nan)
    frame=frame[frame.date.isin(dates)].sort_values(['date','ticker'])
    rows={};observations={};days=[];previous={}
    # Native GA7 controller enforces independent radii + 5% hysteresis.
    from ga7.niche_controller import controlling_niche
    ids=json.loads((NATIVE/'niche_pit_manifest.json').read_text())['ids']
    for dt,g in frame.groupby('date',sort=True):
        day=str((pd.Timestamp('2027-01-04')+pd.offsets.BDay(all_dates.index(dt))).date());year=dt.year
        model=next(m for m in models if m['year']==year)
        assert model['trained_through']<day
        raw=g[nf].to_numpy(float);valid=np.isfinite(raw).all(axis=1)
        z=np.clip((raw-np.array(model['median']))/np.array(model['scale']),-5,5)
        dist=np.linalg.norm(z[:,None,:]-np.array(model['centers'])[None,:,:],axis=2)/np.array(model['radii'])
        bars={}
        for j,r in enumerate(g.to_dict('records')):
            t=r['ticker'];rows[t,day]=r;bars[t]=Bar(float(r['open']),float(r['close']))
            controller=None;matches=()
            if valid[j]:
                controller,qualified=controlling_niche(dist[j],[1.]*13,ids,previous.get(t))
                matches=tuple((n,float(d)) for n,d in zip(ids,dist[j]) if n in qualified)
            previous[t]=controller
            observations[t,day]=(NicheObservation(day,model['trained_through'],'native-annual-centers-SOURCE-PIT-UNVERIFIED',matches,controller),controller)
        if len(bars)!=500:raise ValueError('require 500 stocks')
        days.append((day,bars))
    index={d:i for i,(d,_) in enumerate(days)};calls=Counter();snapshots={}
    def eligible(c,t,d):
        r=rows[t,d];req=required[c.family,c.chromosome_id]
        return bool(r.get('eligible',False)) and all(pd.notna(r.get(LEGACY.get(f,f))) for f in req)
    def native(c,t,d,held):
        key=(c.family,c.chromosome_id);r=rows[t,d];obj=objects[key]
        if c.family=='GA6':
            value=ga6_decision(obj,r,held,session=index[d])
        else:
            value=ga7_decision(obj,{'close':r['close'],'eligible':r.get('eligible',False),
              'features':{f:r.get(f,float('nan')) for f in required[key]}},held)
        if value is None:return None
        action,target=value
        calls[c.family+':'+action]+=1
        if (t,d) not in snapshots:
            snapshots[t,d]=hashlib.sha256(json.dumps({k:(None if pd.isna(v) else str(v)) for k,v in r.items()},sort_keys=True).encode()).hexdigest()
        return NativeProposal(d,t,c.family,c.chromosome_id,action,target,0.,
          'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
          registry.by_id[key],snapshots[t,d],exploratory.birth_cutoffs.get(key,'2026-10-28') if exploratory else '2026-10-28')
    # The diagnostic preserves certified-identity gating; exploratory callers
    # explicitly opt into a labeled routing hypothesis without editing source genomes.
    result=run_slice(days,candidates,classify=lambda t,d:observations[t,d][0],
      eligible=eligible,native=native,max_stocks=500,max_sessions=sessions,native_shadow=True,
      native_genomes=genomes,genome_registry=registry,require_genome_identity=True,
      selector=exploratory.select if exploratory else None,
      session_hook=exploratory.on_session if exploratory else None, retain_audit=exploratory is None,
      funded_entry_scale=(lambda: exploratory.cap) if exploratory else None,
      candidate_provider=(lambda: candidates) if exploratory else None)
    if exploratory is not None:
        exploratory.native_actions=dict(calls)
        return exploratory.finish(result, days, time.monotonic()-started, scenario)
    counts=Counter(o.family for o in result['native_shadow_outcomes'])
    elapsed=time.monotonic()-started
    summary={'status':'DIAGNOSTIC_ONLY_FULL_STUDY_BLOCKED','scenario':scenario,'start_session':start,
      'sessions':sessions,'stocks':500,'chromosomes':len(records),'wall_seconds':elapsed,
      'native_actions':dict(calls),'funded_fills':len(result['ledger']),
      'funded_families':sorted({x['owner'][0] for x in result['realized']}|{x[0] for x in result['owners'].values()}),
      'native_matured_outcomes':dict(counts),'native_shadow_open':len(result['native_shadow_open']),
      'full_experiment_metrics':None,'joint_evolution_complete':False,
      'limitations':['GA6 original niches not funded: no certified PIT identity bridge.',
        'GA6 shadows use feature eligibility only, not certified native niche membership.',
        'GA7 classifier source PIT unverified; raw native feature scaling parity unverified.',
        'No chromosome/manager evolution or causal learning selection in diagnostic.',
        'Synthetic order calendar rebased to 2027 after library freeze; not a historical backtest. Native classifier year still selected by original source-panel date.',
        'No annual performance claim; last year untouched.'],
      'timing_scope':'54 real genomes x 500 stocks diagnostic; extrapolation excludes joint GA cost.'}
    dump('diagnostic.json',summary)
    dump('diagnostic_fills.json',result['ledger'])
    dump('diagnostic_native_maturity.json',[asdict(x) for x in result['native_shadow_outcomes']])
    print(json.dumps(summary,indent=2),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--diagnostic',action='store_true');p.add_argument('--sessions',type=int,default=40)
    args=p.parse_args();records=library();report=preflight(records)
    print(json.dumps({k:v for k,v in report.items() if k not in ('library','predeclared_full_protocol')},indent=2),flush=True)
    if args.diagnostic:
        diagnostic(records,sessions=args.sessions)
    else:
        raise SystemExit(2)  # Gate failure must never look like study success.

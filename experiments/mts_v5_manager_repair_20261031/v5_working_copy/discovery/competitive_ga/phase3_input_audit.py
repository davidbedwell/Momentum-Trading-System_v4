"""Read-only bounded 500-ticker audit; no GA experiment or proof evaluation.

The engineering-only date seal below is NOT an approved research split. Raw
price filters are applied before loading; fundamentals and sealed prices are
never opened. Output remains BLOCKED until governed daily controls exist.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from .first_year_features import build, RAW, SOURCE, COLUMNS
from .first_year_manifest import Calendar, manifest, digest
from .first_year_parity import load_native, ga6_features, compare, required_ga6
from .archived_genomes import ga7_bars

AS_OF = '2023-06-30'


def audit():
    raw = pd.read_parquet(RAW, columns=COLUMNS, filters=[('Date','<=',pd.Timestamp(AS_OF))])
    raw = raw.rename(columns={c:c.lower() for c in COLUMNS})
    raw['date'] = pd.to_datetime(raw.date)
    dates = tuple(d.strftime('%Y-%m-%d') for d in sorted(raw.date.unique()))
    tickers = tuple(sorted(raw.ticker.unique()))
    calendar = Calendar(dates+('2023-07-03',), '2022-12-30', AS_OF, '2023-07-03')
    cache = Path('/tmp/mts_phase3_feature_audit')
    cache.mkdir(exist_ok=True)
    dependencies = [RAW, SOURCE, Path('/opt/mts/ga5_feature_families.py'),
        Path('/opt/mts/thunder-migration/mts-layered-run-20261007/Reconstruction/Certified-Stage2-Source-20261007/MTS_V4/derived_feature_factory.py'),
        Path(__file__).with_name('first_year_features.py')]
    provenance = dict(as_of=AS_OF, hashes={str(p):digest(p) for p in dependencies})
    identity = cache/'provenance.json'
    reusable = identity.exists() and json.loads(identity.read_text()) == provenance
    if not reusable:
        for name in ('full','direct','prefix'):
            (cache/(name+'.parquet')).unlink(missing_ok=True)
        identity.write_text(json.dumps(provenance,sort_keys=True))
    def stage(name, generate):
        target = cache/(name+'.parquet')
        hashfile = target.with_suffix('.sha256')
        if target.exists() and hashfile.exists() and digest(target) == hashfile.read_text():
            print('Verified cached '+name,flush=True)
            return pd.read_parquet(target)
        print('Building '+name+' on 500 tickers',flush=True)
        value = generate()
        value.to_parquet(target,index=False)
        hashfile.write_text(digest(target))
        return value
    full = stage('full',lambda:build(as_of=AS_OF))
    # Direct authentic call, separately from adapter loading/renaming/aliasing.
    factory = load_native(SOURCE, 'mts_phase3_direct_factory')
    direct = stage('direct', lambda:factory.recompute_cross_sectional(pd.concat([
        factory.build_stock_local_frame(g,t,str(g.sector.iloc[0]),None)
        for t,g in raw.groupby('ticker',sort=True)],ignore_index=True)))
    direct = direct.rename(columns={'effective_date':'date'})
    cols = [c for c in direct if c.endswith('__v1')]
    direct['date'] = pd.to_datetime(direct.date)
    native6 = load_native('/opt/mts/ga5_feature_families.py','mts_phase3_direct_ga6')
    six = ga6_features(raw,full)
    reference6 = native6.compute(raw,dict(raw[['ticker','sector']].drop_duplicates().itertuples(index=False,name=None)))
    aliases = {f'ga4_{c}':np.tanh(pd.to_numeric(direct[c],errors='coerce').astype(float).clip(-1e8,1e8)) for c in cols}
    reference6 = reference6.merge(pd.concat([direct[['date','ticker']],pd.DataFrame(aliases,index=direct.index)],axis=1),on=['date','ticker'],validate='one_to_one')
    def keys(f):
        f=f.copy();f['date']=pd.to_datetime(f.date).dt.strftime('%Y-%m-%d');return f
    g4 = compare(keys(full),keys(direct),columns=cols,calendar=calendar,as_of=AS_OF,tickers=tickers)
    g6 = compare(keys(six),keys(reference6),columns=[*native6.FAMILIES,*aliases],calendar=calendar,as_of=AS_OF,tickers=tickers)
    # Long warmup prefix comparison across ALL 500 names, not two-name smoke.
    prefix_end = dates[-21]
    prefix = stage('prefix',lambda:build(as_of=prefix_end))
    causal = compare(keys(prefix),keys(full.loc[full.date<=prefix_end]),columns=[*cols,*aliases],calendar=calendar,as_of=prefix_end,tickers=tickers)
    sys.path.insert(0,'/opt/mts/ga7-deploy/ga7_unbounded')
    from ga7.runner import COLUMNS as GA7_COLUMNS
    from ga7.fold_features import rank_filtered_sessions
    # ALL-TRUE below is strictly a rank diagnostic, never a PIT eligibility claim.
    diagnostic = dict.fromkeys(tickers,True)
    rank_cells = rank_finite = rank_sessions = 0
    for d, section in six.groupby('date',sort=True):
        date = pd.Timestamp(d).strftime('%Y-%m-%d')
        ranked = ga7_bars(section,decision_date=date,eligibility=diagnostic,columns=GA7_COLUMNS)
        bars = {r['ticker']:dict(close=float(r['close']),eligible=True,features={c:float(r[c]) for c in GA7_COLUMNS}) for r in section.to_dict('records')}
        reference7 = rank_filtered_sessions([(date,bars,False)],set(tickers),GA7_COLUMNS)[0][1]
        a=np.array([[ranked[t]['features'][c] for c in GA7_COLUMNS] for t in tickers])
        b=np.array([[reference7[t]['features'][c] for c in GA7_COLUMNS] for t in tickers])
        if not np.allclose(a,b,equal_nan=True,rtol=0,atol=0):raise ValueError('GA7 native rank parity mismatch')
        rank_cells += int(a.size)
        rank_finite += int(np.isfinite(a).sum())
        rank_sessions += 1
    sources=[dict(path=str(p),sha256=digest(p),role=role) for p,role in (
        (RAW,'synthetic_bars'),(SOURCE,'GA4_factory'),
        (Path('/opt/mts/ga5_feature_families.py'),'GA6_factory'),
        (Path('/opt/mts/ga7-deploy/ga7_unbounded/ga7/fold_features.py'),'GA7_ranks'),
        (Path('/opt/mts/ga7-deploy/ga7_unbounded/ga7/runner.py'),'GA7_registry'),
        (dependencies[3],'GA4_transitive_factory'),
        (dependencies[4],'GA4_adapter'))]
    # Identity carried from the Phase 2 report, never chosen on synthetic returns.
    sys.path[:0] = ['/opt/mts','/opt/mts/ga5_redesign']
    from .archived_genomes import ga6
    from ga5_feature_adapter import LEGACY
    from ga6.native_position_decision_adapter import native_action
    candidate_id = '000040b4691c2c84a9bea15a1b3a17a6d489a616480782c5fffddad2d267ea97'
    candidate = ga6('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite',[candidate_id])[candidate_id]
    needed = required_ga6(candidate,LEGACY)
    missing = sorted(set(needed)-set(six))
    last = six.loc[six.date==AS_OF]
    finite = int(np.isfinite(last[needed].to_numpy(dtype=float)).all(axis=1).sum()) if not missing else 0
    actions = {}
    if not missing:
        for row in last.to_dict('records'):
            action,_ = native_action(candidate,row,None,len(dates)-1)
            actions[action] = actions.get(action,0)+1
    candidate_evidence = dict(identity=candidate_id,required_features=needed,
        missing_columns=missing,finite_last_session_tickers=finite,
        flat_state_native_diagnostic_actions=actions,
        scope='explicit Phase 2 identity, real synthetic rows, no PIT/training certification or portfolio experiment')
    result=manifest(keys(raw),calendar=calendar,as_of=AS_OF,tickers=tickers,
                    sources=sources,contracts={},gate_rows={},decision_times={})
    result.update(split_authority='ENGINEERING_ONLY_NOT_APPROVED_RESEARCH_PARTITION',
                  feature_evidence=dict(GA4=g4,GA6=g6,GA6_candidate=candidate_evidence,causal_prefix=causal,
                      GA7=dict(tickers=500,features=len(GA7_COLUMNS),cells=rank_cells,finite_values=rank_finite,sessions=rank_sessions,parity=True,
                               scope='all dated cross sections including warmup; all-true diagnostic gate, no PIT claim'),
                      HORIZONS=dict(status='BLOCKED',reason='No compatible synthetic stress/publication provenance; complete normalization parity not attempted')),
                  first_date=dates[0],sessions=len(dates),proof_values_read=False)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    target=args.output.resolve()
    if not (target.is_relative_to(Path(__file__).resolve().parents[2]) or target.is_relative_to('/tmp')):
        parser.error('output must be inside repository or /tmp')
    result=audit()
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','first_date','sessions','feature_evidence')},indent=2))
    return 2 if result['blockers'] else 0

if __name__=='__main__':raise SystemExit(main())

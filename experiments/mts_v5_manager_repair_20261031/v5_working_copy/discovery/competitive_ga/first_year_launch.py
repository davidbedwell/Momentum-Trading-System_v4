"""Read-only first-year launch preflight. Exit 2 means launch is blocked.

This deliberately cannot start a full experiment while native family bridges,
external stress inputs and execution certification are incomplete.
"""
import argparse
import importlib.metadata
import json
from pathlib import Path
import sqlite3
from .first_year_features import SOURCE,RAW
from .legacy_archive_index import DB as LEGACY_DB
from .horizons_external_stress import RECOVERED_ROOT

ROOT=Path('/opt/mts')


def preflight():
    paths={
        'raw_synthetic_bars':RAW,
        'ga4_feature_factory':SOURCE,
        'ga4_predictor_registry':ROOT/'thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet',
        'legacy_chromosomes':LEGACY_DB,
        'ga6_chromosomes':ROOT/'ga6/runs/frozen_four_run_20261024/catalogue.sqlite',
        'ga6_native_decisions':ROOT/'ga6/native_position_decision_adapter.py',
        'recovered_vix':RECOVERED_ROOT/'CrashMultiMarketV1/VIX_History.csv',
        'recovered_vvix':RECOVERED_ROOT/'CrashMultiMarketV1/VVIX_History.csv',
        'recovered_ofr':RECOVERED_ROOT/'CrashCausalPackV1/ofr_fsi_raw_20261004.csv',
        'ga7_checkpoint':ROOT/'ga7-deploy/ga7_unbounded/runs/preflight_16/checkpoint.json',
        'ga7_native_replay':ROOT/'ga7-deploy/ga7_unbounded/ga7/request_replay.py',
    }
    sources={}
    for name,path in paths.items():
        try:
            with path.open('rb') as stream:stream.read(1)
            sources[name]={'path':str(path),'readable':True,'bytes':path.stat().st_size}
        except OSError as exc:
            sources[name]={'path':str(path),'readable':False,'error':str(exc)}
    catalogues={}
    for name in ('legacy_chromosomes','ga6_chromosomes'):
        if not sources[name]['readable']:continue
        try:
            with sqlite3.connect(paths[name].as_uri()+'?mode=ro',uri=True) as db:
                if name=='legacy_chromosomes':
                    catalogues[name]=dict(db.execute('select study,count(*) from strategies group by study'))
                else:catalogues[name]={'chromosomes':db.execute('select count(*) from chromosomes').fetchone()[0]}
        except sqlite3.Error as exc:catalogues[name]={'error':str(exc)}
    dependencies={}
    for package in ('numpy','pandas','pyarrow','pytest'):
        try:dependencies[package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:dependencies[package]='MISSING'
    blockers=[
        'GA4 archive horizons are observations, not exit policies; held-state bridge fails closed without an explicit native exit producer.',
        'Historical VIX/VVIX/OFR stress files recovered through 2026-09-30; no governed mapping to fictional market paths, full date coverage or publication-time certification.',
        'GA6 native daily bridge and bounded archive restoration implemented; full causal synthetic feature/universe parity remains unverified.',
        'GA7 explicit archive restoration and native eligible-universe ranks implemented; full-universe long-history feature and niche parity remain unverified.',
        'Optional independently funded shadow books now reconcile cash/settlement; authentic native capacity, risk and ledger parity remain uncertified.',
        'Portfolio execution lacks certified settlement, PIT controls, defense timing and independent accounting parity.',
    ]
    blockers.extend('Unreadable source: '+name for name,item in sources.items() if not item['readable'])
    return {'status':'BLOCKED_NOT_LAUNCH_READY','sources':sources,
            'catalogues':catalogues,'dependencies':dependencies,'blockers':blockers,
            'implemented':['bounded original-factory causal feature rebuild',
                           '500-ticker dated manifest, proof seal, PIT/earnings gates and native feature parity audit',
                           'optional independently funded owner shadows with session settlement',
                           'four-family proposal contract, GA6 native actions and fail-closed GA4 held state',
                           'bounded explicit GA6/GA7 archive restoration and native GA7 ranks',
                           'independent shadow native held-state production callback',
                           'close-timed defense and per-session cash/NAV identities',
                           'shared $100k next-open research replay and filled ownership',
                           'fee-inclusive shadow ENTER/ADD/REDUCE/EXIT accounting',
                           'bounded manager evolution with frozen chronological validation'],
            'research_sources_modified':False,'full_experiment_started':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=preflight()
    payload=json.dumps(result,indent=2)
    if args.output:
        # Never write a launch artifact into the preserved research tree.
        target=args.output.resolve()
        workspace=Path(__file__).resolve().parents[2]
        if not (target.is_relative_to(workspace) or target.is_relative_to('/tmp')):
            parser.error('output must be inside the repository or /tmp')
        target.write_text(payload+'\n')
    print(payload)
    return 2

if __name__=='__main__':raise SystemExit(main())

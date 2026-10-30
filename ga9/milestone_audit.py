"""Independent dated input audit and training-only participation experiment.

Never certifies the fixed source cohort as historical Nasdaq membership.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from .input_audit import sha256
from .execution import load_panel, replay, Gene, Manager, scores
from .screening import ScreenPolicy
from .benchmarks import attach_primary, BenchmarkPolicy, DEFAULT_SPY
from .objective import benchmark

RAW = Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
NOTICE = 'https://www.nasdaq.com/press-release/annual-changes-to-the-nasdaq-100-index-2022-12-09'

def audit(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if (output/'audit.json').exists():
        raise FileExistsError('Audit output exists')
    # Announcement facts only: removal does not establish the original admission date.
    events = [dict(ticker=s, action=a, known_at='2022-12-09', effective_from='2022-12-19',
                   source=NOTICE) for a, names in [
                       ('add','CSGP RIVN WBD GFS BKR FANG'),
                       ('remove','VRSN SWKS SPLK BIDU MTCH DOCU NTES')]
              for s in names.split()]
    pd.DataFrame(events).to_csv(output/'independent_membership_events.csv',index=False)
    symbols = sorted(pd.read_parquet(RAW, columns=['ticker']).ticker.unique())
    # Unknown is explicit, never interpreted as eligible or ineligible.
    pd.DataFrame([dict(ticker=s, as_of='2022-01-01', status='unverified',
                       reason='No independently evidenced starting roster and complete change chain')
                  for s in symbols]).to_csv(output/'eligible_universe_audit.csv',index=False)
    design = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  experiment='top_k 20 versus 40; all other rules identical',
                  period=['2022-01-01','2023-01-01'], selection='training-only diagnostic; no promotion or forward tuning',
                  primary='SPY', universe='fixed DEV79; not historical Nasdaq-100',
                  data=str(RAW),data_sha256=sha256(RAW),etf=str(DEFAULT_SPY),etf_sha256=sha256(DEFAULT_SPY))
    (output/'experiment_frozen.json').write_text(json.dumps(design,indent=2))
    results = {}
    for k in [20,40]:
        panel, input_audit = load_panel(RAW,end='2023-01-01',screen_policy=ScreenPolicy(top_k=k))
        panel, etf_audit = attach_primary(panel,DEFAULT_SPY,BenchmarkPolicy('broad_us'),'2023-01-01')
        genes = [Gene('momentum')]
        native = scores(panel, genes)
        entry = np.where(panel.screen_mask[None, :, :], native, np.nan)
        run = replay(panel,genes,Manager(),'2022-01-01','2023-01-01',detail=True,
                     signal=entry, hold_signal=native)
        etf = benchmark(panel.primary_benchmark,'2022-01-01','2023-01-01')
        counts = panel.screen_mask.sum(axis=1)
        eligible = panel.eligible.sum(axis=1)
        daily = pd.DataFrame(dict(date=panel.dates,eligible=eligible,shortlisted=counts))
        daily.to_csv(output/f'participation_top{k}.csv',index=False)
        pd.DataFrame(run['equity']).to_csv(output/f'training_top{k}_equity.csv',index=False)
        results[str(k)] = dict(metrics=run['metrics'],etf_metrics=etf['metrics'],
                              mean_shortlist=float(counts.mean()),zero_shortlist_sessions=int((counts==0).sum()),
                              full_shortlist_sessions=int((counts==k).sum()),
                              distinct_selected_symbols=int(panel.screen_mask.any(axis=0).sum()),
                              eligible_symbol_sessions=int(eligible.sum()),shortlisted_symbol_sessions=int(counts.sum()),
                              fills=len(run['fills']))
    before=json.loads((output/'ga8_before.json').read_text())
    after={p:sha256(p) for p in before}
    record=dict(**design,results=results,independent_membership_events=len(events),
                membership_certified=False, qqq_status=json.loads((output/'acquisition.json').read_text()),
                blockers=['Complete starting Nasdaq-100 roster and all off-cycle changes with announcement evidence',
                          'Delisted/removed constituent bars and identity mapping',
                          'Real QQQ daily OHLC, adjusted close, distributions and split data; download ConnectionError',
                          'No cloud runtime status tool or network policy file available'],
                ga8_source_hashes_unchanged=before==after)
    (output/'ga8_after.json').write_text(json.dumps(after,indent=2))
    (output/'audit.json').write_text(json.dumps(record,indent=2,default=str))
    print(json.dumps(record,indent=2,default=str))

if __name__ == '__main__':
    import sys
    audit(sys.argv[1])

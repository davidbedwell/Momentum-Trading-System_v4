"""2020 GA4/HORIZONS evidence audit; does not invent unavailable decisions."""
import json,glob
from pathlib import Path
import pandas as pd
from .legacy_archive_index import counts
ROOT=Path('/opt/mts/parallel_research_20261016/mts')
OUT=Path('/opt/mts/synthetic-market-lab/reports/legacy_2020_readiness.json')
def run():
 paths=sorted(glob.glob(str(ROOT/'ga4_regime_integration/full_20y_signals/ga4_signals_*.parquet')))
 sample=paths[:3]
 rows=0;keys=set();tickers=set()
 for path in sample:
  x=pd.read_parquet(path,columns=['decision_date','ticker','definition_hash'])
  x=x[(x.decision_date>='2020-05-28')&(x.decision_date<='2020-12-31')]
  rows+=len(x);keys.update(x.definition_hash.unique());tickers.update(x.ticker.unique())
 result={'status':'PARTIAL_2020_COVERAGE_AUDIT','legacy_bank':counts(),'ga4_signal_partitions_total':len(paths),'ga4_partitions_sampled':len(sample),'ga4_sample_2020_rows':rows,'ga4_sample_2020_distinct_definitions':len(keys),'ga4_sample_2020_distinct_tickers':len(tickers),'horizons_event_tape_start':'2006-09-15','horizons_event_tape_end':'2007-03-14','blocker':'HORIZONS 2020 decisions must be reconstructed from frozen grammar; 2006 tape is not a 2020 decision feed','warning':'GA4 coverage is sampled and not an executable parity check; no portfolio or cross-family winner established'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2))
 return result
if __name__=='__main__':print(json.dumps(run(),indent=2))

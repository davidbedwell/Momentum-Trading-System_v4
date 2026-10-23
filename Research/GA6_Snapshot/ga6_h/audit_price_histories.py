"""Read-only, reproducible audit of GA6-H downloaded raw OHLCV files."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

ROOT = Path('/opt/mts/ga6_h/data')
FILES = ROOT / 'prices'
OUT = Path('/opt/mts/ga6_h/audits')
OUT.mkdir(exist_ok=True)
universe = pd.read_parquet(ROOT / 'current_universe.parquet')
manifest = pd.read_parquet(ROOT / 'download_manifest.parquet')
records = []
dates_all = []
for path in sorted(FILES.glob('*.parquet')):
    d = pd.read_parquet(path)
    dates = pd.to_datetime(d['date'], errors='coerce')
    nums = ['Open','High','Low','Close','Adj Close','Volume']
    for col in nums: d[col] = pd.to_numeric(d[col], errors='coerce')
    price = d[['Open','High','Low','Close']]
    bad_ohlc = ((d['High'] < d[['Open','Close','Low']].max(axis=1)) | (d['Low'] > d[['Open','Close','High']].min(axis=1))).sum()
    bad_price = (price.le(0).any(axis=1) | ~np.isfinite(price).all(axis=1)).sum()
    bad_volume = (d['Volume'].lt(0) | ~np.isfinite(d['Volume'])).sum()
    duplicate_dates = dates.duplicated().sum()
    unsorted = not dates.is_monotonic_increasing
    if len(dates): dates_all.extend((dates.min(), dates.max()))
    records.append({'symbol':path.stem,'rows':len(d),'first':str(dates.min().date()) if len(dates) else None,
      'last':str(dates.max().date()) if len(dates) else None,
      'duplicate_dates':int(duplicate_dates),'unsorted':bool(unsorted),'bad_ohlc':int(bad_ohlc),
      'bad_price':int(bad_price),'bad_volume':int(bad_volume),
      'missing_adjusted':int(d['Adj Close'].isna().sum()),'zero_volume':int(d['Volume'].eq(0).sum()),
      'split_events':int(d['Stock Splits'].fillna(0).ne(0).sum()),
      'dividend_events':int(d['Dividends'].fillna(0).ne(0).sum()),
      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
audit = pd.DataFrame(records)
audit.to_parquet(OUT / 'price_coverage.parquet', index=False)
expected = set(universe['yf_symbol'].astype(str))
actual = set(audit.symbol)
summary = {'audited_utc':datetime.now(timezone.utc).isoformat(),'universe_count':len(universe),
 'manifest_count':len(manifest),'file_count':len(audit),'missing_files':sorted(expected-actual),
 'unexpected_files':sorted(actual-expected),
 'total_price_rows':int(audit.rows.sum()),'coverage_2016_or_earlier':int((audit['first'] <= '2016-01-05').sum()),
 'coverage_since_2024_or_later':int((audit['first'] >= '2024-01-01').sum()),
 'short_under_252_sessions':int((audit.rows < 252).sum()),
 'duplicate_date_files':int((audit.duplicate_dates > 0).sum()),
 'unsorted_files':int(audit.unsorted.sum()),'bad_ohlc_files':int((audit.bad_ohlc > 0).sum()),
 'bad_price_files':int((audit.bad_price > 0).sum()),'bad_volume_files':int((audit.bad_volume > 0).sum()),
 'missing_adjusted_files':int((audit.missing_adjusted > 0).sum()),
 'zero_volume_files':int((audit.zero_volume > 0).sum()),
 'split_event_files':int((audit.split_events > 0).sum()),
 'dividend_event_files':int((audit.dividend_events > 0).sum()),
 'earliest':str(audit['first'].min()),'latest':str(audit['last'].max()),
 'largest_ohlc_violations':audit.nlargest(8,'bad_ohlc')[['symbol','bad_ohlc']].to_dict('records'),
 'caveat':'Current-listed survivor universe, NOT historical PIT; no certification of unbiased historical tradability.'}
(OUT / 'price_audit_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2),flush=True)

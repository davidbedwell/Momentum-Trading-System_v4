"""Provider-neutral adapter contract and strictly partitioned JSON implementation."""
from pathlib import Path
from typing import Protocol
from datetime import date
import json
import math
from .core import development_year, timestamp


class Adapter(Protocol):
    def load(self, year: int) -> dict: ...
    def provenance(self) -> dict: ...


def validate(data, year):
    development_year(year)
    required = {'listings','prices','financials','market','actions','delistings','sessions','market_caps'}
    if not required <= data.keys():
        raise ValueError('Missing dataset tables: '+str(sorted(required-data.keys())))
    def unique(rows, keys):
        seen = set()
        for row in rows:
            key = tuple(row[k] for k in keys)
            if key in seen: raise ValueError('Duplicate record: '+str(keys))
            seen.add(key)
    unique(data['prices'], ('id','date'))
    unique(data['market'], ('date',))
    unique(data['financials'], ('id','period_end','version'))
    unique(data['sessions'], ('exchange','date'))
    unique(data['delistings'], ('id','date'))
    for table in data.values():
        if not isinstance(table, list): raise ValueError('Tables must be arrays')
        for row in table:
            if not row.get('source'): raise ValueError('Every row requires source provenance')
            for v in row.values():
                if isinstance(v, (float,int)) and not isinstance(v,bool) and not math.isfinite(v):
                    raise ValueError('Nonfinite value')
    for row in data['listings']:
        date.fromisoformat(row['start']);date.fromisoformat(row['end'])
        if row['start'] > row['end']: raise ValueError('Inverted listing interval')
        if not row.get('id') or not row.get('ticker'): raise ValueError('Security ID and dated ticker required')
    for i,a in enumerate(data['listings']):
        for b in data['listings'][i+1:]:
            if a['id']==b['id'] and max(a['start'],b['start'])<=min(a['end'],b['end']):
                raise ValueError('Overlapping listing intervals')
    sessions = {(r['exchange'],r['date']) for r in data['sessions']}
    for exchange,day in sessions:
        if date.fromisoformat(day).year != year: raise ValueError('Session outside requested year')
    for p in data['prices']:
        if date.fromisoformat(p['date']).year != year: raise ValueError('Mixed-year price partition')
        if min(p[k] for k in ('open','high','low','close'))<=0 or p['volume']<0:
            raise ValueError('Invalid OHLCV')
        if not p['low']<=min(p['open'],p['close'])<=max(p['open'],p['close'])<=p['high']:
            raise ValueError('Inconsistent OHLC')
        if not any(l['id']==p['id'] and l['start']<=p['date']<=l['end']
                   and (l['exchange'],p['date']) in sessions for l in data['listings']):
            raise ValueError('Price outside listing membership')
    keys = {(p['id'],p['date']) for p in data['prices']}
    for listing in data['listings']:
        if listing['kind']!='common' or listing['exchange'] not in {'NYSE','NASDAQ'}:continue
        expected = {day for ex,day in sessions if ex==listing['exchange'] and listing['start']<=day<=listing['end']}
        if not expected: raise ValueError('No calendar coverage for eligible listing')
        if any((listing['id'],day) not in keys for day in expected):
            raise ValueError('Incomplete listing session coverage; resolve gaps explicitly')
        if listing['end'][:4]==str(year) and listing.get('end_reason')=='delisting':
            if not any(d['id']==listing['id'] and d['date']==listing['end'] for d in data['delistings']):
                raise ValueError('Missing terminal delisting value')
    for r in data['financials']:
        if not isinstance(r['version'],int) or r['version'] < 1: raise ValueError('Positive financial version required')
        if r['period_type']!='annual' or r['revision_policy']!='original_as_reported':
            raise ValueError('Annual original as-reported financials required')
        date.fromisoformat(r['period_end'])
        public = r['available_at']
        if len(public)==10: date.fromisoformat(public)
        else: timestamp(public)
        timestamp(r['recorded_at'])
        if r['revenue'] is None: raise ValueError('Omit unavailable financial record; do not impute')
    for r in data['market']:
        if date.fromisoformat(r['date']).year!=year or r['close']<=0: raise ValueError('Invalid market series')
    for r in data['delistings']:
        if r['terminal_adjusted_value']<0: raise ValueError('Negative delisting recovery')
    for r in data['actions']:
        date.fromisoformat(r['date'])
        if r['kind'] not in {'split','dividend','merger','spinoff'}: raise ValueError('Unknown action')
        if not r.get('adjustment_reference'): raise ValueError('Unreconciled action')
    for r in data['market_caps']:
        date.fromisoformat(r['date']);timestamp(r['available_at'])
        if r['value']<0: raise ValueError('Negative market cap')
    return data


class JsonAdapter:
    """One manifest per discovery year. No multi-year payload or evaluation API."""
    def __init__(self, manifest):
        self.path = Path(manifest)
        self.meta = None

    def load(self, year):
        development_year(year)  # reject BEFORE opening even the manifest
        meta = json.loads(self.path.read_text())
        if meta['years'] != [year]: raise ValueError('Manifest must declare exactly the requested discovery year')
        if meta.get('schema_version')!=1: raise ValueError('Unknown schema version')
        for key in ('source','release_date','revision_policy','coverage','adjustment_policy'):
            if not meta.get(key):raise ValueError('Missing manifest provenance '+key)
        if meta['revision_policy']!='original_as_reported': raise ValueError('Restated data prohibited')
        required = ('historical_listing_membership','includes_delistings','corporate_actions_reconciled',
                    'pit_financial_availability','asof_adjusted_ohlcv','complete_exchange_sessions')
        if any(meta.get(k) is not True for k in required): raise ValueError('Coverage attestation incomplete')
        payload = (self.path.parent/meta['payload']).resolve()
        if not payload.is_relative_to(self.path.parent.resolve()):raise ValueError('Payload must remain in manifest directory')
        self.meta = meta
        return validate(json.loads(payload.read_text()), year)

    def provenance(self):
        if self.meta is None:raise ValueError('Load first')
        return self.meta

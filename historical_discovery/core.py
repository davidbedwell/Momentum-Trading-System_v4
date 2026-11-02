"""Pure, deterministic research primitives. All public year APIs fail closed."""
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math

LOCKED = frozenset({2010, 2011})


def development_year(year):
    if year not in range(2005, 2010):
        raise ValueError('Only 2005–2009 discovery is enabled; 2010/2011 labels are locked')


def timestamp(value):
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('Timezone required')
    return value.astimezone(timezone.utc)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Config:
    calendar_threshold: float = 0.50
    advance_threshold: float = 1.00
    top_k: int = 2
    date_precision_lag_days: int = 2
    snapshot_month: int = 6
    snapshot_day: int = 30
    candidates: tuple = ('equal', 'diagonal_covariance')
    features: tuple = ('momentum', 'log_dollar_volume', 'market_return', 'revenue_growth')
    metrics: tuple = ('recall_at_k', 'precision_at_k', 'spearman', 'lead_days', 'remaining_upside')

    def __post_init__(self):
        if self.top_k < 1 or self.date_precision_lag_days < 1:
            raise ValueError('Positive K and conservative lag required')
        if self.calendar_threshold <= 0 or self.advance_threshold <= 0:
            raise ValueError('Positive winner thresholds required')
        if not self.candidates or set(self.candidates) - {'equal', 'diagonal_covariance'}:
            raise ValueError('Unknown model candidate')
        date(2005, self.snapshot_month, self.snapshot_day)


def universe(data, day):
    """Permanent security IDs and dated listing intervals, never current tickers."""
    accepted, excluded = set(), []
    for row in data['listings']:
        if row['start'] <= day <= row['end']:
            if row['exchange'] in {'NYSE', 'NASDAQ'} and row['kind'] == 'common':
                accepted.add(row['id'])
            else:
                excluded.append({'id': row['id'], 'reason': 'exchange_or_security_type'})
    return sorted(accepted), excluded


def usable_at(row, cfg):
    # A date alone is conservatively usable only after the end of that date + lag.
    public = row['available_at']
    if len(public) == 10:
        public = (date.fromisoformat(public) + timedelta(days=cfg.date_precision_lag_days + 1)).isoformat() + 'T00:00:00Z'
    return max(timestamp(public), timestamp(row['recorded_at']))


def features(data, year, cfg):
    development_year(year)
    day = date(year, cfg.snapshot_month, cfg.snapshot_day).isoformat()
    cutoff = timestamp(day + 'T23:59:59Z')
    ids, exclusions = universe(data, day)
    out = {}
    for sid in ids:
        prices = sorted((p for p in data['prices'] if p['id'] == sid and p['date'] <= day
                         and p['date'][:4] == str(year)), key=lambda p: p['date'])
        if len(prices) < 2:
            exclusions.append({'id': sid, 'reason': 'insufficient_pre_snapshot_prices'})
            continue
        first, last = prices[0], prices[-1]
        reports = [r for r in data['financials'] if r['id'] == sid and usable_at(r, cfg) <= cutoff
                   and r['period_end'] <= day and r['version'] == 1]
        # Earliest reported version per period, even when a later restatement exists.
        original = {}
        for r in sorted(reports, key=lambda r: (usable_at(r, cfg), r['version'])):
            original.setdefault(r['period_end'], r)
        ordered = sorted(original.values(), key=lambda r: r['period_end'])
        growth = None
        if len(ordered) >= 2:
            prev, latest = ordered[-2:]
            # Compare fiscal years only; mixed quarterly periods are rejected by schema.
            if prev['revenue'] > 0 and 300 <= (date.fromisoformat(latest['period_end']) - date.fromisoformat(prev['period_end'])).days <= 430:
                growth = latest['revenue'] / prev['revenue'] - 1
        market = sorted((p for p in data['market'] if p['date'] <= day and p['date'][:4] == str(year)), key=lambda p:p['date'])
        if len(market) < 2:
            exclusions.append({'id': sid, 'reason': 'missing_market_history'})
            continue
        caps = [c for c in data.get('market_caps', []) if c['id'] == sid and c['date'] <= day
                and timestamp(c['available_at']) <= cutoff]
        out[sid] = {'momentum': last['close'] / first['open'] - 1,
                    'log_dollar_volume': math.log1p(sum(p['close'] * p['volume'] for p in prices) / len(prices)),
                    'market_return': market[-1]['close'] / market[0]['close'] - 1,
                    'revenue_growth': growth, 'snapshot_close': last['close'],
                    'market_cap': max(caps, key=lambda c:c['date'])['value'] if caps else None}
    return day, out, exclusions


def labels(data, year, cfg):
    development_year(year)
    result = {}
    for sid in sorted({p['id'] for p in data['prices'] if p['date'][:4] == str(year)}):
        rows = sorted((p for p in data['prices'] if p['id'] == sid and p['date'][:4] == str(year)), key=lambda p:p['date'])
        eligible = [p for p in rows if sid in universe(data, p['date'])[0]]
        if len(eligible) < 2:
            continue
        rows = eligible
        # Terminal total-return value is required for a security that delists in-year.
        terminal = [x for x in data['delistings'] if x['id'] == sid and x['date'][:4] == str(year)]
        final = terminal[0]['terminal_adjusted_value'] if terminal else rows[-1]['close']
        calendar = final / rows[0]['open'] - 1
        low, low_day = rows[0]['low'], rows[0]['date']
        advance, start, peak = -1.0, low_day, rows[1]['date']
        for row in rows[1:]:
            gain = row['high'] / low - 1
            if gain > advance:
                advance, start, peak = gain, low_day, row['date']
            if row['low'] < low:
                low, low_day = row['low'], row['date']
        caps = [c for c in data.get('market_caps', []) if c['id'] == sid and c['date'] <= rows[0]['date']
                and timestamp(c['available_at']) <= timestamp(rows[0]['date']+'T23:59:59Z')]
        result[sid] = {'market_cap_at_start': max(caps,key=lambda c:c['date'])['value'] if caps else None,
                       'calendar_return': calendar, 'advance': advance, 'start': start, 'peak': peak,
                       'winner': calendar >= cfg.calendar_threshold or advance >= cfg.advance_threshold,
                       'rank_value': max(calendar, advance),
                       'mean_dollar_volume': sum(p['close']*p['volume'] for p in rows)/len(rows)}
    return result


ARMS = {'chart': ('momentum','log_dollar_volume','market_return'),
        'fundamentals': ('revenue_growth',),
        'combined': ('momentum','log_dollar_volume','market_return','revenue_growth')}


def predict(train, current, columns, candidate):
    """Fixed candidates; all scaling and supervised weights use earlier years only."""
    if not train:
        raise ValueError('No known prior year; first year is warmup')
    means = [sum(x[c] for x,y in train)/len(train) for c in columns]
    scales = [max(1e-12, math.sqrt(sum((x[c]-m)**2 for x,y in train)/len(train))) for c,m in zip(columns,means)]
    target_mean = sum(y for x,y in train)/len(train)
    weights = [1.0]*len(columns)
    if candidate == 'diagonal_covariance':
        weights = [sum(((x[c]-m)/s)*(y-target_mean) for x,y in train)/len(train)
                   for c,m,s in zip(columns,means,scales)]
    scores = {sid:sum(w*(x[c]-m)/s for c,m,s,w in zip(columns,means,scales,weights)) for sid,x in current.items()}
    return scores, {'means':means,'scales':scales,'weights':weights,'training_rows':len(train)}


def ranks(values):
    ordered = sorted(values, key=lambda k:values[k])
    result = {}
    for key in ordered:
        ties = [i+1 for i,k in enumerate(ordered) if values[k] == values[key]]
        result[key] = sum(ties)/len(ties)
    return result


def metrics(scores, actual, snapshots, day, k):
    ids = sorted(set(scores) & set(actual))
    if not ids:
        return {'n':0,'recall_at_k':None,'precision_at_k':None,'spearman':None,'top':[]}
    ordered = sorted(ids, key=lambda s:(-scores[s], s))
    top = ordered[:k]
    winners = {s for s in ids if actual[s]['winner']}
    hits = len(set(top)&winners)
    a,b = ranks({s:scores[s] for s in ids}), ranks({s:actual[s]['rank_value'] for s in ids})
    mean = (len(ids)+1)/2
    denom = math.sqrt(sum((a[s]-mean)**2 for s in ids)*sum((b[s]-mean)**2 for s in ids))
    details = [{'id':s,'winner':actual[s]['winner'],
                'lead_days':(date.fromisoformat(actual[s]['peak'])-date.fromisoformat(day)).days,
                'remaining_upside':snapshots[s]['future_high']/snapshots[s]['snapshot_close']-1}
               for s in top]
    return {'n':len(ids),'winner_count':len(winners),'recall_at_k':hits/len(winners) if winners else None,
            'precision_at_k':hits/len(top),'spearman':sum((a[s]-mean)*(b[s]-mean) for s in ids)/denom if denom else None,
            'actual_ranking':sorted(ids,key=lambda s:(-actual[s]['rank_value'],s)), 'predicted_ranking':ordered,'top':details}

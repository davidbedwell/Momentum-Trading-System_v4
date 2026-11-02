import calendar
import datetime as dt
import math
import statistics as st
from collections import defaultdict

SIGNALS = ('H1', 'H2', 'H3', 'H4', 'H5', 'H6')


def ranks(values):
    """Midrank percentiles; ties receive identical ranks, missing stays missing."""
    good = sorted(v for v in values if v is not None and math.isfinite(v))
    return [((sum(x < v for x in good)+(sum(x == v for x in good)+1)/2)/len(good)) if v is not None and math.isfinite(v) else None for v in values]


def ic(x, y):
    if len(x) < 3:
        return None
    x, y = ranks(x), ranks(y)
    mx, my = st.mean(x), st.mean(y)
    den = math.sqrt(sum((v-mx)**2 for v in x)*sum((v-my)**2 for v in y))
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/den if den else None


def hac(values, lag):
    n = len(values)
    if n < max(3, lag+2):
        return dict(n=n, mean=st.mean(values) if n else None, se=None, t=None, p=None)
    mean = st.mean(values)
    z = [v-mean for v in values]
    var = sum(v*v for v in z)/n
    for k in range(1, lag+1):
        var += 2*(1-k/(lag+1))*sum(z[i]*z[i-k] for i in range(k,n))/n
    se = math.sqrt(max(0,var)/n)
    return dict(n=n, mean=mean, se=se, t=mean/se if se else None, p=math.erfc(abs(mean/se)/math.sqrt(2)) if se else None)


def holm(ps, family_size=None):
    ordered = sorted((v,k) for k,v in ps.items() if v is not None)
    out, previous = {}, 0
    for i,(p,k) in enumerate(ordered):
        previous = max(previous, min(1, p*((family_size if family_size is not None else len(ordered))-i)))
        out[k] = previous
    return out


def add_months(date, n):
    d = dt.date.fromisoformat(date)
    m = d.year*12+d.month-1+n
    y, m = divmod(m,12)
    return str(dt.date(y,m+1,calendar.monthrange(y,m+1)[1]))


def technical(hist):
    p = [float(r['adj_close']) for r in hist]
    monthly = {}
    for r in hist:
        if 'date' in r:
            monthly[r['date'][:7]] = float(r['adj_close'])
    momentum = None
    if hist and 'date' in hist[-1]:
        t = hist[-1]['date']
        numerator, denominator = add_months(t, -2)[:7], add_months(t, -13)[:7]
        if numerator in monthly and denominator in monthly:
            momentum = monthly[numerator] / monthly[denominator] - 1
    returns = [b/a-1 for a,b in zip(p[-253:],p[-252:])] if len(p) >= 253 else []
    return dict(H1=momentum, H2=p[-1]/max(p[-252:]) if len(p)>=252 else None,
                H5=st.stdev(returns)*math.sqrt(252) if len(returns)==252 else None)


def price_issues(prices):
    issues = []
    for symbol, rows in prices.items():
        for a,b in zip(rows,rows[1:]):
            gap = (dt.date.fromisoformat(b['date'])-dt.date.fromisoformat(a['date'])).days
            ratio = float(b['adj_close'])/float(a['adj_close'])
            if gap > 7 or not .5 < ratio < 2:
                issues.append(dict(symbol=symbol, date=b['date'], calendar_gap=gap, adjusted_ratio=ratio))
    return issues


def form_rows(prices, members, years, fundamentals, earnings, sessions=None, closes=None):
    from .adapters import sec_quality, earnings_signal
    calendar_dates = sessions if sessions is not None else sorted({r['date'] for rows in prices.values() for r in rows})
    months = {}
    for d in calendar_dates:
        months[d[:7]] = d
    output = []
    formations = defaultdict(list)
    for t in months.values():
        if t > '2026-09-30' or t < '2006-01-01':
            continue
        if int(t[:4]) not in years:
            continue
        for member in members:
            if not (member['start'] <= t < member['end']):
                continue
            symbol = member['symbol']
            rows = prices.get(symbol, [])
            hist = [r for r in rows if r['date'] <= t]
            if not hist or hist[-1]['date'] != t:
                continue
            base = dict(symbol=symbol, sector=member['sector'], asof=t, **technical(hist))
            base['H3'] = earnings_signal(earnings.get(symbol, {}), t, (closes or {}).get(t))
            base['H4'] = sec_quality(fundamentals.get(symbol, {}), t, (closes or {}).get(t))
            formations[t, member['sector']].append(base)
            future = [r for r in rows if r['date'] > t]
            if not future:
                continue
            entry = future[0]
            next_session = next((d for d in calendar_dates if d > t), None)
            if entry['date'] != next_session or entry.get('adj_open') in (None, ''):
                continue
            opening = entry.get('adj_open') not in (None, '')
            entry_price = float(entry['adj_open'] if opening else entry['adj_close'])
            for h in (1,3,6):
                target = add_months(t,h)
                exits = [r for r in rows if entry['date'] <= r['date'] <= target]
                # Require global calendar to reach horizon and symbol to reach same final session.
                market_end = max((d for d in calendar_dates if d <= target), default='')
                if not exits or calendar_dates[-1] < target or exits[-1]['date'] != market_end:
                    continue
                next_month_end = months.get(add_months(t,1)[:7])
                rebalance_date = next((d for d in calendar_dates if next_month_end and d > next_month_end), None)
                rebalance = next((r for r in rows if r['date'] == rebalance_date), {})
                drift_return = float(rebalance['adj_open'])/entry_price-1 if rebalance.get('adj_open') not in (None,'') else None
                output.append(dict(base, rebalance_return=drift_return, horizon=h, entry=entry['date'], exit=exits[-1]['date'], execution='next-open provisional' if opening else 'next-close proxy', forward_return=float(exits[-1]['adj_close'])/entry_price-1))
    for group in formations.values():
        for key in SIGNALS[:5]:
            for r, rank in zip(group, ranks([r[key] for r in group])):
                r[key+'_rank'] = rank
        for r, rank in zip(group, ranks([-r['H5'] if r['H5'] is not None else None for r in group])):
            r['H5_inverse_rank'] = rank
        for r in group:
            rr = [r[k+'_rank'] for k in ('H1','H3','H4')] + [r['H5_inverse_rank']]
            r['H6_rank'] = st.mean(rr) if all(v is not None for v in rr) else None
        for r, rank in zip(group, ranks([r['H6_rank'] for r in group])):
            r['H6_rank'] = rank
    lookup = {(r['asof'], r['symbol']): r for g in formations.values() for r in g}
    groups = defaultdict(list)
    for r in output:
        r.update({k: v for k,v in lookup[r['asof'],r['symbol']].items() if k.endswith('_rank')})
        groups[r['asof'], r['sector'], r['horizon']].append(r)
    for group in groups.values():
        expected = sum(m['sector'] == group[0]['sector'] and m['start'] <= group[0]['asof'] < m['end'] for m in members)
        benchmark = st.median(r['forward_return'] for r in group) if len(group) == expected else None
        for r in group:
            r['excess'] = r['forward_return']-benchmark if benchmark is not None else None
    return output


def metrics(rows, allowed=None, evaluation_dates=None, excluded_years=()):
    groups = defaultdict(list)
    for r in rows:
        groups[r['asof'],r['sector'],r['horizon']].append(r)
    monthly, prior = [], {}
    for (date,sector,h), group in sorted(groups.items()):
        for signal in SIGNALS:
            if allowed is not None and f'{signal}_{h}' not in allowed:
                continue
            g = [r for r in group if r[signal+'_rank'] is not None and r['excess'] is not None]
            top = [r for r in g if r[signal+'_rank'] > .9]
            bottom = [r for r in g if r[signal+'_rank'] <= .1]
            if signal == 'H5':
                top, bottom = bottom, top
            weights = {r['symbol']: 1/len(top) for r in top}
            weights.update({r['symbol']: -1/len(bottom) for r in bottom})
            key = sector,h,signal
            previous = prior.get(key)
            turnover = None
            if top and bottom:
                if previous is None:
                    turnover = 2.0
                elif add_months(previous['date'],1)[:7] == date[:7] and previous['weights']:
                    drifted = {}
                    valid = True
                    for sign in (1,-1):
                        leg = {s:abs(w) for s,w in previous['weights'].items() if w*sign > 0}
                        if not leg or any(previous['returns'].get(s) is None for s in leg):
                            valid = False
                            break
                        nav = sum(w*(1+previous['returns'][s]) for s,w in leg.items())
                        if nav <= 0:
                            valid = False
                            break
                        drifted.update({s:sign*w*(1+previous['returns'][s])/nav for s,w in leg.items()})
                    if valid:
                        turnover = sum(abs(weights.get(s,0)-drifted.get(s,0)) for s in weights.keys()|drifted.keys())
            prior[key] = dict(date=date,weights=weights if top and bottom else {},
                              returns={r['symbol']:r.get('rebalance_return') for r in group})
            spread = st.mean(r['excess'] for r in top)-st.mean(r['excess'] for r in bottom) if top and bottom else None
            half = [r for r in g if r[signal+'_rank'] > .5]
            monthly.append(dict(asof=date, year=int(date[:4]), sector=sector, horizon=h, signal=signal, n=len(g), eligible=len(group), coverage=len(g)/len(group), ic=ic([r[signal+'_rank'] for r in g],[r['excess'] for r in g]), spread=spread, hit_rate=st.mean(r['excess']>0 for r in half) if half else None, turnover=turnover, net_spread_15bps=spread-.0015*turnover if spread is not None and turnover is not None else None))
    if evaluation_dates is not None:
        monthly = [r for r in monthly if r['asof'] in evaluation_dates]
    summary = {}
    for h in (1,3,6):
        for signal in SIGNALS:
            if allowed is not None and f'{signal}_{h}' not in allowed:
                continue
            bydate = defaultdict(list)
            for r in monthly:
                if r['horizon']==h and r['signal']==signal and r['ic'] is not None:
                    bydate[r['asof']].append(r['ic'])
            # Equal weight sectors per month; never count sectors as independent months.
            dates = sorted(bydate)
            values = [st.mean(bydate[d]) for d in dates]
            result = calendar_hac(dates, values, {1:3,3:5,6:5}[h])
            contiguous = all(add_months(a,1)[:7] == b[:7] for a,b in zip(dates,dates[1:]))
            direction = -1 if signal == 'H5' else 1
            result['fraction_positive_ic'] = st.mean(v*direction > 0 for v in values) if values else None
            result['positive_blocks'] = sum(bool(block) and st.mean(block)*direction > 0 for block in
                ([v for d,v in zip(dates,values) if lo <= int(d[:4]) <= hi] for lo,hi in ((2006,2008),(2009,2010),(2011,2013),(2014,2015))))
            result['contiguous'] = contiguous
            result['exploratory'] = h == 6
            result['complete'] = False  # Executor sets this only after source and monthly coverage checks.
            # Missing months suppress inference except the predeclared contaminated-year exclusion.
            missing = []
            if dates:
                cursor = dates[0]
                while cursor[:7] < dates[-1][:7]:
                    if cursor[:7] not in {d[:7] for d in dates}:
                        missing.append(int(cursor[:4]))
                    cursor = add_months(cursor,1)
            if missing and not set(missing) <= set(excluded_years):
                result.update(se=None,t=None,p=None)
            summary[f'{signal}_{h}'] = result
    correction = holm({k:v['p'] for k,v in summary.items() if not v['exploratory']}, family_size=12)
    for k,v in summary.items():
        v['holm_p'] = correction.get(k)
    return monthly, summary


def placebo(rows, signal, horizon, seed=0, shuffles=1000):
    """Permute returns independently within each sector/month, average sectors then months."""
    import random
    if shuffles != 1000:
        raise ValueError('Protocol requires exactly 1000 shuffles')
    groups = defaultdict(list)
    for r in rows:
        if r['horizon'] == horizon and r.get(signal+'_rank') is not None and r.get('excess') is not None:
            groups[r['asof'], r['sector']].append(r)
    direction = -1 if signal == 'H5' else 1
    prepared = []
    for (date, _), group in sorted(groups.items()):
        x = ranks([r[signal+'_rank'] for r in group])
        y = ranks([r['excess'] for r in group])
        if len(x) < 3:
            continue
        mx,my = st.mean(x),st.mean(y)
        x,y = [v-mx for v in x],[v-my for v in y]
        den = math.sqrt(sum(v*v for v in x)*sum(v*v for v in y))
        if den:
            prepared.append((date,x,y,den))
    def statistic(shuffle=False):
        months = defaultdict(list)
        for date,x,original,den in prepared:
            y = original.copy()
            if shuffle:
                rng.shuffle(y)
            months[date].append(sum(a*b for a,b in zip(x,y))/den*direction)
        return st.mean(st.mean(v) for v in months.values()) if months else None
    rng = random.Random(seed)
    real = statistic()
    if real is None:
        return dict(real=None, percentile99=None, passed=False,shuffles=0,seed=seed,status='undefined IC; no valid permutation statistic')
    null = sorted(statistic(True) for _ in range(shuffles))
    cutoff = null[math.ceil(.99 * shuffles)-1]
    return dict(real=real, percentile99=cutoff, passed=real > cutoff, shuffles=shuffles, seed=seed)


def calendar_hac(dates, values, lag):
    """HAC using calendar distances; excluded years never become adjacent observations."""
    result = hac(values, lag)
    if result['t'] is None:
        return result
    mean = st.mean(values)
    centered = {int(d[:4])*12+int(d[5:7]):v-mean for d,v in zip(dates,values)}
    n = len(values)
    variance = sum(v*v for v in centered.values())/n
    for k in range(1,lag+1):
        variance += 2*(1-k/(lag+1))*sum(v*centered.get(m-k,0) for m,v in centered.items())/n
    se = math.sqrt(max(0,variance)/n)
    return dict(n=n,mean=mean,se=se,t=mean/se if se else None,
                p=math.erfc(abs(mean/se)/math.sqrt(2)) if se else None)

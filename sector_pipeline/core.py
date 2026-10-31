import calendar
import datetime as dt
import math
import statistics as st
from collections import defaultdict

SIGNALS = ('H1', 'H2', 'H3', 'H4', 'H5', 'composite')


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
        return dict(n=n, mean=st.mean(values) if n else None, se=None, p=None)
    mean = st.mean(values)
    z = [v-mean for v in values]
    var = sum(v*v for v in z)/n
    for k in range(1, lag+1):
        var += 2*(1-k/(lag+1))*sum(z[i]*z[i-k] for i in range(k,n))/n
    se = math.sqrt(max(0,var)/n)
    return dict(n=n, mean=mean, se=se, p=math.erfc(abs(mean/se)/math.sqrt(2)) if se else None)


def holm(ps):
    ordered = sorted((v,k) for k,v in ps.items() if v is not None)
    out, previous = {}, 0
    for i,(p,k) in enumerate(ordered):
        previous = max(previous, min(1, p*(len(ordered)-i)))
        out[k] = previous
    return out


def add_months(date, n):
    d = dt.date.fromisoformat(date)
    m = d.year*12+d.month-1+n
    y, m = divmod(m,12)
    return str(dt.date(y,m+1,calendar.monthrange(y,m+1)[1]))


def technical(hist):
    p = [float(r['adj_close']) for r in hist]
    return dict(H1=p[-22]/p[-253]-1 if len(p)>=253 else None,
                H2=p[-1]/p[-64]-1 if len(p)>=64 else None,
                H3=p[-1]/max(p[-252:]) if len(p)>=252 else None)


def price_issues(prices):
    issues = []
    for symbol, rows in prices.items():
        for a,b in zip(rows,rows[1:]):
            gap = (dt.date.fromisoformat(b['date'])-dt.date.fromisoformat(a['date'])).days
            ratio = float(b['adj_close'])/float(a['adj_close'])
            if gap > 7 or not .5 < ratio < 2:
                issues.append(dict(symbol=symbol, date=b['date'], calendar_gap=gap, adjusted_ratio=ratio))
    return issues


def form_rows(prices, members, years, fundamentals, earnings):
    from .adapters import sec_quality, earnings_signal
    calendar_dates = sorted({r['date'] for rows in prices.values() for r in rows})
    months = {}
    for d in calendar_dates:
        months[d[:7]] = d
    output = []
    formations = defaultdict(list)
    for t in months.values():
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
            base['H4'] = earnings_signal(earnings.get(symbol, {}), t)
            base['H5'] = sec_quality(fundamentals.get(symbol, {}), t)
            formations[t, member['sector']].append(base)
            future = [r for r in rows if r['date'] > t]
            if not future:
                continue
            entry = future[0]
            opening = entry.get('adj_open') not in (None, '')
            entry_price = float(entry['adj_open'] if opening else entry['adj_close'])
            for h in (1,3,6):
                target = add_months(t,h)
                exits = [r for r in rows if entry['date'] <= r['date'] <= target]
                # Require global calendar to reach horizon and symbol to reach same final session.
                market_end = max((d for d in calendar_dates if d <= target), default='')
                if not exits or calendar_dates[-1] < target or exits[-1]['date'] != market_end:
                    continue
                output.append(dict(base, horizon=h, entry=entry['date'], exit=exits[-1]['date'], execution='next-open provisional' if opening else 'next-close proxy', forward_return=float(exits[-1]['adj_close'])/entry_price-1))
    for group in formations.values():
        for key in SIGNALS[:5]:
            for r, rank in zip(group, ranks([r[key] for r in group])):
                r[key+'_rank'] = rank
        for r in group:
            rr = [r[k+'_rank'] for k in SIGNALS[:5]]
            r['composite_rank'] = st.mean(rr) if all(v is not None for v in rr) else None
    lookup = {(r['asof'], r['symbol']): r for g in formations.values() for r in g}
    groups = defaultdict(list)
    for r in output:
        r.update({k: v for k,v in lookup[r['asof'],r['symbol']].items() if k.endswith('_rank')})
        groups[r['asof'], r['sector'], r['horizon']].append(r)
    for group in groups.values():
        benchmark = st.mean(r['forward_return'] for r in group)
        for r in group:
            r['excess'] = r['forward_return']-benchmark
    return output


def metrics(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r['asof'],r['sector'],r['horizon']].append(r)
    monthly, prior = [], {}
    for (date,sector,h), group in sorted(groups.items()):
        for signal in SIGNALS:
            g = [r for r in group if r[signal+'_rank'] is not None]
            top = [r for r in g if r[signal+'_rank'] >= .8]
            bottom = [r for r in g if r[signal+'_rank'] <= .2]
            weights = {r['symbol']: 1/len(top) for r in top}
            key = sector,h,signal
            prev = prior.get(key,{})
            turnover = sum(abs(weights.get(s,0)-prev.get(s,0)) for s in weights.keys()|prev.keys())
            prior[key] = weights
            spread = st.mean(r['excess'] for r in top)-st.mean(r['excess'] for r in bottom) if top and bottom else None
            half = [r for r in g if r[signal+'_rank'] > .5]
            monthly.append(dict(asof=date, year=int(date[:4]), sector=sector, horizon=h, signal=signal, n=len(g), eligible=len(group), coverage=len(g)/len(group), ic=ic([r[signal+'_rank'] for r in g],[r['excess'] for r in g]), spread=spread, hit_rate=st.mean(r['excess']>0 for r in half) if half else None, turnover=turnover, top_net_10bps=st.mean(r['excess'] for r in top)-.001*turnover if top else None, top_net_25bps=st.mean(r['excess'] for r in top)-.0025*turnover if top else None))
    summary = {}
    for h in (1,3,6):
        for signal in SIGNALS:
            bydate = defaultdict(list)
            for r in monthly:
                if r['horizon']==h and r['signal']==signal and r['ic'] is not None:
                    bydate[r['asof']].append(r['ic'])
            # Equal weight sectors per month; never count sectors as independent months.
            summary[f'{signal}_{h}'] = hac([st.mean(v) for _,v in sorted(bydate.items())], h-1)
    correction = holm({k:v['p'] for k,v in summary.items() if not k.startswith('composite')})
    for k,v in summary.items():
        v['holm_p'] = correction.get(k)
    return monthly, summary

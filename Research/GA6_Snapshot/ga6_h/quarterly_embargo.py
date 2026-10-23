"""GA6-H causal quarterly earnings entry embargo."""
from bisect import bisect_left
from datetime import date, datetime, timezone

def day(x):
    if isinstance(x, datetime): return x.date()
    if isinstance(x, date): return x
    return date.fromisoformat(str(x)[:10])

def instant(x):
    d = x if isinstance(x, datetime) else datetime.fromisoformat(str(x).replace('Z', '+00:00'))
    if d.tzinfo is None: raise ValueError('timestamp must include timezone')
    return d.astimezone(timezone.utc)

def embargo_sessions(disclosures, sessions, decision_at=None):
    days = sorted(set(day(s) for s in sessions))
    decision = instant(decision_at) if decision_at is not None else None
    blocked = set()
    for item in disclosures:
        if isinstance(item, dict):
            event = day(item['date'])
            if decision is not None:
                known = item.get('known_at')
                if known is None or instant(known) > decision: continue
        else:
            if decision is not None: continue
            event = day(item)
        i = bisect_left(days, event)
        if i >= len(days): continue
        blocked.update(days[j] for j in range(max(0, i-2), min(len(days), i+3)))
    return frozenset(blocked)

def entry_allowed(ticker, session, schedules, sessions, decision_at, verified_tickers=None):
    """Fail closed: missing verified schedule prevents new entries/increases."""
    if decision_at is None: raise ValueError('decision_at required')
    instant(decision_at)
    if verified_tickers is None or ticker not in verified_tickers: return False
    if ticker not in schedules: return False
    return day(session) not in embargo_sessions(schedules[ticker], sessions, decision_at)

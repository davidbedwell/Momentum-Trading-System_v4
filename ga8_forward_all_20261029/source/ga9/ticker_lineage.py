"""Immutable, content-addressed notice facts; identity never grants eligibility."""
from dataclasses import dataclass, asdict
from hashlib import sha256
import json

@dataclass(frozen=True)
class Event:
    event_id: str
    kind: str
    security_id: str
    old_symbol: str
    new_symbol: str | None
    effective_at: str
    known_at: str | None
    publication_date: str
    source: str
    detail: str
    predecessor: str | None = None

    @property
    def digest(self):
        return sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

    def visible(self, decision_at):
        # ISO UTC timestamps only; unknown publication time never becomes midnight.
        from datetime import datetime
        decision = datetime.fromisoformat(decision_at.replace('Z', '+00:00'))
        if decision.tzinfo is None:
            raise ValueError('Timezone required')
        return self.known_at is not None and datetime.fromisoformat(self.known_at.replace('Z', '+00:00')) <= decision

FB = Event('ECA2022-125', 'rename', 'CUSIP:30303M102', 'FB', 'META',
           '2022-06-09', '2022-06-04T04:00:00Z', '2022-06-03',
           'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2022-125',
           'Same Class A security. known_at is conservative next New York midnight; exact publication time unavailable.')
XLNX = Event('ECA2022-23:last-trade', 'last_trade', 'CUSIP:983919101', 'XLNX', None,
             '2022-02-11', None, '2022-02-10',
             'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2022-23',
             'Updated page: last trade Feb 11; halted Feb 14; suspended Feb 15. Update publication time unknown.')
MERGER = Event('ECA2022-23:closed', 'merger', XLNX.security_id, 'XLNX', 'AMD',
               '2022-02-14', None, '2022-02-10', XLNX.source,
               '1.7234 AMD shares per XLNX share; successor is a distinct security, never a bar alias.', XLNX.digest)
EVENTS = (FB, XLNX, MERGER)


def historical_identity(symbol, day):
    """Retrospective evidence resolution, NOT a PIT trading authorization."""
    from datetime import date
    date.fromisoformat(day)
    if symbol in ('FB', 'META'):
        return dict(security_id=FB.security_id, effective_symbol='FB' if day < FB.effective_at else 'META',
                    event_digest=FB.digest, trading_eligible=False)
    if symbol == 'XLNX':
        return dict(security_id=XLNX.security_id, effective_symbol='XLNX',
                    post_last_trade=day > XLNX.effective_at, event_digest=XLNX.digest, trading_eligible=False)
    raise ValueError('Unsupported identity; AMD cannot be used as an XLNX alias')

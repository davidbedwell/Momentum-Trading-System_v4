"""PIT daily A/B/C -> Defensive -> R-1 replay, fail-closed on missing signals.

No trading fills or historical detector reconstruction are claimed.
"""
from dataclasses import dataclass
from .defensive_state_controller import DefensiveStateController

@dataclass(frozen=True)
class DayRecord:
    date: str
    a: bool
    b: bool
    c: bool
    r1: bool
    b1: bool = False


def replay(records):
    ctl = DefensiveStateController()
    result = []
    previous = None
    for row in records:
        if not isinstance(row, DayRecord):
            raise TypeError('expected DayRecord with independently computed PIT signals')
        if not row.date or (previous is not None and row.date <= previous):
            raise ValueError('dates must be nonempty, strictly increasing and unique')
        if any(type(x) is not bool for x in (row.a, row.b, row.b1, row.c, row.r1)):
            raise ValueError('A/B/B1/C/R1 must be observed booleans; missing signals cannot be inferred')
        prior = ctl.defensive
        actions = ctl.update(abc_crash_detected=row.a or row.b or row.b1 or row.c, r1_confirmed=row.r1)
        result.append(dict(date=row.date, state='DEFENSIVE' if ctl.defensive else 'NORMAL',
                           crash_entry=not prior and ctl.defensive,
                           r1_exit=prior and not ctl.defensive,
                           cash_first_actions=list(actions)))
        previous = row.date
    return result

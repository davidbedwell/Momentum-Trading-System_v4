"""Fail-closed, causal Normal/Defensive close-state tape for G4 research.

Inputs MUST be independently computed from information available by each close.
This module does not infer or tune crash signals from future market outcomes.
"""
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class RegimeClose:
    day: date
    a: bool
    b: bool
    b1: bool
    c: bool
    r1: bool


def compile_normal_tape(rows, *, initial_state='NORMAL'):
    """Return immutable (date, state, reasons) records; A/B/B1/C outrank R1.

    A Defensive declaration at close D cancels pending Normal entries and
    requires liquidation at the next executable open; not at D's close.
    """
    if initial_state not in ('NORMAL', 'DEFENSIVE'):
        raise ValueError('invalid initial state')
    state = initial_state
    previous = None
    output = []
    for row in rows:
        if not isinstance(row, RegimeClose):
            raise TypeError('every row must be a RegimeClose with complete signals')
        if not isinstance(row.day, date) or (previous is not None and row.day <= previous):
            raise ValueError('dates must be strictly ascending')
        for name in ('a', 'b', 'b1', 'c', 'r1'):
            if type(getattr(row, name)) is not bool:
                raise ValueError('missing or non-boolean signal: ' + name)
        active = tuple(name.upper() for name in ('a', 'b', 'b1', 'c') if getattr(row, name))
        if active:
            state = 'DEFENSIVE'
            reason = active
        elif state == 'DEFENSIVE' and row.r1:
            state = 'NORMAL'
            reason = ('R1_RELEASE',)
        else:
            reason = ('HOLD_' + state,)
        output.append((row.day, state, reason))
        previous = row.day
    if not output:
        raise ValueError('empty controller tape')
    return tuple(output)


def normal_entry_decisions(tape):
    """Decisions at close T; any permitted order executes no earlier than T+1 open."""
    return tuple((day, state == 'NORMAL') for day, state, _ in tape)


def defensive_transition_dates(tape):
    return tuple(day for i, (day, state, _) in enumerate(tape)
                 if state == 'DEFENSIVE' and (i == 0 or tape[i-1][1] != 'DEFENSIVE'))

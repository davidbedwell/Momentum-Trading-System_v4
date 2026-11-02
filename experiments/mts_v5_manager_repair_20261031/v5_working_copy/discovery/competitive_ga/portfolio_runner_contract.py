"""Runner control plane. No fabricated signals, defense or market returns."""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Window:
    train_years: tuple
    forward_year: int


def windows(years=5):
    if years < 2: raise ValueError('need training and forward years')
    return tuple(Window(tuple(range(1, y)), y) for y in range(2, years+1))


def run_walkforward(*, fit: Callable, evaluate: Callable, years=5):
    """Fit only earlier years, freeze once, evaluate both defense modes on next year.

    fit(train_years) returns immutable manager snapshot. evaluate(snapshot, year,
    defense_enabled) returns independent observed replay metrics. Callbacks must
    implement genuine GA6/GA7 proposals and actual defense, not synthetic scores.
    """
    records = []
    for window in windows(years):
        frozen = fit(window.train_years)
        if frozen is None: raise ValueError('missing frozen manager')
        off = evaluate(frozen, window.forward_year, False)
        on = evaluate(frozen, window.forward_year, True)
        if off is None or on is None: raise ValueError('both paired replays required')
        records.append({'train_years':window.train_years, 'forward_year':window.forward_year,
                        'defense_off':off, 'defense_on':on})
    return tuple(records)

import pytest
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.native_replay_bridge import signals_for_close


def proposal(family, ticker):
    return NativeProposal('2020-01-04', ticker, family, 'c'+family, 'ENTER', .10, .04,
        'net_return_fraction' if family == 'GA7' else 'entry_equity_fraction',
        'manifest', 'snapshot', '2020-01-03')


def evaluate(priority):
    return signals_for_close([proposal('GA6', 'AAA'), proposal('GA7', 'BBB')],
        '2020-01-04', trades_by_chromosome={}, drawdown_by_chromosome={},
        independently_confirmed=set(), held_positions={}, risk_inputs={},
        calibrated_priority=priority)


@pytest.mark.parametrize('priorities', [
    {'cGA6': .03},
    {'cGA6': .03, 'cGA7': float('nan')},
    {'cGA6': .03, 'cGA7': float('inf')},
    {'cGA6': .03, 'cGA7': None},
])
def test_incomplete_or_nonfinite_calibration_fails_closed(priorities):
    with pytest.raises(ValueError, match='calibrated priority'):
        evaluate(priorities)


def test_complete_calibrated_priorities_are_preserved():
    signals = evaluate({'cGA6': .03, 'cGA7': .02})
    assert [(s.ticker, s.score) for s in signals] == [('AAA', .03), ('BBB', .02)]

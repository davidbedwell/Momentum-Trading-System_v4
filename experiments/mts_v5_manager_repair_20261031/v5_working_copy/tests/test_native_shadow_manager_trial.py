from datetime import date, timedelta
from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar


def test_competing_native_shadow_outcomes_mature_after_exits():
    dates = [(date(2026, 1, 2) + timedelta(days=i)).isoformat() for i in range(7)]
    candidates = [Candidate('specialist', 'GA6', 'A', .02), Candidate('generic', 'GA7', None, .02)]
    def classify(ticker, day):
        return NicheObservation(day, '2026-01-01', 'fixture', (('A', .1),))
    def native(c, ticker, day, held):
        action = 'EXIT' if held and day >= dates[3] else 'HOLD' if held else 'ENTER'
        return NativeProposal(day, ticker, c.family, c.chromosome_id, action,
            0 if action == 'EXIT' else .1, .01,
            'entry_equity_fraction' if c.family == 'GA6' else 'net_return_fraction',
            'fixture', 'fixture', '2026-01-01')
    result = run_slice([(day, {'AAA': Bar(100+i, 100+i)}) for i, day in enumerate(dates)],
        candidates, classify=classify, eligible=lambda *args: True, native=native,
        conditional_ev=lambda c, *args: .02 if c.niche else .20, native_shadow=True)
    outcomes = result['native_shadow_outcomes']
    assert {o.chromosome_id for o in outcomes} == {'specialist', 'generic'}
    assert all(o.maturity_session > o.decision_session for o in outcomes)
    assert all(o.source == 'shadow' for o in outcomes)
    assert result['native_shadow_open'] == {}
    assert result['owners'] == {}
    assert result['native_shadow_calibrator'].estimate('generic', ('GA7_ENTRY',), 7) is None

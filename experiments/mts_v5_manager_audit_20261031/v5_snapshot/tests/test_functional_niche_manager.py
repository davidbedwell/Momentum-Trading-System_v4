"""Explicit synthetic fixtures; no claim these are archived models or observations."""
from types import SimpleNamespace
import unittest
from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.ga7_native_daily_producer import produce
from engines.portfolio_replay.kernel import Bar


def observation(ticker, date):
    return NicheObservation(date, '2025-12-31', 'synthetic-test-fixture',
                            (('far', .9), ('near', .1)))


def scenario(prefix=None, cash=100000.):
    dates = [f'2026-01-{day:02d}' for day in range(1, 7)]
    closes = [100, 100, 104, 104, 97, 98]
    days = [(date, {'AAA': Bar(close, close)}) for date, close in zip(dates, closes)]
    candidates = [Candidate(cid, 'GA7', niche, .02) for cid, niche in
                  [('a', 'near'), ('b', 'near'), ('wrong', 'far'), ('blocked', 'near')]]
    genome = SimpleNamespace(operator='AND', entry_pct=.04, feature_a='a', feature_b='b',
                             threshold_a=0., threshold_b=0., stop_pct=.02, exit_rule='reversal')
    def native(c, ticker, date, held):
        i = dates.index(date)
        strength = .4 if i == 3 else .8
        values = produce(genome, {ticker: dict(close=closes[i], eligible=True,
                         controlling_niche='near', features=dict(a=strength, b=strength))},
                         decision_date=date, trained_through='2025-12-31',
                         source_hash='synthetic-genome-fixture', snapshot_hash='synthetic-close-fixture',
                         chromosome_id=c.chromosome_id, held={ticker: held} if held else {},
                         niche_group='near')
        return values[0] if values else None
    return run_slice(days[:prefix], candidates, classify=observation,
                     eligible=lambda c, t, d: c.chromosome_id != 'blocked', native=native, cash=cash)



class FunctionalSliceTests(unittest.TestCase):

    def test_native_competition_and_complete_incumbent_lifecycle(self):
        result = scenario()
        decisions = result['decisions']
        assert decisions[0]['controlling_niche'] == 'near'
        assert decisions[0]['eligible'] == [('GA7', 'a'), ('GA7', 'b')]
        owner = decisions[0]['selected'][:2]
        assert [d['selected'][2] for d in decisions[:5]] == ['ENTER', 'HOLD', 'ADD', 'REDUCE', 'EXIT']
        assert all(d['eligible'] == [owner] for d in decisions[1:5])
        ledger = result['ledger']
        assert [f[2] for f in ledger] == ['BUY', 'BUY', 'SELL', 'SELL']
        assert [f[0] for f in ledger] == ['2026-01-02', '2026-01-04', '2026-01-05', '2026-01-06']
        assert ledger[0][4] == 100 and ledger[1][4] == 104
        assert result['owners'] == {}
        assert abs(result['nav'][-1][1] - 100000. - sum(r['pnl'] for r in result['realized'])) < 1e-7
        assert all(n[2] >= 0 for n in result['nav'])
        assert result['launch_ready'] is False


    def test_prefix_causality_and_real_funding(self):
        short, full = scenario(3, cash=1000.), scenario(cash=1000.)
        assert short['ledger'] == full['ledger'][:len(short['ledger'])]
        assert short['decisions'] == full['decisions'][:3]
        assert short['nav'] == full['nav'][:3]
        assert abs(short['ledger'][0][3] - .4) < 1e-10
        assert short['ledger'][0][5] > 0


    def test_overlap_ties_and_explicit_non_niche(self):
        assert NicheObservation('2026-01-01', '2025-12-31', 'fixture',
                                (('b', .1), ('a', .1))).controlling('2026-01-01') == 'a'
        assert NicheObservation('2026-01-01', '2025-12-31', 'fixture', ()).controlling('2026-01-01') is None
        for obs in [NicheObservation('2026-01-02', '2025-12-31', 'fixture', ()),
                    NicheObservation('2026-01-01', '2026-01-01', 'fixture', ()),
                    NicheObservation('2026-01-01', '2025-12-31', 'fixture', (('a', float('nan')),))]:
            with unittest.TestCase().assertRaises(ValueError):
                obs.controlling('2026-01-01')


    def test_ga4_never_blocks_or_trades(self):
        with unittest.TestCase().assertRaisesRegex(ValueError, 'GA4 is research-only'):
            run_slice([], [Candidate('research', 'GA4', None, .02)],
                      classify=observation, eligible=None, native=None)


    def test_shared_bank_reserves_cash_across_stocks(self):
        from discovery.competitive_ga.native_signal_contract import NativeProposal
        candidates = [Candidate('owner', 'GA7', 'near', .02)]
        bars = {f'S{i:02d}': Bar(100, 100) for i in range(16)}
        def native(c, ticker, date, held):
            return NativeProposal(date, ticker, 'GA7', c.chromosome_id,
                                  'HOLD' if held else 'ENTER',
                                  held['weight'] if held else .1, 0.,
                                  'net_return_fraction', 'fixture', 'fixture', '2025-12-31')
        result = run_slice([('2026-01-01', bars), ('2026-01-02', bars)], candidates,
                           classify=observation, eligible=lambda *a: True, native=native,
                           cash=1000.)
        buys = result['ledger']
        assert 9 <= len(buys) <= 10
        assert sum(q * price + fee for _, _, _, q, price, fee in buys) <= 1000. + 1e-8
        assert result['nav'][-1][2] >= 0
        assert len(result['owners']) == len(buys)

    def test_entry_eligibility_loss_does_not_strand_incumbent(self):
        from discovery.competitive_ga.native_signal_contract import NativeProposal
        calls = []
        def native(c, ticker, date, held):
            calls.append((date, bool(held)))
            return NativeProposal(date, ticker, 'GA7', c.chromosome_id,
                                  'EXIT' if held else 'ENTER', 0. if held else .04,
                                  0., 'net_return_fraction', 'fixture', 'fixture', '2025-12-31')
        def classify(ticker, date):
            return NicheObservation(date, '2025-12-31', 'fixture',
                                    (('near', .1),) if date.endswith('01') else ())
        result = run_slice([(f'2026-01-0{i}', {'A': Bar(100, 100)}) for i in (1, 2, 3)],
                           [Candidate('a', 'GA7', 'near', .02)], classify=classify,
                           eligible=lambda c, t, d: d.endswith('01'), native=native)
        assert calls == [('2026-01-01', False), ('2026-01-02', True)]
        assert [f[2] for f in result['ledger']] == ['BUY', 'SELL']
        assert not result['owners']

    def test_reverse_dates_rejected(self):
        with unittest.TestCase().assertRaisesRegex(ValueError, 'chronological'):
            run_slice([('2026-01-02', {'A': Bar(10, 10)}),
                       ('2026-01-01', {'A': Bar(10, 10)})],
                      [Candidate('a', 'GA7', 'other', .02)], classify=observation,
                      eligible=lambda *a: True, native=lambda *a: None)


if __name__ == "__main__":
    unittest.main()

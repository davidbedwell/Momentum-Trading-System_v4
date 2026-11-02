from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar


def test_ga6_ga7_compete_in_same_niche_with_shared_capital():
    dates = ['2026-01-01', '2026-01-02', '2026-01-03']
    candidates = [Candidate('six', 'GA6', 'near', .02), Candidate('seven', 'GA7', 'near', .02), Candidate('other', 'GA6', 'far', .02)]
    seen = []
    def native(c, ticker, date, held):
        seen.append((c.family, c.chromosome_id, date))
        return NativeProposal(date, ticker, c.family, c.chromosome_id,
                              'HOLD' if held else 'ENTER', held['weight'] if held else .10,
                              .01, 'entry_equity_fraction' if c.family == 'GA6' else 'net_return_fraction', 'fixture', 'fixture', '2025-12-31')
    result = run_slice([(d, {'AAA': Bar(100, 100)}) for d in dates], candidates,
        classify=lambda ticker, date: NicheObservation(date, '2025-12-31', 'fixture', (('near', .1),)),
        eligible=lambda *args: True, native=native)
    assert ('GA6', 'six', dates[0]) in seen
    assert ('GA7', 'seven', dates[0]) in seen
    assert not any(c == 'other' for _, c, _ in seen)
    assert result['decisions'][0]['eligible'] == [('GA6', 'six'), ('GA7', 'seven')]
    assert len(result['ledger']) == 1
    assert result['owners']['AAA'] in (('GA6', 'six'), ('GA7', 'seven'))

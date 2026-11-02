from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

def test_paired_defense_diverges_only_after_trigger():
    days=[(f'2026-01-0{i}', {'AAA':Bar(price,price)}) for i,price in enumerate((100,101,80,75,78),1)]
    candidate=[Candidate('six','GA6','near',.02),Candidate('seven','GA7','near',.02)]
    def native(c,t,d,held):
        return NativeProposal(d,t,c.family,c.chromosome_id,'HOLD' if held else 'ENTER',held['weight'] if held else .1,0.,'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction','fixture','fixture','2025-12-31')
    def run(defense):
        return run_slice(days,candidate,classify=lambda t,d:NicheObservation(d,'2025-12-31','fixture',(('near',.1),)),eligible=lambda *a:True,native=native,defense_at_close=defense)
    off=run(lambda d:False)
    on=run(lambda d:d>='2026-01-03')
    assert off['ledger'][:1]==on['ledger'][:1]
    assert on['decisions'][:2]==off['decisions'][:2]
    assert any(d['selected'] and d['selected'][2]=='DEFENSE_EXIT' for d in on['decisions'])
    assert len(on['ledger'])>len(off['ledger'])
    assert on['nav'][-1][1]!=off['nav'][-1][1]

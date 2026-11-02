from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar


def test_niche_specialist_beats_global_ev_and_negative_ev_abstains():
    dates=['2026-01-02','2026-01-03','2026-01-04']
    candidates=[Candidate('specialist','GA6','A',.02),Candidate('global','GA7',None,.02)]
    def native(c,t,d,held):
        return NativeProposal(d,t,c.family,c.chromosome_id,'HOLD' if held else 'ENTER',.1,.01,
                              'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
                              'fixture','fixture','2026-01-01')
    def classify(t,d):return NicheObservation(d,'2026-01-01','fixture',(('A',.1),))
    def run(ev):return run_slice([(d,{'AAA':Bar(100.+i,100.+i)}) for i,d in enumerate(dates)],candidates,
        classify=classify,eligible=lambda *a:True,native=native,conditional_ev=ev,shadow_horizon=1)
    winning=run(lambda c,*a:.02 if c.chromosome_id=='specialist' else .20)
    assert winning['owners']['AAA']==('GA6','specialist')
    matured=[r for r in winning['shadow_markouts'] if r['status']=='MATURED_FIXED_HORIZON']
    assert {r['owner'] for r in matured} == {('GA6','specialist'),('GA7','global')}
    assert any(r['selected'] for r in matured) and any(not r['selected'] for r in matured)
    assert all('net_return_estimate' in r for r in matured)
    abstain=run(lambda *a:-.01)
    assert not abstain['ledger']
    assert not abstain['owners']

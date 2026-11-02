from datetime import date,timedelta
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

def test_rejected_challenger_can_enter_shadow_while_incumbent_funded():
    dates=[(date(2026,1,2)+timedelta(days=i)).isoformat() for i in range(7)]
    def classify(t,d):return NicheObservation(d,'2026-01-01','fixture',(('A',.1),))
    def native(c,t,d,held):
        if c.chromosome_id=='challenger' and d<dates[2]:return None
        action='EXIT' if held and d>=dates[4] else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,
            .01,'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
            'fixture','fixture','2026-01-01')
    result=run_slice([(d,{'AAA':Bar(100+i,100+i)}) for i,d in enumerate(dates)],
        [Candidate('incumbent','GA6','A',.02),Candidate('challenger','GA7',None,.02)],
        classify=classify,eligible=lambda *args:True,native=native,
        conditional_ev=lambda c,*args:.02 if c.family=='GA6' else .20,native_shadow=True)
    outcomes=result['native_shadow_outcomes']
    assert any(o.chromosome_id=='challenger' and o.decision_session>=3 for o in outcomes)
    assert any(o.chromosome_id=='incumbent' for o in outcomes)

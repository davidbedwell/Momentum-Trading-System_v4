from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.capital_competition import Opportunity
from engines.portfolio_replay.kernel import Bar


def test_cross_family_challenger_releases_only_evidence_backed_capital():
    dates=[f'2026-01-{i:02d}' for i in range(2,11)]
    names=[f'S{i}' for i in range(10)]+['NEW']
    days=[(d,{t:Bar(100.,100.) for t in names}) for d in dates]
    candidates=[Candidate('six','GA6','A',.02),Candidate('seven','GA7','B',.02),Candidate('horizon','HORIZONS','B',.02)]
    def classify(t,d):
        return NicheObservation(d,'2026-01-01','fixture',(('B' if t=='NEW' else 'A',.1),))
    def native(c,t,d,held):
        if t=='NEW' and d<'2026-01-05':return None
        return NativeProposal(d,t,c.family,c.chromosome_id,'HOLD' if held else 'ENTER',held['weight'] if held else .1,
                              .01,{'GA6':'entry_equity_fraction','GA7':'net_return_fraction','HORIZONS':'native_horizon_score'}[c.family],
                              'fixture','fixture','2026-01-01')
    def estimate(d,t,owner,funded):
        return Opportunity(owner,t,.01 if funded else .08,0.,.001)
    result=run_slice(days,candidates,classify=classify,eligible=lambda c,t,d:True,
                     native=native,opportunity_at_close=estimate)
    transfers=[d for d in result['decisions'] if d.get('action')=='COMPETITIVE_RELEASE']
    assert transfers, 'funded portfolio should identify a superior challenger'
    assert all(d['released_weight']<=.1 and d['net_advantage']>0 and d['settlement_deferred'] for d in transfers)
    assert any(f[2]=='SELL' for f in result['ledger'])
    assert result['nav'][-1][1]>0

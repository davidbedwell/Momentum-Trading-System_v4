"""Functional funded-vs-unlearned synthetic counterfactual, not certification."""
from datetime import date,timedelta
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.evolved_selection_policy import SelectionGenes
from discovery.competitive_ga.genome_identity import GenomeIdentityRegistry
from engines.portfolio_replay.kernel import Bar

def test_matured_shadow_changes_funded_selection_fill_and_nav():
    start=date(2026,1,2)
    days=[]
    for i in range(64):
        d=(start+timedelta(days=i)).isoformat()
        # Steady appreciation rewards longer-hold native exit; 2-session exits pay repeated fees.
        price=100+1.2*i
        days.append((d,{'AAA':Bar(price,price),'BBB':Bar(price*.8,price*.8),'CCC':Bar(price*1.1,price*1.1)}))
    index={d:i for i,(d,_) in enumerate(days)}
    candidates=[Candidate('short','GA6','A',.02),Candidate('long','GA7',None,.02)]
    genomes={('GA6','short'):{'entry':1,'exit_sessions':2},('GA7','long'):{'entry':1,'exit_sessions':8}}
    registry=GenomeIdentityRegistry()
    for (family,cid),genome in genomes.items():registry.register(family,cid,genome)
    def native(c,t,d,held):
        age=index[d]-held['entry_session'] if held else 0
        action='EXIT' if held and age>=(2 if c.family=='GA6' else 8) else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,
            .01,'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
            'fixture','fixture','2025-12-31')
    def replay(learning):
        return run_slice(days,candidates,
            classify=lambda t,d:NicheObservation(d,'2025-12-31','synthetic',(('A',.2),)),
            eligible=lambda *args:True,native=native,
            conditional_ev=lambda c,*args:.025 if c.family=='GA6' else .015,
            selection_genes=SelectionGenes(0,1,0,0),native_shadow=learning,
            native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    learned=replay(True)
    baseline=replay(False)
    first_diff=next((i for i,(a,b) in enumerate(zip(learned['decisions'],baseline['decisions']))
        if a['selected']!=b['selected']),None)
    assert first_diff is not None,'native shadow learning never changed funded selection'
    assert learned['learning_snapshots'][first_diff]['matured_count']>=5
    assert learned['decisions'][first_diff]['selected'][:2]==('GA7','long')
    assert baseline['decisions'][first_diff]['selected'][:2]==('GA6','short')
    assert learned['ledger']!=baseline['ledger'],'funded executions unchanged'
    assert learned['nav'][-1][1]!=baseline['nav'][-1][1],'portfolio NAV unchanged'

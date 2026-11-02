"""Continuous funded learning across a reversal; no reset or refit."""
from datetime import date,timedelta
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.evolved_selection_policy import SelectionGenes
from discovery.competitive_ga.genome_identity import GenomeIdentityRegistry
from engines.portfolio_replay.kernel import Bar

def test_continuous_funded_replay_survives_reversal_and_keeps_learning():
    start=date(2026,1,2)
    days=[]
    for i in range(64):
        d=(start+timedelta(days=i)).isoformat()
        p=100+1.2*i if i<32 else 138.4-1.4*(i-32)
        days.append((d,{t:Bar(p*k,p*k) for t,k in [('AAA',1),('BBB',.8),('CCC',1.1)]}))
    index={d:i for i,(d,_) in enumerate(days)}
    candidates=[Candidate('short','GA6','A',.02),Candidate('long','GA7',None,.02)]
    genomes={('GA6','short'):{'hold':2},('GA7','long'):{'hold':8}}
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
            eligible=lambda *a:True,native=native,
            conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .015,
            selection_genes=SelectionGenes(0,1,0,0),native_shadow=learning,
            native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    learned=replay(True)
    baseline=replay(False)
    snaps=learned['learning_snapshots']
    assert snaps[31]['matured_count']>0
    assert snaps[32]['matured_count']>=snaps[31]['matured_count']
    assert snaps[63]['matured_count']>snaps[32]['matured_count']
    assert len(learned['nav'])==64
    assert learned['ledger']!=baseline['ledger']
    assert learned['nav'][-1][1]!=baseline['nav'][-1][1]
    # Pre-reversal prefix is unaffected by any later reversal bars.
    short=run_slice(days[:32],candidates,
        classify=lambda t,d:NicheObservation(d,'2025-12-31','synthetic',(('A',.2),)),
        eligible=lambda *a:True,native=native,
        conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .015,
        selection_genes=SelectionGenes(0,1,0,0),native_shadow=True,
        native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    assert short['nav']==learned['nav'][:32]
    assert short['decisions']==learned['decisions'][:32*3]

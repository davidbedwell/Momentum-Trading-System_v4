"""Measure actual funded selection response to a synthetic trend reversal."""
import json
from datetime import date,timedelta
from .functional_niche_manager import Candidate,NicheObservation,run_slice
from .native_signal_contract import NativeProposal
from .evolved_selection_policy import SelectionGenes
from .genome_identity import GenomeIdentityRegistry
from .causal_market_state import state_from_closes
from engines.portfolio_replay.kernel import Bar

def run():
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
    def replay(learning, min_momentum=None):
        return run_slice(days,candidates,
            classify=lambda t,d:NicheObservation(d,'2025-12-31','synthetic',(('A',.2),)),
            eligible=lambda *a:True,native=native,
            conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .015,
            selection_genes=SelectionGenes(0,1,0,0,min_market_momentum=min_momentum),native_shadow=learning,
            native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    learned,baseline,gated=replay(True),replay(False),replay(True,0.)
    def picks(result,begin,end):
        rows=[d for d in result['decisions'] if begin<=index[d['date']]<end]
        selected=[d['selected'] for d in rows if d.get('selected')]
        return {'GA6':sum(p[0]=='GA6' and p[2]=='ENTER' for p in selected),
                'GA7':sum(p[0]=='GA7' and p[2]=='ENTER' for p in selected),
                'NO_ENTRY':sum(d.get('selected') is None for d in rows)}
    def metrics(result):
        nav=[n[1] for n in result['nav']]
        peak=nav[0];dd=0
        for v in nav:peak=max(peak,v);dd=max(dd,1-v/peak)
        return {'ending_nav':nav[-1],'full_return':nav[-1]/nav[0]-1,
                'post_boundary_return':nav[-1]/nav[31]-1,'max_drawdown':dd,
                'entries_before':picks(result,0,32),'entries_after':picks(result,32,64),
                'fills':len(result['ledger'])}
    negative=next((i for i in range(32,64) if state_from_closes([d[1]['AAA'].close for d in days[:i+1]],i).momentum<0),None)
    divergence=next((index[a['date']] for a,b in zip(learned['decisions'],baseline['decisions']) if a.get('selected')!=b.get('selected')),None)
    return {'scope':'SYNTHETIC_DIAGNOSTIC_NOT_VALIDATION','boundary_session':32,
        'first_negative_5_session_momentum':negative,'momentum_detection_lag':negative-32 if negative is not None else None,
        'first_funded_learning_divergence':divergence,
        'matured_at_boundary':learned['learning_snapshots'][32]['matured_count'],
        'learned':metrics(learned),'baseline':metrics(baseline),
        'state_gated':metrics(gated)}
if __name__=='__main__':print(json.dumps(run(),indent=2))

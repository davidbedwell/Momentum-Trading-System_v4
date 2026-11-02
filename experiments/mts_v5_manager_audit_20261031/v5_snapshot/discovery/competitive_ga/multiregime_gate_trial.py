"""Bounded synthetic scenario test of causal momentum abstention."""
import json
from datetime import date,timedelta
from .functional_niche_manager import Candidate,NicheObservation,run_slice
from .native_signal_contract import NativeProposal
from .evolved_selection_policy import SelectionGenes
from .genome_identity import GenomeIdentityRegistry
from engines.portfolio_replay.kernel import Bar

SCENARIOS={
 'up_down_recovery':[(24,1.2),(20,-1.4),(20,1.5)],
 'steady_up':[(64,.8)],
 'steady_down':[(64,-.65)],
 'choppy':[(16,.7),(16,-.6),(16,.7),(16,-.6)],
 'delayed_reversal':[(40,.9),(24,-1.3)],
 'down_recovery':[(28,-.8),(36,1.2)],
}

def trial(scenario,threshold):
    prices=[];p=100.
    for n,step in SCENARIOS[scenario]:
        for _ in range(n):prices.append(p);p+=step
    start=date(2026,1,2)
    days=[((start+timedelta(days=i)).isoformat(),{t:Bar(p*k,p*k) for t,k in [('AAA',1),('BBB',.8),('CCC',1.1)]}) for i,p in enumerate(prices)]
    idx={d:i for i,(d,_) in enumerate(days)}
    candidates=[Candidate('short','GA6','A',.02),Candidate('long','GA7',None,.02)]
    genomes={('GA6','short'):{'hold':2},('GA7','long'):{'hold':8}}
    reg=GenomeIdentityRegistry()
    for (f,c),g in genomes.items():reg.register(f,c,g)
    def native(c,t,d,held):
        age=idx[d]-held['entry_session'] if held else 0
        action='EXIT' if held and age>=(2 if c.family=='GA6' else 8) else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,.01,
            'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
            'fixture','fixture','2025-12-31')
    r=run_slice(days,candidates,classify=lambda t,d:NicheObservation(d,'2025-12-31','synthetic',(('A',.2),)),
        eligible=lambda *a:True,native=native,
        conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .015,
        selection_genes=SelectionGenes(0,1,0,0,min_market_momentum=threshold),native_shadow=True,
        native_genomes=genomes,genome_registry=reg,require_genome_identity=True)
    nav=[x[1] for x in r['nav']];peak=nav[0];dd=0
    for v in nav:peak=max(peak,v);dd=max(dd,1-v/peak)
    selected=[d['selected'] for d in r['decisions']]
    return {'return':round(nav[-1]/nav[0]-1,5),'mdd':round(dd,5),
            'no_entry':sum(s is None for s in selected),
            'ga6_entries':sum(s is not None and s[0]=='GA6' and s[2]=='ENTER' for s in selected),
            'ga7_entries':sum(s is not None and s[0]=='GA7' and s[2]=='ENTER' for s in selected)}

def run():
    thresholds=[None,-.03,-.01,0.,.01,.03]
    return {'scope':'SYNTHETIC_FUNCTIONALITY_NOT_OOS','thresholds':thresholds,
        'scenarios':{name:{str(t):trial(name,t) for t in thresholds} for name in SCENARIOS}}
if __name__=='__main__':print(json.dumps(run(),indent=2))

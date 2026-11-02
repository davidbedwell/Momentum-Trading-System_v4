"""One funded 192-session synthetic replay, frozen threshold and uninterrupted learning."""
import json
from datetime import date,timedelta
from .functional_niche_manager import Candidate,NicheObservation,run_slice
from .native_signal_contract import NativeProposal
from .evolved_selection_policy import SelectionGenes
from .genome_identity import GenomeIdentityRegistry
from .frozen_threshold_holdout import run as discover
from .multiregime_gate_trial import SCENARIOS
from engines.portfolio_replay.kernel import Bar

PHASES=('choppy','delayed_reversal','down_recovery')
def replay(threshold,days=None):
    prices=[];p=100.;boundaries=[]
    for phase in PHASES:
        for count,step in SCENARIOS[phase]:
            for _ in range(count):prices.append(p);p+=step
        boundaries.append(len(prices))
    if days is not None:prices=prices[:days]
    start=date(2026,1,2)
    bars=[((start+timedelta(days=i)).isoformat(),{t:Bar(p*k,p*k) for t,k in [('AAA',1),('BBB',.8),('CCC',1.1)]}) for i,p in enumerate(prices)]
    idx={d:i for i,(d,_) in enumerate(bars)}
    candidates=[Candidate('short','GA6','A',.02),Candidate('long','GA7',None,.02)]
    genomes={('GA6','short'):{'hold':2},('GA7','long'):{'hold':8}}
    registry=GenomeIdentityRegistry()
    for (family,cid),genome in genomes.items():registry.register(family,cid,genome)
    def native(c,t,d,held):
        age=idx[d]-held['entry_session'] if held else 0
        action='EXIT' if held and age>=(2 if c.family=='GA6' else 8) else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,.01,
            'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
            'fixture','fixture','2025-12-31')
    r=run_slice(bars,candidates,max_sessions=192,
        classify=lambda t,d:NicheObservation(d,'2025-12-31','synthetic',(('A',.2),)),
        eligible=lambda *a:True,native=native,
        conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .015,
        selection_genes=SelectionGenes(0,1,0,0,min_market_momentum=threshold),native_shadow=True,
        native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    return r,boundaries

def stats(r,boundaries):
    nav=[x[1] for x in r['nav']];peak=nav[0];mdd=0
    for v in nav:peak=max(peak,v);mdd=max(mdd,1-v/peak)
    phase=[];start=0
    for end in boundaries:
        if end>len(nav):break
        selected=[d['selected'] for d in r['decisions'][start*3:end*3]]
        phase.append({'name':PHASES[len(phase)],'start_nav':round(nav[start-1] if start else 100000,2),
            'end_nav':round(nav[end-1],2),'no_entry':sum(s is None for s in selected),
            'entries':sum(s is not None and s[2]=='ENTER' for s in selected),
            'matured_end':r['learning_snapshots'][end-1]['matured_count']})
        start=end
    return {'end_nav':round(nav[-1],2),'return':round(nav[-1]/100000-1,5),
        'mdd':round(mdd,5),'phases':phase}

def run():
    threshold=discover()['frozen_threshold']
    frozen,boundaries=replay(threshold)
    baseline,_=replay(None)
    prefix,_=replay(threshold,64)
    return {'scope':'CONTINUOUS_SYNTHETIC_NOT_MARKET_OOS','threshold':threshold,
        'sessions':len(frozen['nav']),'boundaries':boundaries,
        'prefix_nav_identical':prefix['nav']==frozen['nav'][:64],
        'prefix_decisions_identical':prefix['decisions']==frozen['decisions'][:64*3],
        'frozen':stats(frozen,boundaries),'baseline':stats(baseline,boundaries)}
if __name__=='__main__':print(json.dumps(run(),indent=2))

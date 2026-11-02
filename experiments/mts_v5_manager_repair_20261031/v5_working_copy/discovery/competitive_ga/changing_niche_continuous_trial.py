"""Functional trial: changing PIT controlling niches, multiple native chromosomes, one bank."""
import json
from datetime import date,timedelta
from collections import Counter
from .functional_niche_manager import Candidate,NicheObservation,run_slice
from .native_signal_contract import NativeProposal
from .evolved_selection_policy import SelectionGenes
from .genome_identity import GenomeIdentityRegistry
from .causal_niche_classifier import classify_closes
from engines.portfolio_replay.kernel import Bar

N=192
TICKERS=('AAA','BBB','CCC')
def replay(days=N):
    start=date(2026,1,2)
    bars=[]
    for i in range(days):
        rows={}
        for j,t in enumerate(TICKERS):
            # Phases vary independently by ticker, not one common price path.
            p=100.+j*10
            for k in range(i):
                phase=((k+j*17)//24)%4
                p+= (1.0,-.8,.65,-.45)[phase]
            rows[t]=Bar(p,p)
        bars.append(((start+timedelta(days=i)).isoformat(),rows))
    idx={d:i for i,(d,_) in enumerate(bars)}
    candidates=[Candidate('a_fast','GA6','A',.02),Candidate('a_slow','GA7','A',.02),
        Candidate('b_fast','GA6','B',.02),Candidate('b_slow','GA7','B',.02),
        Candidate('general','HORIZONS',None,.02)]
    genomes={(c.family,c.chromosome_id):{'hold':2 if 'fast' in c.chromosome_id else 7 if 'slow' in c.chromosome_id else 4,'niche':c.niche} for c in candidates}
    registry=GenomeIdentityRegistry()
    for (f,c),g in genomes.items():registry.register(f,c,g)
    histories={t:[] for t in TICKERS}
    for _,row in bars:
        for t in TICKERS:histories[t].append(row[t].close)
    def classify(t,d):
        i=idx[d]
        return classify_closes(histories[t][:i+1],i,d)
    def native(c,t,d,held):
        age=idx[d]-held['entry_session'] if held else 0
        horizon=genomes[(c.family,c.chromosome_id)]['hold']
        action='EXIT' if held and age>=horizon else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,.01,
            'entry_equity_fraction' if c.family=='GA6' else 'native_horizon_score' if c.family=='HORIZONS' else 'net_return_fraction',
            'fixture','fixture','2025-12-31')
    result=run_slice(bars,candidates,max_sessions=N,classify=classify,eligible=lambda *a:True,
        native=native,conditional_ev=lambda c,*a:.02 if c.niche else .012,
        selection_genes=SelectionGenes(.02,1,0,0,min_market_momentum=-.03),native_shadow=True,
        native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    return result

def run():
    full=replay();prefix=replay(64)
    counts=Counter((d['controlling_niche'],d['selected'][0],d['selected'][1]) for d in full['decisions'] if d['selected'] and d['selected'][2]=='ENTER')
    changes=sum(a['controlling_niche']!=b['controlling_niche'] for a,b in zip(full['decisions'][:-3],full['decisions'][3:]) if a['ticker']==b['ticker'])
    nav=[row[1] for row in full['nav']];peak=nav[0];mdd=0.
    for v in nav:peak=max(peak,v);mdd=max(mdd,1-v/peak)
    return {'scope':'SYNTHETIC_FUNCTIONALITY_ONLY','sessions':len(nav),
        'niche_changes':changes,'funded_entries_by_niche_owner':{str(k):v for k,v in counts.items()},
        'native_shadow_outcomes':len(full['native_shadow_outcomes']),
        'prefix_nav_identical':prefix['nav']==full['nav'][:64],
        'prefix_decisions_identical':prefix['decisions']==full['decisions'][:64*3],
        'ending_nav':round(nav[-1],2),'max_drawdown':round(mdd,5)}
if __name__=='__main__':print(json.dumps(run(),indent=2))

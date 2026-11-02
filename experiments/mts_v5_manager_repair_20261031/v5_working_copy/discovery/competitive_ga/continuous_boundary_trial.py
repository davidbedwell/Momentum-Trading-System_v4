"""Bounded continuous synthetic replay across a regime boundary (no resets)."""
import json
from datetime import date,timedelta
from .functional_niche_manager import Candidate,NicheObservation,run_slice
from .native_signal_contract import NativeProposal
from .evolved_selection_policy import SelectionGenes
from engines.portfolio_replay.kernel import Bar

def run():
    start=date(2026,1,2)
    days=[]
    for i in range(64):
        d=(start+timedelta(days=i)).isoformat()
        if i<32:
            prices={'AAA':100+1.1*i,'BBB':100+.5*i,'CCC':100+.2*i}
        else:
            j=i-32
            prices={'AAA':135.2-1.3*j,'BBB':116+1.0*j,'CCC':106.4-.3*j}
        days.append((d,{t:Bar(p,p) for t,p in prices.items()}))
    index={d:i for i,(d,_) in enumerate(days)}
    candidates=[Candidate('specialist','GA6','A',.02),Candidate('transfer','GA7',None,.02)]
    def classify(t,d):return NicheObservation(d,'2025-12-31','synthetic',(('A',.2),))
    def native(c,t,d,held):
        age=index[d]-held['entry_session'] if held else 0
        action='EXIT' if held and age>=(2 if c.family=='GA6' else 5) else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,
            .01,'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
            'fixture','fixture','2025-12-31')
    outputs={}
    for name,genes in [('fit',SelectionGenes(.15,1,0,0)),('ev',SelectionGenes(0,1,0,0)),
        ('state',SelectionGenes(.1442564771,2.2657485345,0,0,1.1027178676,-2.6392058227))]:
        result=run_slice(days,candidates,classify=classify,eligible=lambda *a:True,native=native,
            conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .07,
            selection_genes=genes,native_shadow=True,max_sessions=64)
        nav=[x[1] for x in result['nav']]
        peak=nav[0];dd=0.
        for v in nav:
            peak=max(peak,v);dd=max(dd,1-v/peak)
        snaps=result['learning_snapshots']
        outputs[name]={'return':nav[-1]/nav[0]-1,'mdd':dd,
            'nav_before_boundary':nav[31],'nav_after_boundary':nav[32],
            'ending_nav':nav[-1], 'fills':len(result['ledger']),
            'matured_before_boundary':snaps[31]['matured_count'],
            'matured_after_boundary':snaps[32]['matured_count'],
            'final_matured':snaps[-1]['matured_count']}
    return {'scope':'SYNTHETIC_CONTINUOUS_64_SESSIONS_NO_REOPTIMIZATION',
        'boundary_session':32,'results':outputs}

if __name__=='__main__':print(json.dumps(run(),indent=2))

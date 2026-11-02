"""Synthetic GA6/v4 allocation behavior; no data or live services."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'reference_snapshot'))
from ga6.shared_selector_allocation_20261025 import allocate
from ga6.shared_selector_engine_contract_20261025 import CandidateDecision
from ga6.shared_selector_competition_20261025 import self_test
c=lambda ticker,weight,score,action='ENTER':CandidateDecision('2020-01-03',ticker,'owner','NICHE-0001',action,weight,score,'on','2020-01-02')
r=allocate([c('A',0,1),c('B',.1,2),c('C',.1,3,'SCALE_IN')],{},100000,100000)
assert ('A','owner',.03) in r and not any(x[0]=='C' for x in r)
n=allocate([c('N',.1,float('nan'))],{},100000,100000)
assert n
results={'zero_target_entry':r,'nan_score_accepted':n,'competition_self_test':self_test(),'scope':'GA6 standalone allocation only'}
# Older v4 modular risk sizing and allocator: direct synthetic inputs.
sys.path.append('/opt/mts')
from mts_horizon_competitive_allocator_v2 import allocate as horizon, Opportunity
from mts_risk_sizing_v1 import size_long
s=size_long(100000,100,[-.1]*40,100000,0)
assert s['estimated_loss']<=s['budget']
results['v4_tail_risk_sizer']=s
(HERE/'legacy_smoke_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))

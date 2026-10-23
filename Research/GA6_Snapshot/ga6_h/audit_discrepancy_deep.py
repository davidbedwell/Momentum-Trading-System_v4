import json
from pathlib import Path
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
r=Path('/opt/mts')
cp=json.loads((r/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text())
allc=[StructuralCandidate.restore(x) for x in cp['members']]
p=pd.read_csv(r/'ga6_h/audits/ga6v3_DEV87_vs_development_20261023.csv')
same=pd.read_csv(r/'ga6_h/audits/ga6v3_400_DEV87_same_period_2019_2024.csv')
later=pd.read_csv(r/'ga6_h/audits/ga6v3_400_DEV87_20261023.csv')
x=p.merge(same,on='identity',suffixes=('_old','_same')).merge(later,on='identity',suffixes=('_same','_later'))
x['universe_delta']=x.cagr_same-x.dev_cagr
x['period_delta']=x.cagr_later-x.cagr_same
x['dev_to_later']=x.cagr_later-x.dev_cagr
print('ATTRIBUTION means',x[['dev_cagr','cagr_same','cagr_later','universe_delta','period_delta','dev_to_later']].mean().round(5).to_dict())
print('NICHE',x.groupby('niche_same')[['dev_cagr','cagr_same','cagr_later','universe_delta','period_delta']].mean().round(4).to_string())
print('TRADE',x[['dev_trades','trades_same','trades_later']].mean().round(2).to_dict())
print('ZERO TRADES',int(sum(x.trades_same==0)),int(sum(x.trades_later==0)))
print('MDD',x[['dev_mdd','mdd_same','mdd_later']].mean().round(4).to_dict())
print('CORRELATION',x[['dev_cagr','cagr_same','cagr_later']].corr().round(3).to_string())
print('PERIOD YEARS',1510/252,425/252)
print('NOTE: comparison is sequential descriptive decomposition, not causal factorial decomposition')
out=r/'ga6_h/audits/ga6v3_matched130_three_way_20261023.csv'
x.to_csv(out,index=False)
print('OUTPUT',out)

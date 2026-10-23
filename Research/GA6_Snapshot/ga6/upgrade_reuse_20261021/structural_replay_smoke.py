import json,pandas as pd
from pathlib import Path
from ga5_redesign.niche_seeds import initial
from ga6.upgrade_reuse_20261021.structural_portfolio_evaluator import evaluate
from ga6.upgrade_reuse_20261021.structural_candidate import StructuralCandidate
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
root=Path('/opt/mts')
d=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
d=d[(d.date>='2025-01-01')&(d.date<'2025-04-01')].copy()
p=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
dates=set(d.date.astype(str).str[:10]);tickers=set(d.ticker)
member={(day,t):v for day,t,v in p['membership'] if day in dates and t in tickers}
veto={day:v for day,v in p['risk_veto'].items() if day in dates}
blocked={t:frozenset(x for x in v if x in dates) for t,v in p['blocked'].items() if t in tickers}
g=initial('NICHE-0001');prepared=PreparedSessions(d)
kwargs=dict(blocked=blocked,membership=member,risk_veto=veto,annual_cash_yield=p['cash_proxy_annual_yield'])
leaf=lambda f,threshold:{'family':f,'threshold':threshold,'comparison':'>='}
trees={'legacy':None,'AND':{'op':'AND','children':[leaf('trend',0.9),leaf('momentum',-1.)]},'OR':{'op':'OR','children':[leaf('trend',0.9),leaf('momentum',-1.)]}}
results={}
for name,tree in trees.items():
 r=evaluate(prepared,g,entry_tree=tree,**kwargs) if tree is None else StructuralCandidate.restore(StructuralCandidate(g,tree).checkpoint()).replay(prepared,**kwargs)
 results[name]={k:r[k] for k in ('sessions','fills','final_nav','mdd_diagnostic')}
 results[name]['buys']=r['signal_trace']['executed_buys']
print(json.dumps(results,indent=2,default=str))

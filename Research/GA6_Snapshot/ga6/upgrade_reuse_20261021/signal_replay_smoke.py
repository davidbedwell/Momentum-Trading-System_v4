"""Read-only chronological feature-expression smoke test, not portfolio backtest."""
import json,pathlib,pandas as pd
from ga6.upgrade_reuse_20261021.family_logic import evaluate,validate
P=pathlib.Path('ga5_redesign/exploratory79_ga4_enriched.parquet')
F=('trend','momentum','volatility','volume','recursive','sector','breadth','relative_strength')
df=pd.read_parquet(P,columns=['date','ticker',*F]);df=df[df['ticker']==sorted(df['ticker'].unique())[0]].sort_values('date').head(200)
expressions=[{'op':'AND','children':[{'family':'trend','threshold':0,'comparison':'>='},{'family':'momentum','threshold':0,'comparison':'>='}]},{'op':'AND','children':[{'op':'OR','children':[{'family':'trend','threshold':0,'comparison':'>='},{'family':'momentum','threshold':0,'comparison':'>='}]},{'family':'volatility','threshold':.2,'comparison':'<='}]}]
rows=[]
for exp in expressions:
 validate(exp);results=[evaluate(exp,{k:getattr(row,k) for k in F}) for row in df.itertuples(index=False)];rows.append({'families':len(validate(exp)),'sessions':len(results),'true':sum(x is True for x in results),'false':sum(x is False for x in results),'missing':sum(x is None for x in results)})
assert all(r['sessions']==r['true']+r['false']+r['missing'] for r in rows)
out={'status':'SIGNAL_ONLY_SMOKE_NOT_PORTFOLIO_EVALUATION','source':str(P),'rows':rows};pathlib.Path('ga6/upgrade_reuse_20261021/signal_replay_smoke.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

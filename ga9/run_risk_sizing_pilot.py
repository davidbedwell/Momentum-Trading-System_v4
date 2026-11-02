"""Isolated GA9 risk-sizing ablation, never production deployment."""
import json,sys
from pathlib import Path
from dataclasses import replace
from . import exploratory
from .execution import Gene,Manager,replay
p,provenance,refs=exploratory.inputs('real')
source=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
result=[]
for fold in source['folds']:
 a=int(p.dates.searchsorted(fold['start']));b=int(p.dates.searchsorted(fold['end_exclusive']))
 signal,_=exploratory.model_signal(p,source['family'],a,source['horizon'])
 for risk,weight in ((.004,.06),(.02,.10),(.02,.06)):
  m=exploratory.edge_manager(Manager(**source['manager']))
  m=replace(m,risk_cap=risk,reserve=0.1,slots=10,size_scale=1.)
  z=replay(p,[Gene(source['family'],threshold=0,hold_sessions=source['horizon'],weight=weight)],m,p.dates[a],p.dates[b-1]+__import__('pandas').Timedelta(days=1),detail=False,signal=signal,hold_signal=signal,edge_mode=True,absolute_edges=True)
  result.append(dict(fold=fold['start'],risk_cap=risk,weight=weight,metrics=z['metrics'],audit=z['audit']))
(out/'results.json').write_text(json.dumps(dict(label='DEVELOPMENT_ONLY_RISK_SIZING_ABLATION',source=sys.argv[1],results=result),indent=2))
for x in result:print(x['fold'],x['risk_cap'],x['weight'],'cagr',round(x['metrics']['cagr']*100,3),'mdd',round(x['metrics']['max_drawdown']*100,3),'exposure',round(x['metrics']['exposure']*100,2),'fills',x['metrics']['fills'])

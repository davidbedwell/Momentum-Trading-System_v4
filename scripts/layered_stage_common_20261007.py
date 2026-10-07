from pathlib import Path
import pandas as pd,numpy as np,json,math
ROOT=Path('/home/ubuntu/mts-ga-dev117-permitted-20261006'); RUN=Path('Research/Runs/layered')
H=[5,10,20,63]
def load_bank(): return json.load(open(RUN/'stage2-opportunity-20261007/opportunity_bank.json'))['bank']
def frame(t):
 d=pd.read_parquet(ROOT/f'{t}.parquet',columns=['date','adj_close','high','low','volume']).sort_values('date');p=d.adj_close.astype(float);r=p.pct_change()
 d['ret1']=r;d['ret20']=p.pct_change(20);d['ret63']=p.pct_change(63);d['range20']=p/p.rolling(20).max()-1;d['range50']=p/p.rolling(50).max()-1;d['gap20']=p/p.rolling(20).mean()-1;d['gap50']=p/p.rolling(50).mean()-1
 d['z20']=(p-p.rolling(20).mean())/p.rolling(20).std();delta=p.diff();up=delta.clip(lower=0).rolling(14).mean();dn=(-delta.clip(upper=0)).rolling(14).mean();d['rsi14']=100-100/(1+up/dn)
 d['rv20']=r.rolling(20).std()*np.sqrt(252);d['rv63']=r.rolling(63).std()*np.sqrt(252);d['relvol20']=d.volume/d.volume.rolling(20).mean();d['volslope20']=d.volume.rolling(5).mean()/d.volume.rolling(20).mean()-1
 for h in H:d[f'f{h}']=p.shift(-h)/p-1
 return d
def mask(d,c):
 q=d[c['feature']].quantile(.8 if c['tail']=='HIGH' else .2);return d[c['feature']].ge(q) if c['tail']=='HIGH' else d[c['feature']].le(q)
def signed(x,c): return x if c['direction']=='LONG' else -x
def write(stage,name,report,decision='PASS',reason=''):
 o=RUN/f'stage{stage}-{name}-20261007';o.mkdir(parents=True,exist_ok=True);(o/'report.json').write_text(json.dumps(report,indent=2,default=str));g={'decision':decision,'gate_version':f'stage{stage}-v1','reason':reason,'scientific_parameters_changed':False};(o/'gate.json').write_text(json.dumps(g,indent=2));print(json.dumps(g))

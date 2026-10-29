#!/usr/bin/env python3
import importlib.util, json, random, hashlib
from pathlib import Path
import numpy as np
P=Path('/home/ubuntu/Momentum-Trading-System_v4/scripts/run_horizon_free_ga_frozen_architecture_v2_20261005.py')
spec=importlib.util.spec_from_file_location('ga',P); ga=importlib.util.module_from_spec(spec); spec.loader.exec_module(ga)
results={}
def ck(name,cond,detail=''):
    results[name]={'pass':bool(cond),'detail':str(detail)}
    if not cond: raise AssertionError(name+': '+str(detail))

# Synthetic group schema: 4 stock, 2 sector, 3 market.
groups={'stock':[0,1,2,3],'sector':[4,5],'market':[6,7,8]}
T,N,F=40,8,9
X=np.full((T,N,F),.5,float); RX=np.zeros((T,N),float); rf=np.full(T,.0001)
g={'modules':[{'family':'momentum','signal_ids':[0],'signal_w':[2.0],
               'gate_ids':[6],'gate_w':[5.0],'gate_bias':-2.5,'module_w':1.0}],
   'opportunity_scale':.01,'risk_appetite_id':6,'risk_appetite_w':5.0,'risk_appetite_bias':-2.5,
   'safe_margin':0.0,'replace_margin':0.0,'short':False,'alloc':'strength'}
# PF-02/03: market-only perturbation must change gross exposure.
Xlo=X.copy(); Xhi=X.copy(); Xlo[:,:,6]=.05; Xhi[:,:,6]=.95
_,Wlo,_=ga.simulate(g,Xlo,RX,rf,5); _,Whi,_=ga.simulate(g,Xhi,RX,rf,5)
lo=float(np.abs(Wlo).sum(1).mean()); hi=float(np.abs(Whi).sum(1).mean())
ck('PF-02_market_layer_influence',abs(hi-lo)>.10,{'low_gross':lo,'high_gross':hi})
ck('PF-03_rank_cancellation_regression',hi>lo,{'low_gross':lo,'high_gross':hi})

# Sector influence: gate on sector input.
gs=json.loads(json.dumps(g)); gs['modules'][0]['gate_ids']=[4]; gs['modules'][0]['gate_w']=[6.0]; gs['modules'][0]['gate_bias']=-3
Xa=X.copy(); Xb=X.copy(); Xa[:,:,4]=.1; Xb[:,:,4]=.9
Ea,_,_=ga.opportunity(gs,Xa); Eb,_,_=ga.opportunity(gs,Xb)
ck('PF-04_sector_layer_influence',float(np.mean(Eb-Ea))>.001,float(np.mean(Eb-Ea)))

# All four frozen allocation modes reachable and finite.
for mode in ga.ALLOCS:
    gm=json.loads(json.dumps(g)); gm['alloc']=mode
    p,w,to=ga.simulate(gm,Xhi,RX,rf,5)
    ck('PF-05_alloc_'+mode,np.isfinite(p).all() and np.isfinite(w).all())

# SAFE genuine: negative/zero long opportunity with shorts disabled -> 100% SAFE.
gn=json.loads(json.dumps(g)); gn['modules'][0]['signal_w']=[-4.0]; gn['short']=False
_,Wn,_=ga.simulate(gn,Xhi,RX,rf,5)
ck('PF-20_safe_genuine',float(np.abs(Wn).sum())==0.0,float(np.abs(Wn).sum()))

# No leverage.
R=random.Random(20261005)
for i in range(100):
    gr=ga.random_genome(R,F,groups)
    _,w,_=ga.simulate(gr,X,RX,rf,5)
    if np.max(np.abs(w).sum(1))>1+1e-9: raise AssertionError('leverage')
ck('PF-19_no_leverage',True)

# No forbidden horizon/entry state in decision code.
src=P.read_text()
forbidden=['held_days','min_hold','max_hold','entry_price','entry_date','cooldown']
ck('PF-16_no_hold_or_entry_state',not any(x in src for x in forbidden),[x for x in forbidden if x in src])

# Ticker identity absent from genome/simulate functions.
import inspect
dec=inspect.getsource(ga.random_genome)+inspect.getsource(ga.opportunity)+inspect.getsource(ga.simulate)
ck('PF-22_no_ticker_identity','ticker' not in dec.lower())

# Sentinel old defect must not exist.
ck('PF-OLD_rank_transform_removed','argsort(np.argsort(raw' not in src)

out=Path('/home/ubuntu/Momentum-Trading-System_v4/Research/Reports/MTS_FROZEN_ARCH_GA_V2_PREFLIGHT_20261005.json')
out.write_text(json.dumps({'status':'PASS','runner_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':results},indent=2))
print('PREFLIGHT_PASS',out)
print(json.dumps(results,indent=2))

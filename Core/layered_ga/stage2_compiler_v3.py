from __future__ import annotations

from pathlib import Path
import math
import random
import sys
from typing import Any, Mapping
import numpy as np
import pandas as pd

CERTIFIED_ROOT = Path(__file__).resolve().parents[2] / 'Reconstruction/Certified-Stage2-Source-20261007'
root=str(CERTIFIED_ROOT)
if root not in sys.path: sys.path.insert(0,root)
from MTS_V4.computational_search import Gene,SearchSpace
from MTS_V4.search_families import FAMILY_FACTORIES

UNAVAILABLE_OR_NONCAUSAL_FEATURES=frozenset({'turnover__v1','turnover_relative_20__v1','sector_return_252_percentile__v1'})

CERTIFIED_FAMILIES=(
    'MOMENTUM','BREAKOUT','TREND','MEAN_REVERSION','VOLATILITY',
    'VOLUME_LIQUIDITY','RELATIVE_CROSS_SECTIONAL','MARKET_REGIME_STRUCTURE'
)


def stage2_search_spaces() -> dict[str,SearchSpace]:
    out={}
    for fam in CERTIFIED_FAMILIES:
        src=FAMILY_FACTORIES[fam]()
        genes=[];excluded=[]
        for g in src.genes:
            if g.gene_id=='forward_horizon':continue
            vals=tuple(v for v in g.values if v not in UNAVAILABLE_OR_NONCAUSAL_FEATURES)
            removed=[v for v in g.values if v in UNAVAILABLE_OR_NONCAUSAL_FEATURES]
            if removed: excluded.extend((g.gene_id,v) for v in removed)
            genes.append(Gene(g.gene_id,vals,g.feature_column,g.meaning))
        attrs=dict(src.attributes);attrs.update({'stage2_v3_full_path':True,'forward_horizon_gene_removed':True,'source_content_hash':src.content_hash,'excluded_values':tuple(excluded)})
        out[fam]=SearchSpace(src.search_space_id+'-stage2-v3',src.version,fam,tuple(genes),src.maximum_active_predicates,attrs)
    return out


def random_genome(space:SearchSpace,rng:random.Random)->dict[str,Any]:
    return {g.gene_id:rng.choice(g.values) for g in space.genes}


class VectorSignalCompiler:
    def __init__(self,frame:pd.DataFrame):
        self.frame=frame.reset_index(drop=True)
        self._arrays:dict[str,np.ndarray]={}
        self._q:dict[tuple[str,float],float|None]={}

    def arr(self,feature:str)->np.ndarray:
        if feature not in self._arrays:
            self._arrays[feature]=pd.to_numeric(self.frame[feature],errors='coerce').to_numpy(float)
        return self._arrays[feature]

    def qthreshold(self,feature:str,q:float)->float|None:
        key=(feature,float(q))
        if key not in self._q:
            a=self.arr(feature);clean=a[np.isfinite(a)]
            if len(clean)==0:self._q[key]=None
            else:
                # Reproduce recovered _quantile arithmetic exactly. Tiny IEEE-754
                # boundary differences are scientifically material for >=/<= predicates.
                ordered=sorted(float(x) for x in clean)
                pos=(len(ordered)-1)*float(q);lo=math.floor(pos);hi=math.ceil(pos)
                if lo==hi: threshold=ordered[lo]
                else:
                    w=pos-lo;threshold=ordered[lo]*(1-w)+ordered[hi]*w
                self._q[key]=float(threshold)
        return self._q[key]

    @staticmethod
    def pred(a:np.ndarray,mode:str,t:float)->np.ndarray:
        valid=np.isfinite(a)
        if mode in {'ABOVE','HIGH','LEADER','POSITIVE'}:return valid & (a>=t)
        if mode in {'BELOW','LOW','LAGGARD','NEGATIVE'}:return valid & (a<=t)
        return np.zeros(len(a),dtype=bool)

    def compile(self,family:str,g:Mapping[str,Any])->np.ndarray:
        n=len(self.frame);signal=np.zeros(n,dtype=bool)
        if family=='MOMENTUM':
            f=g['momentum_feature'];q=float(g['threshold_quantile']);t=self.qthreshold(f,q if g['direction']=='ABOVE' else 1-q)
            if t is None:return signal
            signal=self.pred(self.arr(f),g['direction'],t);cf=g['context_feature']
            if cf!='NONE': signal &= np.isfinite(self.arr(cf)) & (self.arr(cf)>=float(g['context_threshold']))
        elif family=='BREAKOUT':
            f=g['range_feature'];rt=self.qthreshold(f,float(g['range_threshold_quantile']))
            if rt is None:return signal
            signal=self.pred(self.arr(f),'ABOVE',rt);pf=g['participation_feature']
            if pf!='NONE':
                pt=self.qthreshold(pf,float(g['participation_threshold_quantile']));signal &= False if pt is None else self.pred(self.arr(pf),'ABOVE',pt)
            vf=g['volatility_feature']
            if vf!='NONE':
                vq=float(g['volatility_threshold_quantile']);vt=self.qthreshold(vf,vq if g['volatility_state']=='HIGH' else 1-vq)
                signal &= False if vt is None else self.pred(self.arr(vf),g['volatility_state'],vt)
        elif family=='TREND':
            tf=g['trend_feature'];tq=float(g['threshold_quantile']);tt=self.qthreshold(tf,tq if g['direction']=='ABOVE' else 1-tq)
            if tt is None:return signal
            signal=self.pred(self.arr(tf),g['direction'],tt);cf=g['confirmation_feature']
            if cf!='NONE':
                cq=float(g['confirmation_threshold_quantile']);ct=self.qthreshold(cf,cq if g['confirmation_direction']=='ABOVE' else 1-cq)
                signal &= False if ct is None else self.pred(self.arr(cf),g['confirmation_direction'],ct)
        elif family=='MEAN_REVERSION':
            f=g['displacement_feature'];tail=g['tail'];sev=float(g['severity']);t=self.qthreshold(f,sev if tail=='LOW' else 1-sev)
            if t is None:return signal
            signal=self.pred(self.arr(f),tail,t);cf=g['context_feature']
            if cf!='NONE':
                cq=float(g['context_threshold_quantile']);ct=self.qthreshold(cf,cq if g['context_state']=='HIGH' else 1-cq)
                signal &= False if ct is None else self.pred(self.arr(cf),g['context_state'],ct)
        elif family=='VOLATILITY':
            f=g['volatility_feature'];state=g['state'];q=float(g['threshold_quantile']);t=self.qthreshold(f,q if state=='HIGH' else 1-q)
            if t is None:return signal
            signal=self.pred(self.arr(f),state,t);pf=g['price_context']
            if pf!='NONE':
                pt=self.qthreshold(pf,.5);signal &= False if pt is None else self.pred(self.arr(pf),'ABOVE',pt)
        elif family=='VOLUME_LIQUIDITY':
            pf=g['participation_feature'];q=float(g['threshold_quantile']);pt=self.qthreshold(pf,q if g['state']=='HIGH' else 1-q)
            if pt is None:return signal
            signal=self.pred(self.arr(pf),g['state'],pt);price=g['price_feature']
            if price!='NONE':
                pq=float(g['price_threshold_quantile']);pth=self.qthreshold(price,pq if g['price_direction']=='ABOVE' else 1-pq)
                signal &= False if pth is None else self.pred(self.arr(price),g['price_direction'],pth)
        elif family=='RELATIVE_CROSS_SECTIONAL':
            rf=g['relative_feature'];q=float(g['threshold_quantile']);rt=self.qthreshold(rf,q if g['tail']=='LEADER' else 1-q)
            if rt is None:return signal
            signal=self.pred(self.arr(rf),g['tail'],rt);mf=g['market_context']
            if mf!='NONE':signal &= self.pred(self.arr(mf),g['market_context_state'],float(g['market_context_threshold']))
        elif family=='MARKET_REGIME_STRUCTURE':
            f=g['breadth_feature'];state=g['breadth_state'];t=float(g['breadth_threshold']);v=self.arr(f);valid=np.isfinite(v)
            if state=='LOW':signal=valid&(v<t)
            elif state=='HIGH':signal=valid&(v>t)
            else:signal=valid&(np.abs(v-t)<=.10)
            sf=g['security_context']
            if sf!='NONE':
                sq=float(g['security_context_threshold_quantile']);st=self.qthreshold(sf,sq if g['security_context_direction']=='ABOVE' else 1-sq)
                signal &= False if st is None else self.pred(self.arr(sf),g['security_context_direction'],st)
        else: raise ValueError(f'uncertified/unhandled family {family}')
        return np.asarray(signal,dtype=np.bool_)

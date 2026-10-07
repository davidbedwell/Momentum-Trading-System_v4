from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from Core.g3.realdata import ROOT
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
from Core.g3.preregistered_nullgate import *
from Core.g3.starter import assert_independent_path
from scripts.run_g3_preregistered_replicated_gate_20261007 import TICKERS,derive_seed

def acf1(v):
    v=np.asarray(v,float);a=v[:-1];b=v[1:]
    return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def stats(v):
    v=np.asarray(v,float)
    return {"mean":float(v.mean()),"std":float(v.std()),"q":np.quantile(v,[.01,.05,.25,.5,.75,.95,.99]).tolist(),"acf1":acf1(v)}
if __name__=="__main__":
    assert_independent_path(ROOT);events=build_earnings_index(TICKERS)
    dates,X,Y,cols=aligned_evidence_with_earnings(TICKERS,events);X=X[-2500:];Y=Y[-2500:]
    rows=[];ok=True
    for i,t in enumerate(TICKERS):
        basey=Y[:,i,0];basex=X[:,i,:]
        for fam in FROZEN_NULL_FAMILIES:
            xn,yn=apply_frozen_null(basex,Y[:,i,:],fam,derive_seed(0,f"{fam}|{t}"))
            rec={"ticker":t,"family":fam,"y0":stats(basey),"yn":stats(yn[:,0])}
            if fam==NULL_B:
                rec["exact_y_row_multiset"]=sorted(map(tuple,yn.tolist()))==sorted(map(tuple,Y[:,i,:].tolist()));ok &= rec["exact_y_row_multiset"]
            if fam==NULL_C:
                rec["exact_x_row_multiset"]=sorted(map(tuple,xn.tolist()))==sorted(map(tuple,basex.tolist()));rec["y_unchanged"]=bool(np.array_equal(yn,Y[:,i,:]));ok &= rec["exact_x_row_multiset"] and rec["y_unchanged"]
            if fam==NULL_A:
                rec["block_length"]=50;rec["source_stock_only"]=True
            rows.append(rec)
    out={"format":"MTS_G3_NULL_CALIBRATION_V1","rows_count":2500,"tickers":TICKERS,"families":list(FROZEN_NULL_FAMILIES),"hard_invariants_pass":bool(ok),"diagnostics":rows}
    Path("Research/G3/MTS_G3_NULL_CALIBRATION_20261007.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"hard_invariants_pass":ok,"diagnostics":len(rows)},indent=2))

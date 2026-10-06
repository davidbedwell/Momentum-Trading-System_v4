import importlib.util, pathlib, numpy as np, json
R=pathlib.Path("/home/ubuntu/Momentum-Trading-System_v4")
sp=importlib.util.spec_from_file_location("ga",R/"scripts/run_ga_redesign_approved_20261006.py");ga=importlib.util.module_from_spec(sp);sp.loader.exec_module(ga)
d67,d50,dev,dates,X,RX,rf,names,groups,P,px,C=ga.build_arrays();tr,bl=ga.folds(dev)[0];imap={t:i for i,t in enumerate(dev)}
dt,tt,Xt,*_=ga.v2.make_arrays(tr); db,tb,Xb,*_=ga.v2.make_arrays(bl)
assert np.array_equal(dates,dt) and np.array_equal(dates,db)
fi=np.array([imap[t] for t in tr]);bi=np.array([imap[t] for t in bl])
stockn=17
A=X[:,fi,:stockn];B=Xt[:,:,:stockn];mask=np.isfinite(A)&np.isfinite(B)
C1=X[:,bi,:stockn];D=Xb[:,:,:stockn];maskb=np.isfinite(C1)&np.isfinite(D)
pt,_=ga.dynamic_peer_context(px,dates,tr);pb,_=ga.dynamic_peer_context(px,dates,bl)
peer_start=groups["peer"][0];PA=X[:,fi,peer_start:peer_start+7];PB=X[:,bi,peer_start:peer_start+7]
def stat(a,b,m=None):
 if m is None:m=np.isfinite(a)&np.isfinite(b)
 z=np.abs(a[m]-b[m]);return {"n":int(z.size),"changed_gt_1e-7":int((z>1e-7).sum()),"fraction_changed":float((z>1e-7).mean()),"mean_abs_delta":float(z.mean()),"max_abs_delta":float(z.max())}
out={"fold":0,"train80_xs_rank_all117_vs_recomputed80":stat(A,B,mask),"blind37_xs_rank_all117_vs_recomputed37":stat(C1,D,maskb),"train80_peer_all117_vs_recomputed80":stat(PA,pt),"blind37_peer_all117_vs_recomputed37":stat(PB,pb)}
op=R/"Research/Reports/MTS_FOLD_FEATURE_ISOLATION_AUDIT_20261006.json";op.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print("OUT",op)

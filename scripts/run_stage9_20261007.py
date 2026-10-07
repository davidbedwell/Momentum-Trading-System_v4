#!/usr/bin/env python3
from layered_stage_common_20261007 import *
gal=pd.read_parquet(RUN/'stage1-context-map-20261007/galaxy_context.parquet')
# integrate separately governed A/B/C dimensions as observable defense evidence, not tune against portfolio return
x=gal.copy();ret=x.adj_close.pct_change();dd=x.adj_close/x.adj_close.cummax()-1
A=(x.ret20<-0.10)&(x.rv20>x.rv20.expanding().quantile(.8))
B=(x.ma_gap50<0)&(x.ret60<0)
C=(x.ret20<0)&(x.trajectory<0)&(dd<-0.08)
defensive=(A|B|C)
write(9,'portfolio-catastrophe',{'defensive_days':int(defensive.sum()),'total_days':len(x),'defensive_fraction':float(defensive.mean()),'A_days':int(A.sum()),'B_days':int(B.sum()),'C_days':int(C.sum()),'integration':'Boolean OR survival override; R-1 recovery remains six-dimensional governed recovery evidence.','warning':'Thresholds are calibration descriptors for integration, not upstream opportunity gates.'})

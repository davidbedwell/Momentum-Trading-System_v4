"""Fail-closed coverage audit: never substitute GA4 features for Horizons aliases."""
from .horizons_native_score import FEATURES
from .synthetic_fiveyear_panel import ROOT
import pyarrow.parquet as pq

def audit():
 result=[]
 for scenario in range(1,6):
  paths=[ROOT/f'universe_{scenario}_ga4_native.parquet',ROOT/f'universe_{scenario}_eight_family.parquet']
  cols=set().union(*(set(pq.read_schema(p).names) for p in paths))
  available=sorted(set(FEATURES)&cols)
  missing=sorted(set(FEATURES)-cols)
  result.append({'scenario':scenario,'available_native':available,'missing_native':missing,'coverage':len(available),'required':len(FEATURES)})
 return result
if __name__=='__main__':
 for row in audit():print(row)

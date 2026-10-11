"""Leakage-guarded distressed path nearest-neighbor classifier."""
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
def matched_failure_scores(train_features,train_outcome,query_features,neighbors=25):
 x=np.asarray(train_features,dtype=float);q=np.asarray(query_features,dtype=float)
 y=np.asarray(train_outcome,dtype=int)
 if x.ndim!=2 or q.ndim!=2 or x.shape[1]!=q.shape[1] or x.shape[0]!=len(y):
  raise ValueError('Feature alignment mismatch')
 if len(x)<neighbors or neighbors<1 or not np.isfinite(x).all() or not np.isfinite(q).all():
  raise ValueError('Insufficient or nonfinite matched support')
 if not np.isin(y,[0,1]).all() or len(np.unique(y))<2:raise ValueError('Both outcome classes required')
 scaler=StandardScaler().fit(x)
 model=NearestNeighbors(n_neighbors=neighbors).fit(scaler.transform(x))
 dist,ids=model.kneighbors(scaler.transform(q))
 return {'failure_probability':y[ids].mean(axis=1),'mean_neighbor_distance':dist.mean(axis=1),
         'baseline_probability':float(y.mean()),'train_count':len(y)}
def select_threshold(calibration_scores,calibration_truth,min_support=30):
 p=np.asarray(calibration_scores,float);y=np.asarray(calibration_truth,int)
 if p.ndim!=1 or p.shape!=y.shape or not np.isfinite(p).all() or not np.isin(y,[0,1]).all() or not np.all((p>=0)&(p<=1)):
  raise ValueError('Invalid calibration')
 if not len(y):return None
 base=y.mean();eligible=[]
 for t in np.arange(.5,.951,.05):
  subset=p>=t
  if subset.sum()>=min_support:
   lift=y[subset].mean()-base
   eligible.append((float(lift),float(t)))
 if not eligible:return None
 best=max(eligible)
 return best[1] if best[0]>0 else None

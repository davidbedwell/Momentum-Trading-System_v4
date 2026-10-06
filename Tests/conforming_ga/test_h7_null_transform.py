import numpy as np,pandas as pd,pytest
from Core.conforming_ga.h7_g2 import null_long_df,null_tape

def frame(T=61,N=4):
 dates=pd.bdate_range("2020-01-01",periods=T);rows=[]
 for j in range(N):
  ret=np.arange(T,dtype=float)*.0001 + j*.00001
  adj=np.empty(T);adj[0]=100+j
  for t in range(1,T):adj[t]=adj[t-1]*(1+ret[t])
  for t,d in enumerate(dates):
   rows.append(dict(date=d,ticker=f"S{j}",adj_close=adj[t],close=adj[t],open=adj[t]*.999,high=adj[t]*1.002,low=adj[t]*.998,volume=1e6+t*100+j,dividends=0.0))
 return pd.DataFrame(rows),tuple(f"S{j}" for j in range(N))

def returns(df,tickers):
 a=df.pivot(index="date",columns="ticker",values="adj_close").reindex(columns=tickers).to_numpy()
 return a[1:]/a[:-1]-1

def test_null_common_permutation_preserves_cross_sectional_return_vectors():
 d,t=frame();o=returns(d,t);n=returns(null_long_df(d,t,7,block=10),t)
 # Every null cross-sectional return vector must be one original vector.
 for row in n:
  assert np.any(np.all(np.isclose(o,row,rtol=1e-10,atol=1e-12),axis=1))

def test_null_is_deterministic_and_changes_temporal_alignment():
 d,t=frame();a=null_long_df(d,t,91,10);b=null_long_df(d,t,91,10)
 pd.testing.assert_frame_equal(a,b)
 assert not np.allclose(returns(d,t),returns(a,t))

def test_null_moves_stock_microstructure_with_common_source_days():
 d,t=frame();n=null_long_df(d,t,17,10)
 # Relative OHLC shape remains internally valid after reconstruction.
 assert np.all(n.high>=n.close)
 assert np.all(n.low<=n.close)

def test_legacy_tape_null_is_fail_closed():
 with pytest.raises(RuntimeError,match="NONCONFORMING_LEGACY_NULL_DISABLED"):
  null_tape(None,1)

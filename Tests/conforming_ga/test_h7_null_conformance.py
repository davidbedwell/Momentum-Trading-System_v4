import numpy as np,pandas as pd
from pathlib import Path
from Core.conforming_ga.h7_g2 import null_long_df,build_null_tape
from Core.conforming_ga.g2features import build_g2_tape
from Core.conforming_ga.realdata import FoldLoader
from Core.conforming_ga.null_provenance import CHRONOLOGICAL_EXOGENOUS_PIT_STOCK_CONTEXT,assert_stock_bank_provenance

REPO=Path(__file__).resolve().parents[2]
MIRROR=Path("/home/ubuntu/mts-clean-folds-20261006")

def _ret(df,tickers):
 a=df.pivot(index="date",columns="ticker",values="adj_close").reindex(columns=tickers).to_numpy(float)
 return a[1:]/a[:-1]-1

def _corrvec(r):
 x=np.nan_to_num(r);sd=x.std(axis=0);good=sd>1e-15
 return np.corrcoef(x[:,good],rowvar=False)

def test_full_null_provenance_and_rebuild_contract():
 L=FoldLoader(REPO,MIRROR,0,"train");raw=L.load_prices()
 raw=raw[(raw.date>="2018-01-01")&(raw.date<="2021-12-31")].copy();tickers=L.tickers
 nraw1=null_long_df(raw,tickers,12345,20);nraw2=null_long_df(raw,tickers,12345,20)
 pd.testing.assert_frame_equal(nraw1,nraw2)
 orig=_ret(raw,tickers);nul=_ret(nraw1,tickers)
 # Same common schedule preserves the multiset of cross-sectional daily vectors.
 # Sort rows by a deterministic lexicographic key and compare.
 so=np.lexsort(np.nan_to_num(orig).T[::-1]);sn=np.lexsort(np.nan_to_num(nul).T[::-1])
 assert np.allclose(orig[so],nul[sn],equal_nan=True,rtol=1e-10,atol=1e-12)
 # Cross-sectional dependence is materially preserved.
 assert np.allclose(_corrvec(orig),_corrvec(nul),equal_nan=True,rtol=1e-8,atol=1e-10)
 # But original chronological association is destroyed.
 assert not np.allclose(orig,nul,equal_nan=True)
 actual=build_g2_tape(REPO,raw,tickers,start="2018-06-01",end="2021-06-30")
 null1=build_null_tape(REPO,raw,tickers,12345,20,start="2018-06-01",end="2021-06-30")
 null2=build_null_tape(REPO,raw,tickers,12345,20,start="2018-06-01",end="2021-06-30")
 # Genuine external market/context chronology stays bit/equality-identical.
 assert actual.market.keys()==null1.market.keys()
 assert all(np.array_equal(actual.market[k],null1.market[k],equal_nan=True) for k in actual.market)
 # Deterministic full tape reproduction.
 for bank in ("stock","sector","market","execution"):
  a=getattr(null1,bank);b=getattr(null2,bank)
  assert a.keys()==b.keys()
  assert all(np.array_equal(a[k],b[k],equal_nan=True) for k in a)
 # Stock-derived rolling features and every dynamic-peer feature are rebuilt.
 changed_stock=[k for k in actual.stock if not np.array_equal(actual.stock[k],null1.stock[k],equal_nan=True)]
 changed_peer=[k for k in actual.sector if not np.array_equal(actual.sector[k],null1.sector[k],equal_nan=True)]
 assert_stock_bank_provenance(actual.stock.keys())
 invariant_stock=set(actual.stock)-set(changed_stock)
 # Provenance is the contract: only registered PIT/exogenous fields may be
 # intentionally carried unchanged. Numerical inequality is supporting
 # evidence, not the definition of stock-path conformance.
 assert invariant_stock <= CHRONOLOGICAL_EXOGENOUS_PIT_STOCK_CONTEXT
 # Strong empirical evidence on this controlled fixture: every currently
 # stock-path-derived field did in fact change, as did every dynamic peer.
 path_fields=set(actual.stock)-CHRONOLOGICAL_EXOGENOUS_PIT_STOCK_CONTEXT
 assert path_fields <= set(changed_stock)
 assert len(path_fields)==42
 assert set(changed_peer)==set(actual.sector)

import numpy as np
import pandas as pd
from Core.g3.realdata import causal_zscore

def test_causal_normalization_future_mutation_cannot_change_past():
    idx=pd.date_range("2020-01-01", periods=80, freq="D")
    base=pd.DataFrame({"a":np.arange(1.,81.),"b":np.arange(101.,181.)},index=idx)
    changed=base.copy()
    changed.iloc[60:,:] *= 1000000.0
    x1=causal_zscore(base,min_periods=5)
    x2=causal_zscore(changed,min_periods=5)
    pd.testing.assert_frame_equal(x1.iloc[:60],x2.iloc[:60])

def test_causal_normalization_current_row_not_in_own_baseline():
    idx=pd.date_range("2020-01-01", periods=8, freq="D")
    base=pd.DataFrame({"a":[1.,2.,3.,4.,5.,6.,7.,8.]},index=idx)
    changed=base.copy(); changed.iloc[6,0]=7000.0
    x2=causal_zscore(changed,min_periods=3)
    hist=base.iloc[:6,0]
    expected=(7000.0-hist.mean())/hist.std(ddof=0)
    assert np.isclose(x2.iloc[6,0],expected)

def test_evidence_arrays_drops_incomplete_future_horizons(tmp_path, monkeypatch):
    import Core.g3.realdata as rd
    raw=tmp_path/"raw"; derived=tmp_path/"derived"
    raw.mkdir(); derived.mkdir()
    idx=pd.date_range("2020-01-01", periods=12, freq="D")
    prices=pd.DataFrame({"adj_close":np.arange(100.,112.)},index=idx)
    features=pd.DataFrame({"f1":np.arange(1.,13.),"f2":np.arange(21.,33.)},index=idx)
    prices.to_parquet(raw/"T.parquet"); features.to_parquet(derived/"T.parquet")
    monkeypatch.setattr(rd,"RAW",raw); monkeypatch.setattr(rd,"DERIVED",derived)
    X,Y,cols=rd.evidence_arrays("T",horizon=3,min_normalization_history=2)
    # First two rows are normalization warmup; last three lack a full future path.
    assert X.shape == (7,2)
    assert Y.shape == (7,3)
    assert cols == ["f1","f2"]
    # The final retained target must use real observations 109->110->111,
    # never repeated/padded terminal prices.
    np.testing.assert_allclose(Y[-1], [109/108-1,110/109-1,111/110-1])
    assert np.isfinite(X).all() and np.isfinite(Y).all()

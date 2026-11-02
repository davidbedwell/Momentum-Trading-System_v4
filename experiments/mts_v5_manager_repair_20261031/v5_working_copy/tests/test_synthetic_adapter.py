import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"discovery"/"competitive_ga"))
from synthetic_adapter import load_fsynth,close_features_at

def test_hides_future_and_generator_labels(tmp_path):
    p=tmp_path/"market";p.mkdir()
    rows=[]
    for i in range(25):
        rows.append({"Date":pd.Timestamp("2020-01-01")+pd.Timedelta(days=i),"Ticker":"A","Open":100+i,"High":101+i,"Low":99+i,"Close":100+i,"Volume":1000,"Regime":99})
    pd.DataFrame(rows).to_parquet(p/"stock_prices.parquet")
    df=load_fsynth(p)
    assert "Regime" not in df
    early=close_features_at(df,"2020-01-21",5)
    changed=df.copy()
    changed.loc[changed.Date>pd.Timestamp("2020-01-21"),"Close"]*=5
    assert early.equals(close_features_at(changed,"2020-01-21",5))

def test_rejects_invalid_prices(tmp_path):
    p=tmp_path/"market";p.mkdir()
    pd.DataFrame([{"Date":"2020-01-01","Ticker":"A","Open":100,"High":101,"Low":99,"Close":105,"Volume":1000}]).to_parquet(p/"stock_prices.parquet")
    with pytest.raises(ValueError,match="invalid OHLC"):load_fsynth(p)

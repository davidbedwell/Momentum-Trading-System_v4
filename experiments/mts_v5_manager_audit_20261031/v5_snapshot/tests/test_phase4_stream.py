"""Proof seal and metadata tests contain only labeled generated fixtures."""
import pandas as pd
import pytest
from discovery.competitive_ga.streaming_first_year import inventory, chunks
from discovery.competitive_ga.first_year_manifest import Calendar

D=('2026-01-02','2026-01-05','2026-01-06')
T=tuple(f'T{i:03}' for i in range(500))
C=Calendar(D,*D)


def test_metadata_inventory_never_needs_price_columns(tmp_path):
    path=tmp_path/'metadata.parquet'
    pd.DataFrame([(pd.Timestamp(d),t) for d in D for t in T],columns=['Date','Ticker']).to_parquet(path)
    assert inventory(path)==(D,T)


@pytest.mark.parametrize('kind',['duplicate','missing','foreign'])
def test_inventory_rejects_bad_daily_universe(tmp_path,kind):
    path=tmp_path/'metadata.parquet'
    p=pd.DataFrame([(pd.Timestamp(d),t) for d in D for t in T],columns=['Date','Ticker'])
    if kind=='duplicate':p=pd.concat([p,p.iloc[:1]])
    if kind=='missing':p=p.iloc[1:]
    if kind=='foreign':p.loc[0,'Ticker']='FOREIGN'
    p.to_parquet(path)
    with pytest.raises(ValueError):inventory(path)


def test_stream_seal_precedes_any_legacy_or_cache_io(tmp_path):
    with pytest.raises(ValueError,match='sealed proof'):
        next(chunks(calendar=C,as_of=D[2],tickers=T,cache=tmp_path,raw_path='/missing'))
    assert list(tmp_path.iterdir())==[]


@pytest.mark.parametrize('size',[0,129,1.5,True])
def test_chunk_limits_precede_source_io(tmp_path,size):
    with pytest.raises(ValueError,match='chunk size'):
        next(chunks(calendar=C,as_of=D[1],tickers=T,cache=tmp_path,raw_path='/missing',chunk_sessions=size))

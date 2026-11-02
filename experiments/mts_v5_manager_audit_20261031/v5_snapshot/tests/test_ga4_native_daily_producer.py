import pandas as pd
import pytest
from discovery.competitive_ga.ga4_native_daily_producer import produce

class Compiler:
    def __init__(self,frame):self.frame=frame
    def compile(self,family,genome):
        return (self.frame['signal']>genome['threshold']).to_numpy()


def run(frame):
    return produce(Compiler(frame),[('MOMENTUM',{'threshold':.5})],
        decision_date='2020-01-02',chromosome_id='ga4-1',
        trained_through='2020-01-01',source_hash='source',snapshot_hash='snap')


def test_ga4_native_predicate_becomes_provenanced_entry():
    panel=pd.DataFrame({'date':['2020-01-02']*3,'ticker':['A','B','C'],
                        'signal':[.2,.8,.9]})
    result=run(panel)
    assert [p.ticker for p in result]==['B','C']
    assert all(p.family=='GA4' and p.action=='ENTER' for p in result)


def test_future_date_and_duplicate_ticker_rejected():
    panel=pd.DataFrame({'date':['2020-01-02','2020-01-03'],
                        'ticker':['A','B'],'signal':[.2,.9]})
    with pytest.raises(ValueError,match='future quantile leakage'):
        run(panel)
    panel['date']='2020-01-02'
    panel['ticker']=['A','A']
    with pytest.raises(ValueError,match='duplicate ticker'):
        run(panel)

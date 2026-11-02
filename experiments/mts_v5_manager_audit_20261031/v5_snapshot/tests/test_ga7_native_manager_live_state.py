"""GA7 native stop from actual next-open fill, with fee-inclusive cost basis."""
from types import SimpleNamespace
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.ga7_native_daily_producer import produce
from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.causal_calibration import TradeOutcome

class FeatureBar(dict):
    @property
    def close(self):return self['close']
    @property
    def open(self):return self['open']
    @property
    def dividend(self):return 0.
    @property
    def split(self):return 1.

def test_ga7_native_exit_uses_actual_fill_and_genome_stop():
    genome=SimpleNamespace(operator='AND',entry_pct=.07,feature_a='a',feature_b='b',
        threshold_a=0.,threshold_b=0.,stop_pct=.012,exit_rule='signal_decay')
    observations=[]
    def producer(date,session,bars,holdings,owners,defense,fillbook):
        held={t:fillbook.held(t,bars[t].close,100000.) for t,p in fillbook.positions.items() if p.owner==('GA7','c7')}
        observations.append((session,held))
        if session>=4:return []
        return produce(genome,bars,decision_date=date,trained_through='2020-01-01',
            source_hash='src',snapshot_hash='snapshot',chromosome_id='c7',defensive=defense,held=held)
    days=[]
    for i in range(6):
        features={'a':.9,'b':.9} if i<3 else {'a':.1,'b':.1}
        bars={'AAA':FeatureBar(open=100,close=100,eligible=True,features=features)}
        outcomes=[TradeOutcome('c7',('GA7_ENTRY',),0,i,.1,'shadow')] if i==1 else []
        days.append((f'2020-01-{i+2:02d}',bars,producer,outcomes,False))
    result=run(days,min_samples=1,stops_by_owner={('GA7','c7'):.012})
    assert [x[2] for x in result['ledger']]==['BUY','SELL']
    assert observations[3][1]['AAA']['initial_stop']==.012
    assert observations[3][1]['AAA']['entry']==100
    assert result['position_basis']=={}

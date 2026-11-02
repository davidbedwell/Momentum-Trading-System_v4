from discovery.competitive_ga.manager_policy_v2 import Genes,Proposal
from discovery.competitive_ga.manager_order_adapter import orders
from engines.portfolio_replay.kernel import Replay,Bar


def proposal(ticker,action,edge,target,chrom='g1'):
    return Proposal(ticker,chrom,'GA6',action,edge,0,1,target,True,12)


def test_competitive_entry_and_exit_execute_next_open():
    p=Replay()
    decisions=orders([proposal('A','ENTER',.08,.08)],{},1.,Genes(min_edge=.01))
    p.day('day1',{'A':Bar(100,100)},decisions)
    assert not p.ledger
    p.day('day2',{'A':Bar(100,100)},())
    assert p.shares['A']>0
    weight=p.shares['A']*100/p.nav[-1][1]
    exits=orders([proposal('A','EXIT',.10,0)],{'A':weight},p.cash/p.nav[-1][1],Genes())
    p.day('day3',{'A':Bar(100,100)},exits)
    assert p.shares['A']>0
    p.day('day4',{'A':Bar(100,100)},())
    assert 'A' not in p.shares
    assert p.ledger[-1][2]=='SELL'


def test_uncalibrated_proposals_cannot_deploy():
    x=proposal('A','ENTER',.08,.08)
    x=Proposal(x.ticker,x.chromosome_id,x.family,x.action,x.edge,x.downside,x.confidence,x.target,False,0)
    assert orders([x],{},1.,Genes())==[]


def test_replacement_cannot_recycle_unsettled_cash():
    genes=Genes(min_edge=.01,replace_margin=.01,max_initial=.10)
    positions={'OLD':.10}
    ps=[proposal('OLD','HOLD',.02,.10),proposal('NEW','ENTER',.10,.10)]
    result=orders(ps,positions,0.,genes)
    assert any(s.ticker=='OLD' and s.target_weight==0 for s in result)
    assert not any(s.ticker=='NEW' and s.target_weight>0 for s in result)

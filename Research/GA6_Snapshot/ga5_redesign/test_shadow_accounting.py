from ga5_redesign.shadow_signals import ShadowBook
from ga5_redesign.niche_seeds import initial

def test_shadow_partial_fill_reconciliation():
 b=ShadowBook(initial('growth'),fee=.001)
 policy={('2026-01-01','A'):True,('2026-01-02','A'):True,('2026-01-03','A'):True,('2026-01-04','A'):True}
 veto={d:True for d in ('2026-01-01','2026-01-02','2026-01-03','2026-01-04')}
 b.pending['A']=('BUY','2026-01-01',1.)
 b.start('2026-01-01',{'A':100},{},policy,veto)
 b.pending['A']=('SCALE_IN','2026-01-01',.5)
 b.start('2026-01-02',{'A':110},{},policy,veto)
 assert abs(b.open['A']['shares']-(1+min(.5,b.genome.max_weight)))<1e-12
 b.pending['A']=('SCALE_OUT','2026-01-02',.5)
 b.start('2026-01-03',{'A':120},{},policy,veto,{'A':{'dividends':1,'stock_splits':0}})
 assert abs(b.open['A']['shares']-(1+min(.5,b.genome.max_weight))*.5)<1e-12
 b.pending['A']=('SELL','2026-01-03',1.)
 b.start('2026-01-04',{'A':130},{},policy,veto)
 assert len(b.closed)==1 and not b.open
 tr=b.closed[0]
 buys=sum(e['price']*e['quantity']*1.001 for e in b.events if e['kind']=='BUY')
 sells=sum(e['price']*e['quantity']*.999 for e in b.events if e['kind']=='SELL')
 dividends=sum(e['price']*e['quantity'] for e in b.events if e['kind']=='DIVIDEND')
 assert abs(tr['realized_pnl']-(sells+dividends-buys))<1e-8
 assert abs(tr['net_return']-tr['realized_pnl']/buys)<1e-10
 assert len(b.events)==5

def test_shadow_split_is_audited_not_double_adjusted():
 b=ShadowBook(initial('growth'))
 b.pending['A']=('BUY','2026-01-01',1.)
 membership={('2026-01-01','A'):True,('2026-01-02','A'):True}
 veto={'2026-01-01':True,'2026-01-02':True}
 b.start('2026-01-01',{'A':100},{},membership,veto)
 b.start('2026-01-02',{'A':100},{},membership,veto,{'A':{'stock_splits':2,'dividends':0}})
 assert b.open['A']['shares']==1
 assert b.events[-1]['kind']=='SPLIT_REPORTED'

from shared_capital_execution import SharedCapitalExecution
x=SharedCapitalExecution(cash=10000,annual_cash_yield=0)
rows={'AAA':{'dividends':0,'stock_splits':0},'BBB':{'dividends':0,'stock_splits':0}}
mem={(d,t):True for d in ('2024-01-02','2024-01-03','2024-01-04','2024-01-05') for t in rows}
def step(d,price=100,defense=True,dividend=0):
 rows['AAA']['dividends']=dividend
 return x.start(d,{'AAA':price,'BBB':100},{'AAA':price,'BBB':100},rows,risk_veto={d:defense},membership=mem,blocked={})
step('2024-01-02');x.schedule('2024-01-02',[dict(symbol='AAA',action='ENTER',weight=.5,max_weight=.5)])
step('2024-01-03');assert x.ledger.holdings['AAA']==49
x.schedule('2024-01-03',[dict(symbol='AAA',action='EXIT')])
step('2024-01-04',dividend=1)
assert x.ledger.holdings['AAA']==0 and x.ledger.available_cash()<x.ledger.cash
x.schedule('2024-01-04',[dict(symbol='BBB',action='ENTER',weight=.9,max_weight=.9)])
step('2024-01-05')
assert x.ledger.holdings['BBB']>0 and x.ledger.available_cash()>=0
assert x.ledger.dividend_cash==49 and len(x.closed)==1
assert all(f['execution_date']>f['decision_date'] for f in x.ledger.fills)
print('PASS: shared cash, T+1, dividend, original PositionRisk, next-open fills',len(x.ledger.fills),'fills',x.nav[-1])

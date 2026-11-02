import unittest
from types import SimpleNamespace
from ga7.request_replay import replay_requests

class CorporateActionTests(unittest.TestCase):
    def test_dividend_cash_and_return(self):
        g=SimpleNamespace(feature_a='x',feature_b='y',threshold_a=0,threshold_b=0,operator='AND',capacity=1,stop_pct=.02,exit_rule='signal_decay',entry_pct=.1,identity=lambda:'test')
        def bar(price,eligible=True,dividend=0,split=0,signal=1):
            return {'open':price,'close':price,'low':price,'eligible':eligible,'dividend':dividend,'split':split,'features':{'x':signal,'y':signal},'sector':'A'}
        sessions=[('1',{'A':bar(100)},False),('2',{'A':bar(100)},False),('3',{'A':bar(99,dividend=1,signal=0)},False),('4',{'A':bar(99,signal=0)},False)]
        result,_=replay_requests(g,sessions,lambda g,b:b['features']['x']>0.5,fee=0,cash_yield=0)
        self.assertEqual(result['trades'],1)
        self.assertAlmostEqual(result['final_nav'],100000,places=5)
    def test_split_adjusted_prices_do_not_double_split(self):
        g=SimpleNamespace(feature_a='x',feature_b='y',threshold_a=0,threshold_b=0,operator='AND',capacity=1,stop_pct=.02,exit_rule='signal_decay',entry_pct=.1,identity=lambda:'test')
        def bar(split=0,signal=1):return {'open':50,'close':50,'low':50,'eligible':True,'dividend':0,'split':split,'features':{'x':signal,'y':signal},'sector':'A'}
        sessions=[('1',{'A':bar()},False),('2',{'A':bar()},False),('3',{'A':bar(split=2,signal=0)},False),('4',{'A':bar(signal=0)},False)]
        result,_=replay_requests(g,sessions,lambda g,b:b['features']['x']>0.5,fee=0,cash_yield=0)
        self.assertAlmostEqual(result['final_nav'],100000,places=5)

if __name__=='__main__':unittest.main()

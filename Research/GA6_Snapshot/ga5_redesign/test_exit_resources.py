from ga5_redesign.exit_objectives import metrics,dominates,pareto_front,calmar
from ga5_redesign.exit_counterfactuals import replay
from ga5_redesign.niche_seeds import initial
def test_exit_metrics_and_pareto():
 trades=[{'entry':100,'exit':110,'net_return':.08,'mfe':.2,'mae':-.04,'sessions':10},{'entry':100,'exit':90,'net_return':-.12,'mfe':.01,'mae':-.2,'sessions':5}]
 m=metrics(trades)
 assert m['count']==2 and m['capture_coverage']==2 and m['tail']==-.12
 assert pareto_front([{'count':1,'expectancy':1,'capture':1,'giveback':1,'adverse':1,'tail':1,'efficiency':1},{'count':1,'expectancy':0,'capture':0,'giveback':0,'adverse':0,'tail':0,'efficiency':0}])==[0]
 assert calmar(.2,-.1)==2
def test_censored_trade_not_fake_exit():
 g=initial('trend')
 assert replay({'price':100},[],g)['status']=='CENSORED'
 assert metrics([])['status']=='INSUFFICIENT_TRADES'

"""Cash-independent, unit-notional shadow trade ledger. Research-only.
Next-open execution, fees, partial sales, split/dividend events, censored positions.
"""
from ga5_chromosome_decisions import PositionState
from ga5_feature_adapter import extract
from fast_decision import evaluate as decide
from ga5_earnings_entry_embargo import entry_allowed

class ShadowBook:
 def __init__(self,genome,fee=.001):
  self.genome=genome;self.fee=fee;self.open={};self.pending={}
  self.closed=[];self.events=[];self.signals=0;self.missing_open=0
  self.fields=(genome.entry_feature,genome.hold_feature,genome.exit_feature,genome.regime_feature,genome.sizing_feature,genome.replace_feature)
 def _event(self,date,ticker,kind,price,quantity,reason):
  self.events.append({'date':date,'ticker':ticker,'kind':kind,'price':price,'quantity':quantity,'reason':reason})
 def start(self,date,opens,blocked,membership,veto,actions=None):
  actions=actions or {}
  # Prices and split ratios must be in the same basis. In split-adjusted data,
  # do not apply splits a second time. Record for audit only.
  for ticker,tr in self.open.items():
   action=actions.get(ticker,{})
   split=float(action.get('stock_splits',0) or 0);div=float(action.get('dividends',0) or 0)
   if split:self._event(date,ticker,'SPLIT_REPORTED',split,0,'split_adjusted_price_basis')
   if div:
    # Dividends supplied on the same price basis as adjusted OHLC.
    cash=tr['shares']*div;tr['dividends']+=cash
    self._event(date,ticker,'DIVIDEND',div,tr['shares'],'ex_date')
  for ticker,(action,signal_date,amount) in list(self.pending.items()):
   del self.pending[ticker]
   if ticker not in opens:self.missing_open+=1;continue
   price=float(opens[ticker])
   if action=='BUY':
    if ticker in self.open or not membership.get((date,ticker),False) or not entry_allowed(ticker,date,blocked) or veto.get(date) is not True or veto.get(signal_date) is not True:continue
    qty=1.;cost=qty*price*(1+self.fee)
    self.open[ticker]={'entry_date':date,'signal_date':signal_date,'entry':price,'peak':price,'sessions':0,'mae':0.,'mfe':0.,'shares':qty,'cost_basis':cost,'realized':0.,'dividends':0.,'invested':cost}
    self._event(date,ticker,'BUY',price,qty,'ENTRY')
   elif ticker in self.open:
    tr=self.open[ticker]
    if action=='SCALE_IN':
     if not membership.get((date,ticker),False) or not entry_allowed(ticker,date,blocked) or veto.get(date) is not True or veto.get(signal_date) is not True:continue
     qty=max(0.,min(float(amount),self.genome.max_weight))*tr['shares']
     if qty<=0:continue
     cost=qty*price*(1+self.fee);tr['entry']=(tr['entry']*tr['shares']+price*qty)/(tr['shares']+qty)
     tr['shares']+=qty;tr['cost_basis']+=cost;tr['invested']+=cost
     self._event(date,ticker,'BUY',price,qty,'SCALE_IN')
    elif action in ('SCALE_OUT','SELL'):
     qty=tr['shares'] if action=='SELL' else min(tr['shares'],max(0.,float(amount))*tr['shares'])
     if qty<=0:continue
     portion=qty/tr['shares'];basis=tr['cost_basis']*portion
     tr['realized']+=qty*price*(1-self.fee)-basis
     tr['cost_basis']-=basis;tr['shares']-=qty
     self._event(date,ticker,'SELL',price,qty,action)
     if tr['shares']<=1e-10:
      self.open.pop(ticker)
      total=tr['realized']+tr['dividends']
      self.closed.append({'ticker':ticker,**tr,'exit_date':date,'exit':price,'net_return':total/tr['invested'],'realized_pnl':total})
 def finish(self,date,rows,closes,blocked,membership,veto):
  for ticker,row in rows.items():
   f=extract(row,self.fields)
   if f is None:continue
   price=float(closes[ticker])
   if ticker in self.open:
    tr=self.open[ticker];tr['sessions']+=1;tr['peak']=max(tr['peak'],price)
    change=price/tr['entry']-1;tr['mae']=min(tr['mae'],change);tr['mfe']=max(tr['mfe'],change)
    action,weight=decide(self.genome,f,PositionState(tr['shares'],tr['entry'],tr['peak'],tr['sessions']),price)
    if action in ('EXIT','REPLACE_CANDIDATE') or veto.get(date) is not True:self.pending[ticker]=('SELL',date,1.)
    elif action in ('SCALE_IN','SCALE_OUT'):self.pending[ticker]=(action,date,weight)
   elif ticker not in self.pending:
    action,_=decide(self.genome,f,PositionState(),price)
    if action=='ENTER' and membership.get((date,ticker),False) and entry_allowed(ticker,date,blocked) and veto.get(date) is True:
     self.pending[ticker]=('BUY',date,1.);self.signals+=1
 def summary(self):
  returns=[t['net_return'] for t in self.closed];n=len(returns)
  return {'eligible_signals':self.signals,'closed_trades':n,'still_open':len(self.open),'missing_next_open':self.missing_open,'events':len(self.events),'success_gt5_rate':sum(x>.05 for x in returns)/n if n else None,'win_rate':sum(x>0 for x in returns)/n if n else None,'mean_net_return':sum(returns)/n if n else None,'median_net_return':sorted(returns)[n//2] if n else None,'trades':self.closed}

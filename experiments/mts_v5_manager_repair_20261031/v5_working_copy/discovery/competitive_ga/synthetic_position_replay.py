"""Native GA6 decisions with next-open fills; research pilot, not parity-certified."""
import json,sqlite3
from collections import Counter
from .synthetic_fiveyear_panel import load_year
from .native_signal_smoke import DB
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from ga6.native_position_decision_adapter import native_action,HeldState
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from .synthetic_matured_selector import MaturedSelector

def run(scenario=1,chromosomes=3,start_session=300,sessions=20):
 frame=load_year(scenario)
 dates=sorted(frame.date.unique())[start_session:start_session+sessions]
 with sqlite3.connect(DB) as db:
  records=db.execute('select id,definition from chromosomes limit ?', (chromosomes,)).fetchall()
 candidates={sid:StructuralCandidate.restore(json.loads(raw)) for sid,raw in records}
 replay=Replay();held={};pending_owner={};counts=Counter();max_observed_weight=0.;breach_sessions=0
 selector=MaturedSelector(min_samples=5);roundtrip={};closed_trades=0
 for i,date in enumerate(dates):
  rows=frame.loc[frame.date==date].set_index('ticker')
  bars={t:Bar(float(r.open),float(r.close)) for t,r in rows.iterrows()}
  prior=len(replay.ledger)
  replay.day(str(date),bars,())
  for _,ticker,side,qty,price,fee in replay.ledger[prior:]:
   if side=='BUY':
    if ticker not in roundtrip:roundtrip[ticker]={'owner':pending_owner[ticker],'cost':0.,'proceeds':0.}
    roundtrip[ticker]['cost']+=qty*price+fee
   else:
    roundtrip[ticker]['proceeds']+=qty*price-fee
   if side=='BUY':
    if ticker not in held:
     if ticker not in pending_owner:raise ValueError('buy without owner')
     held[ticker]=(pending_owner[ticker],HeldState(replay.shares[ticker],price,price,i))
    else:
     sid,s=held[ticker];s.entry_price=(s.entry_price*s.shares+qty*price)/(s.shares+qty);s.shares=replay.shares[ticker]
   elif ticker in held:
    held[ticker][1].shares=replay.shares.get(ticker,0)
    if not held[ticker][1].shares:
     del held[ticker]
     trade=roundtrip.pop(ticker)
     selector.close(i,trade['owner'],trade['proceeds']/trade['cost']-1.)
     closed_trades+=1
  selector.mature(i)
  proposals=[];pending_owner={}
  for ticker,(sid,state) in list(held.items()):
   if ticker not in rows.index:continue
   row=rows.loc[ticker].to_dict();state.peak_price=max(state.peak_price,float(row['close']))
   action,weight=native_action(candidates[sid],row,state,i);counts[action]+=1
   if action=='EXIT':proposals.append(Signal(ticker,'GA6',sid,0))
   elif action=='REDUCE':
    current=replay.shares[ticker]*float(row['close'])/replay.nav[-1][1]
    proposals.append(Signal(ticker,'GA6',sid,current*max(0,min(1,weight))))
   # HOLD/ADD without certified scale-in evidence never manufacture orders.
  for ticker,row in rows.iterrows():
   if ticker in held:continue
   eligible=[]
   for sid,candidate in candidates.items():
    action,weight=native_action(candidate,row.to_dict(),None,i);counts[action]+=1
    if action=='ENTER' and weight>0:eligible.append((sid,weight))
   winner=selector.select(eligible,ticker,i)
   if winner is not None:
    sid,weight=winner
    proposals.append(Signal(ticker,'GA6',sid,min(.10,weight)))
    pending_owner[ticker]=sid
  weights=[qty*float(rows.loc[ticker,'close'])/replay.nav[-1][1] for ticker,qty in replay.shares.items()]
  largest=max(weights,default=0.)
  max_observed_weight=max(max_observed_weight,largest)
  if largest>.10:breach_sessions+=1
  # Organic appreciation is not a sell signal; native EXIT/REDUCE remains authoritative.
  replay.pending=proposals
 nav=[float(row[1]) for row in replay.nav]
 peak=nav[0];drawdown=0.
 for equity in nav:
  peak=max(peak,equity)
  drawdown=max(drawdown,1-equity/peak)
 final_rows=frame.loc[frame.date==dates[-1]].set_index('ticker')
 final_weights={ticker:qty*float(final_rows.loc[ticker,'close'])/nav[-1] for ticker,qty in replay.shares.items()}
 return {'scenario':scenario,'sessions':len(dates),'chromosomes':len(candidates),'actions':dict(counts),
         'fills':len(replay.ledger),'ending_nav':nav[-1],
         'net_return':nav[-1]/100000.-1,'max_drawdown':drawdown,
         'open_positions':len(replay.shares),'largest_position_weight':max(final_weights.values(),default=0.),
         'unexecuted_final_session_signals':len(replay.pending),
         'max_observed_position_weight':max_observed_weight,
         'close_sessions_with_cap_breach':breach_sessions,
         'organic_growth_trims':0,
         'closed_roundtrips':closed_trades,'matured_outcomes_by_chromosome':{k:len(v) for k,v in selector.outcomes.items()},
         'limitations':'pilot; no crash defense, earnings embargo, calibrated selector, or production accounting parity'}

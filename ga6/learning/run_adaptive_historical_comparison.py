"""Actual-market pilot: past-only chromosome choice, one shared cash account.

Limitations: reference signals are from independently capitalized positions.
Entry signals are from independent references; exits are computed on actual held positions and
defense. This is a real execution pilot, NOT full adaptive policy certification.
"""
import sys,json
from pathlib import Path
from collections import defaultdict
sys.path[:0]=["/opt/mts","/opt/mts/ga5_redesign","/opt/mts/ga6/github_validation_20261023/checkout"]
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_chromosome_contract import Genome
from ga5_earnings_entry_embargo import entry_allowed
from ga6.structural_independent_v2_20261022 import structural_portfolio_evaluator as evaluator
from ga6.learning.reference_decision_capture import evaluate_with_decision_trace
from ga6.learning.reference_fill_capture import run_reference_with_fills
from ga6.learning.shared_capital_replay import replay_orders
from ga6.learning.portfolio_assessment import assess_shared_portfolio
from settlement_ledger import SettledLedger
from mts_next_open_ledger_v1 import Order

root=Path("/opt/mts/ga5_redesign")
frame=pd.read_parquet(root/"exploratory79_ga4_enriched.parquet")
frame=frame[(frame.date>="2025-01-02")&(frame.date<"2025-07-01")]
prepared=PreparedSessions(frame)
raw=json.loads((root/"exploratory79_policy.json").read_text())
state=json.loads(Path("/opt/mts/ga6/runs/ga6_production_v1/checkpoint_unified.json").read_text())
# First two distinct valid chromosomes, frozen before observing comparison outcomes.
genomes=[]
for d in state["members"]:
 try:g=Genome(**d)
 except (TypeError,ValueError):continue
 if g.valid() and all(g!=x for x in genomes):genomes.append(g)
 if len(genomes)==2:break
assert len(genomes)==2
blocked={t:frozenset(v) for t,v in raw["blocked"].items()}
membership={(d,t):v for d,t,v in raw["membership"] if d in prepared.dates}
veto={d:v for d,v in raw["risk_veto"].items() if d in prepared.dates}
kwargs=dict(blocked=blocked,membership=membership,risk_veto=veto,
 annual_cash_yield=raw["cash_proxy_annual_yield"],niche_labels=None)
signals={};matured=defaultdict(list);count={}
for k,g in enumerate(genomes):
 r=evaluate_with_decision_trace(evaluator,prepared,g,**kwargs)
 signals[str(k)]=r["decision_signals"]
 f=run_reference_with_fills(evaluator,prepared,g,**kwargs)["fills"]
 # Only fully round-trip long positions, with realized gross execution P&L
 # net of fees. Labels become available only AFTER the closing session.
 inventory=defaultdict(int);basis=defaultdict(float)
 for fill in f:
  s=fill["security"];q=fill["quantity"];notional=q*fill["price"];fee=fill["fee"]
  if fill["side"]=="BUY":
   inventory[s]+=q;basis[s]+=notional+fee
  else:
   held=inventory[s];assert held>=q>0
   cost=basis[s]*q/held
   inventory[s]-=q;basis[s]-=cost
   if inventory[s]==0:basis.pop(s,None)
   ret=(notional-fee-cost)/cost
   matured[str(k)].append((fill["execution_date"],ret))
 count[str(k)]=len(matured[str(k)])
sessions=[(ds,opens,closes) for ds,_,opens,closes in prepared.sessions]
allowed={(ds,s):entry_allowed(s,ds,blocked) for ds,rows,_,_ in prepared.sessions for s in rows}
actions={}
for k,items in signals.items():
 for item in items:
  if item["action"]=="ENTER" and item["position"]["shares"]==0:
   actions.setdefault((item["decision_date"],item["symbol"]),[]).append((k,item))
dates=sorted(prepared.dates)
adaptive=defaultdict(list);fixed=defaultdict(list);selection_counts=defaultdict(int)
for (day,symbol),candidates in sorted(actions.items()):
 # Cold-start deterministic control; maturity is STRICTLY BEFORE decision day.
 score={}
 for k,_ in candidates:
  samples=[ret for close,ret in matured[k] if close<day]
  if len(samples)>=3:
   score[k]=(sum(samples)/(len(samples)+10),len(samples))
 chosen=max(candidates,key=lambda pair:(score.get(pair[0],(-1e9,0))[0],-int(pair[0])))
 # Flat-state ENTER only; no reusing independent portfolio position exits.
 for target,pair in ((adaptive,chosen),(fixed,next((x for x in candidates if x[0]=="0"),None))):
  if pair is None:continue
  k,item=pair
  target[day].append(dict(symbol=symbol,chromosome=k,action="ENTER",
     weight=min(.03,float(item["weight"])),evidence_cutoff=day))
 if chosen[0] in score:selection_counts["matured"]+=1
 else:selection_counts["cold_start"]+=1
def execute(proposals, provider=None):
 return replay_orders(sessions,proposals,starting_cash=100000,fee=.001,
   annual_cash_yield=raw["cash_proxy_annual_yield"],ledger_class=SettledLedger, decision_provider=provider,
   order_class=Order,max_positions=10,max_hold=40,membership=membership,
   earnings_allowed=allowed,risk_veto=veto,corporate_actions={
    ds:[(t,float(r.get("stock_splits",0)),float(r.get("dividends",0)))
        for t,r in rows.items() if r.get("stock_splits",0) or r.get("dividends",0)]
    for ds,rows,_,_ in prepared.sessions})
# Stateful decisions are generated at each actual shared-account close.
# Reference features are immutable PIT; position-specific signal recomputed
# from actual shared portfolio holdings, never reference shadow position state.
feature_index={k:{(x["decision_date"],x["symbol"]):x for x in v} for k,v in signals.items()}
def provider_factory(mode):
 def provider(day, closes, owners, holdings, entered, session_index):
  picks=adaptive if mode=="adaptive" else fixed
  requested={p["symbol"]:p for p in picks.get(day,[])}
  proposals=[]
  for symbol,k in owners.items():
   snapshot=feature_index[k].get((day,symbol))
   if snapshot is None:continue
   # Preserve ownership; never assign an existing position to a new chromosome.
   # Exit/hold decisions are based on actual position age and market close.
   held=session_index-entered[symbol]
   action="EXIT" if held>=39 else "HOLD"
   proposals.append(dict(symbol=symbol,chromosome=k,action=action,weight=1,
                         evidence_cutoff=day))
  for symbol,p in requested.items():
   if symbol not in owners:proposals.append(p)
  return proposals
 return provider
a=execute({},provider_factory("adaptive"));b=execute({},provider_factory("fixed"))
def stats(x):
 p=assess_shared_portfolio(x["nav"],starting_cash=100000)
 return dict(final_nav=x["final_nav"],fills=len(x["fills"]),rejections=len(x["rejections"]),portfolio=p)
out=dict(scope="actual historical prices; stateful held-position HOLD/EXIT and entry ranking; NOT full genome-driven EXIT/SCALE parity",
  dates=[dates[0],dates[-1]],chromosomes=2,matured_reference_exit_counts=count,
  selection_counts=dict(selection_counts),adaptive=stats(a),fixed=stats(b))
destination=Path("/opt/mts/ga6/runs/ga6_shared_adaptive_pilot_20261023")
destination.mkdir(parents=True,exist_ok=True)
(destination/"RESULT.json").write_text(json.dumps(out,indent=2,default=str))
print(json.dumps(out,indent=2,default=str))

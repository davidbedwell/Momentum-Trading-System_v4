"""Actual Jan-Mar 2025 frozen-evaluator fill and daily-NAV ledger replay."""
import json,sys,hashlib
from pathlib import Path
sys.path[:0]=["/opt/mts","/opt/mts/ga5_redesign",
              "/opt/mts/ga6/github_validation_20261023/checkout"]
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_chromosome_contract import Genome
from ga6.structural_independent_v2_20261022 import structural_portfolio_evaluator as evaluator
from ga6.learning.reference_fill_capture import run_reference_with_fills
from ga6.learning.historical_fill_parity import replay_captured_reference
from settlement_ledger import SettledLedger
from mts_next_open_ledger_v1 import Order
root=Path("/opt/mts/ga5_redesign")
source=root/"exploratory79_ga4_enriched.parquet"
policy_path=root/"exploratory79_policy.json"
frame=pd.read_parquet(source)
frame=frame[(frame.date>="2025-01-02")&(frame.date<"2025-04-01")]
prepared=PreparedSessions(frame)
policy=json.loads(policy_path.read_text())
state=json.loads(Path("/opt/mts/ga6/runs/ga6_production_v1/checkpoint_unified.json").read_text())
genome=Genome(**state["members"][0])
kwargs=dict(blocked={t:frozenset(v) for t,v in policy["blocked"].items()},
 membership={(d,t):v for d,t,v in policy["membership"] if d in prepared.dates},
 risk_veto={d:v for d,v in policy["risk_veto"].items() if d in prepared.dates},
 annual_cash_yield=policy["cash_proxy_annual_yield"],niche_labels=None)
reference=run_reference_with_fills(evaluator,prepared,genome,**kwargs)
parity=replay_captured_reference(reference,prepared,starting_cash=100000,
 fee=.001,annual_cash_yield=policy["cash_proxy_annual_yield"],
 ledger_class=SettledLedger,order_class=Order)
out=dict(parity=parity,reference_final_nav=reference["metrics"]["final_nav"],
 reference_cagr=reference["metrics"]["cagr_diagnostic"],
 reference_mdd=reference["metrics"]["mdd_diagnostic"],
 dataset_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 policy_sha256=hashlib.sha256(policy_path.read_bytes()).hexdigest(),
 start="2025-01-02",end="2025-03-31",chromosome=state["members"][0],
 scope="actual market OHLCV; frozen evaluator fills; independent ledger replay; NOT decision policy parity")
dest=Path("/opt/mts/ga6/runs/ga6_historical_shared_parity_20261023")
dest.mkdir(exist_ok=True,parents=True)
(dest/"RESULT.json").write_text(json.dumps(out,indent=2,default=str))
print(json.dumps({k:v for k,v in out.items() if k!="chromosome"},indent=2),flush=True)

"""Isolated exploratory risk-ablation pilot; does not alter GA9 production risk gate."""
import argparse,json
from pathlib import Path
from . import risk,execution,objective,exploratory

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--seconds',type=float,default=45);p.add_argument('--evaluations',type=int,default=24);a=p.parse_args()
 # Ablate 8% feasibility without changing original production semantics.
 risk.MAX_DRAWDOWN=1.0;execution.MAX_DRAWDOWN=1.0;objective.MAX_DRAWDOWN=1.0
 execution.risk_feasible=lambda m: 0<=m<=1.0
 objective.risk_feasible=lambda m: 0<=m<=1.0
 report=exploratory.experiment(a.output,'real',seconds=a.seconds,evaluations=a.evaluations,repair='edge_units_v2')
 report['risk_experiment']='8_percent_hard_gate_disabled_for_exploratory_comparison_only'
 report['external_reference_mdd']=.08
 Path(a.output,'relaxed_risk_summary.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:report.get(k) for k in ('evaluations','generations','total_fills','positive_forecasts','target_met','stop_reason','risk_experiment')}))
if __name__=='__main__':main()

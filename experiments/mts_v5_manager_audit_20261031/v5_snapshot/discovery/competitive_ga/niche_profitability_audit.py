"""GA7 archive group profitability; NOT exhaustive daily manager opportunity attribution."""
import json
from pathlib import Path
import pandas as pd
ROOT=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518')
SRC=ROOT/'ga7_all_full_dev79_capacity79_causal_v2_2009_2018.csv'
OUT=Path('/opt/mts/synthetic-market-lab/reports/ga7_niche_vs_non_niche_profitability.json')
def run():
 x=pd.read_csv(SRC)
 x=x[x.status=='OK'].copy()
 x['category']=x.group.map(lambda g:'NON_NICHE' if g=='NON_NICHE' else 'NICHE')
 result={}
 for name,g in x.groupby('category'):
  p=g[(g.trades>0)&(g.final_nav>100000)]
  result[name]={'chromosomes_evaluated':len(g),'chromosomes_with_trades':int((g.trades>0).sum()),'profitable_chromosomes':len(p),'profitable_fraction_of_evaluated':round(len(p)/len(g),4),'median_cagr_pct':round(float(g.cagr.median()*100),3),'median_mdd_pct':round(float(g.mdd.median()*100),3),'median_calmar':round(float(g.calmar.median()),3),'total_trades_across_independent_replays':int(g.trades.sum()),'positive_conservative_ev_r':int((g.conservative_ev_r>0).sum()),'median_final_nav':round(float(g.final_nav.median()),2)}
 report={'scope':'GA7 independent chromosome portfolio replays, DEV79 2009-2018, not 2020 manager competition','source':str(SRC),'definition_of_profitable':'at least one trade and ending NAV above initial 100000 in independent replay','groups':result,'limitations':['Chromosome profitability is NOT the number of distinct actionable stock opportunities','Same ticker/date opportunities can duplicate across chromosomes','Each chromosome independently replays capital; totals cannot be combined into a shared portfolio','Not a prospective out-of-sample result; causal v2 execution parity not certified','GA6, GA4, HORIZONS excluded; DEV87 untouched']}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':print(json.dumps(run(),indent=2))

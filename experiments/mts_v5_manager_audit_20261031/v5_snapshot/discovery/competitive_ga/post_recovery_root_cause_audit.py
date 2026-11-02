"""Research-only causal breakdown of the 2020 post-recovery manager failure."""
import csv,json,sqlite3
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np,pandas as pd
from discovery.competitive_ga.ga6_native_position_replay import run
from discovery.competitive_ga.chronological_shadow_feed import ShadowFeed
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS,PRICES
from discovery.competitive_ga.manager_policy_v2 import Genes

OUT=Path('/opt/mts/synthetic-market-lab/reports/post_recovery_root_cause_2020.json')
INV=Path('/opt/mts/ga6/runs/selector_learning_fourfold_20261025/engineering_candidate_inventory_NOT_PROSPECTIVE.csv')
def audit():
    _,fills=run(output='ATTRIBUTED')
    feed=ShadowFeed(fills)
    signals=pd.read_csv(SIGNALS)
    dates=sorted(pd.to_datetime(pd.read_parquet(PRICES,columns=['date']).query("'2020-01-01' <= date <= '2020-12-31'").date).dt.strftime('%Y-%m-%d').unique())
    byday=dict(tuple(signals.groupby('signal_date')))
    counts=Counter();by_month=defaultdict(Counter);chrom=defaultdict(Counter)
    g=Genes()
    for i,day in enumerate(dates):
        matured=feed.advance(i)
        if day<'2020-05-28':continue
        bucket=by_month[day[:7]]
        for o in matured:
            bucket['realized_outcomes']+=1
            if o.net_r>0:bucket['positive_outcomes']+=1
        if day not in byday:continue
        for r in byday[day].itertuples():
            bucket['signal_rows']+=1
            cal=feed.estimate(r.chromosome_id,i)
            if cal is None:
                bucket['uncalibrated']+=1;chrom[r.chromosome_id]['uncalibrated']+=1
                continue
            bucket['calibrated']+=1
            score=cal['edge']-g.risk_penalty*max(0,cal['downside'])
            if cal['edge']>=g.min_edge:bucket['raw_edge_pass']+=1
            if score>=g.min_edge:bucket['score_pass']+=1
            else:bucket['score_fail']+=1
            chrom[r.chromosome_id]['calibrated']+=1
            if score>=g.min_edge:chrom[r.chromosome_id]['score_pass']+=1
    outcomes=[{'chromosome_id':o.chromosome_id,'maturity_date':dates[o.maturity_session],
               'net_r':round(o.net_r,6)} for o in feed.calibrator.outcomes]
    after=[o for o in outcomes if o['maturity_date']>='2020-05-28']
    inv=pd.read_csv(INV)
    selected=set(signals.chromosome_id.unique())
    catalogue=sqlite3.connect('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite')
    catalogue_count=catalogue.execute('select count(*) from chromosomes').fetchone()[0]
    result={'status':'DIAGNOSTIC_NOT_PIT_CERTIFIED','window':['2020-05-28','2020-12-31'],
      'catalogue_records':catalogue_count,'engineering_candidate_ids':int(inv.chromosome_id.nunique()),
      'signal_feed_chromosome_ids':len(selected),
      'feed_ids_in_candidate_inventory':len(selected & set(inv.chromosome_id)),
      'by_month':{k:dict(v) for k,v in sorted(by_month.items())},
      'by_chromosome':{k:dict(v) for k,v in chrom.items()},
      'post_recovery_realized_outcomes':len(after),
      'post_recovery_positive_realized_outcomes':sum(o['net_r']>0 for o in after),
      'post_recovery_mean_realized_lot_return':round(float(np.mean([o['net_r'] for o in after])),6) if after else None,
      'post_recovery_outcomes':after,
      'limitations':['Only three sampled GA6 chromosomes','Lot-level realized returns are not independent trade samples','Historical inventory selection is not out-of-sample','Not a portfolio replay of broader library','No PIT or evaluator parity certification']}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+'\n')
    return {k:v for k,v in result.items() if k!='post_recovery_outcomes'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))

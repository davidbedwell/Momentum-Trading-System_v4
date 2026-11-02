"""Same inventory-status diagnostics; no additional replay or selector."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
import itertools
import numpy as np
import pandas as pd
from study import MODES,OUT,CATS

def main():
    cols=['date','ticker','segment','category','valid','q0','delta','incremental_nav']
    frames={m:pd.read_csv(OUT/f'{m}_opportunity_ledger.csv.gz',usecols=cols,parse_dates=['date']).set_index(['date','ticker']) for m in MODES}
    base=frames[MODES[0]];flat=np.logical_and.reduce([x.q0.lt(1e-9) for x in frames.values()]);held=np.logical_and.reduce([x.q0.gt(1e-9) for x in frames.values()]);rows=[];rng=np.random.default_rng(7901)
    for seg in ['discovery','test']:
        calendar=base.index.get_level_values('date')[base.segment==seg].unique();codes=calendar.to_period('M').factorize()[0];n=codes.max()+1;counts=np.bincount(codes);draws=rng.integers(0,n,(2000,n))
        for state,condition in [('all_four_flat',flat),('all_four_held',held)]:
            for cat in CATS:
                mask=base.valid&base.segment.eq(seg)&base.category.eq(cat)&condition
                for a,b in itertools.combinations(MODES,2):
                    z=(frames[a].incremental_nav-frames[b].incremental_nav).where(mask,0).groupby(level='date').sum().reindex(calendar,fill_value=0)
                    boot=np.bincount(codes,weights=z.to_numpy())[draws].sum(axis=1)/counts[draws].sum(axis=1)
                    dis=mask&(np.sign(frames[a].delta)!=np.sign(frames[b].delta));num=int(dis.sum());months=base.index.get_level_values('date')[dis].to_period('M').nunique()
                    lo,hi=np.quantile(boot,[.025,.975])
                    rows.append(dict(segment=seg,stratum=state,category=cat,a=a,b=b,matched=int(mask.sum()),discordant_actions=num,discordant_months=months,mean_daily_bps=z.mean()*1e4,ci95_low_bps=lo*1e4,ci95_high_bps=hi*1e4,status='descriptive_path_confounded' if num>=100 and months>=24 else 'inconclusive_insufficient_comparable_actions'))
    pd.DataFrame(rows).to_csv(OUT/'inventory_stratum_contrasts.csv',index=False)
    summary=pd.read_csv(OUT/'category_summary.csv')
    summary['opportunity_cost_against_hold_dollars']=-summary.incremental_pnl
    summary.to_csv(OUT/'opportunity_cost_summary.csv',index=False)
if __name__=='__main__':main()

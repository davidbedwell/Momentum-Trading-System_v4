import pandas as pd,numpy as np,json
from pathlib import Path
root=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019')
x=pd.read_parquet(root/'all13_niche_screen/eligible_chromosomes.parquet')
out=root/'all13_niche_screen'/'all13_fitness_firstwave'
out.mkdir(exist_ok=True)
rows=[]
for niche,g in x.groupby('niche'):
 g=g.copy();g['abs_mdd']=g.mdd.abs()
 g['calmar']=g.cagr/g.abs_mdd.replace(0,np.nan)
 g['fitness_rank']=g.fitness.rank(pct=True)
 g['calmar_rank']=g.calmar.rank(pct=True)
 g['cagr_rank']=g.cagr.rank(pct=True)
 g['mdd_rank']=(-g.abs_mdd).rank(pct=True)
 g['fitness_minus_calmar_rank']=g.fitness_rank-g.calmar_rank
 g.sort_values('fitness',ascending=False).head(25).to_csv(out/(niche+'_top25_fitness.csv'),index=False)
 g.sort_values('calmar',ascending=False).head(25).to_csv(out/(niche+'_top25_calmar.csv'),index=False)
 rows.append(dict(niche=niche,chromosomes=len(g),unique_fitness=g.fitness.nunique(),unique_cagr=g.cagr.nunique(),median_cagr=float(g.cagr.median()),median_mdd=float(g.abs_mdd.median()),best_cagr=float(g.cagr.max()),lowest_mdd=float(g.abs_mdd.min()),median_calmar=float(g.calmar.median()),fitness_cagr_spearman=float(g.fitness.corr(g.cagr,method='spearman')),fitness_mdd_spearman=float(g.fitness.corr(g.abs_mdd,method='spearman')),fitness_calmar_spearman=float(g.fitness.corr(g.calmar,method='spearman')),top_fitness_id=str(g.sort_values('fitness',ascending=False).iloc[0].id),top_calmar_id=str(g.sort_values('calmar',ascending=False).iloc[0].id)))
report=pd.DataFrame(rows).sort_values('niche')
report.to_csv(out/'all13_niche_fitness_diagnostic.csv',index=False)
(root/'all13_niche_screen'/'all13_fitness_firstwave'/'README.txt').write_text('First-wave all-13 fitness diagnostic on existing eligibility evaluations. NOT trajectory-level A/B/C classification, not counterfactual portfolio replay, not out-of-sample certification. Chromosomes remain niche-specific.\n')
print(report[['niche','chromosomes','unique_fitness','median_cagr','median_mdd','fitness_cagr_spearman','fitness_mdd_spearman','fitness_calmar_spearman']].to_string(index=False),flush=True)
print('OUTPUT',out,flush=True)

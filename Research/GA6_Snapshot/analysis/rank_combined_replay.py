import pandas as pd,numpy as np
from pathlib import Path
p=Path('/opt/mts/ga6_h/audits');d=pd.read_csv(p/'GA6v3_global_chromosome_pareto_leaderboard.csv');c='DEV79_DEV87';groups=['DEV79','DEV87','DEV50b',c]
# Rank directly by observed shared-capital replay CAGR, not an average of constituent CAGRs.
d['combined_cagr_rank']=d[c+'__cagr'].rank(method='min',ascending=False).astype(int)
d['combined_positive_ev']=d[c+'__net_ev']>0
d['three_cohort_positive_lcb']=np.logical_and.reduce([d[x+'__ev_lcb']>0 for x in groups[:3]])
d['combined_cagr_vs_constituent_mean_pp']=100*(d[c+'__cagr']-d[['DEV79__cagr','DEV87__cagr']].mean(axis=1))
metrics=['cagr','mdd','net_ev','ev_lcb','win_rate','trades','avg_sessions','avg_invested_weight'];cols=['combined_cagr_rank','index','identity','niche','duplicate_group_size','pareto_front','three_cohort_positive_lcb']+[x+'__'+m for x in groups for m in metrics]+['combined_cagr_vs_constituent_mean_pp']
d.sort_values(['combined_cagr_rank','DEV79_DEV87__net_ev'],ascending=[True,False])[cols].to_csv(p/'GA6v3_400_ranked_combined_165_with_individual_tests.csv',index=False)
print('TOP 20 BY COMBINED SHARED CAPITAL CAGR');print(d.sort_values(c+'__cagr',ascending=False)[['index','niche',c+'__cagr',c+'__mdd',c+'__net_ev','DEV79__cagr','DEV87__cagr','DEV50b__cagr','three_cohort_positive_lcb','duplicate_group_size']].head(20).to_string(index=False,float_format=lambda x:f'{x:.4f}'))
print('combined >=35%',int((d[c+'__cagr']>=.35).sum()),'combined >=35 and positive three LCB',int(((d[c+'__cagr']>=.35)&d.three_cohort_positive_lcb).sum()))

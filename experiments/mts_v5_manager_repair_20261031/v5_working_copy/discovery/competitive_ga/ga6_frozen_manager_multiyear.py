"""Frozen 2020-selected exit rule, independently replayed across other years.

Each year starts with $100k and empty holdings. The selected rule is never
retuned using evaluation-year outcomes. Research only; not PIT certified.
"""
import json
from pathlib import Path
from discovery.competitive_ga.ga6_native_position_replay import run
OUT=Path('/opt/mts/synthetic-market-lab/reports/ga6_frozen_manager_multiyear_20261027.json')
def selected(age,row,state):
    return age>=20 and float(row['close'])/state.entry_price-1<=.10
def main():
    rows=[]
    for year in (2017,2018,2019,2021,2022,2023,2024,2025):
        variants={}
        for label,kw in [('native',{}),('fixed40',{'max_hold':40}),('frozen_manager',{'manager':selected})]:
            result=run(start_date=f'{year}-01-01',end_date=f'{year}-12-31',output=False,**kw)
            variants[label]={k:result[k] for k in ('sessions','net_return','max_drawdown','fills')}
        rows.append({'year':year,**variants,'frozen_minus_native_pp':round(100*(variants['frozen_manager']['net_return']-variants['native']['net_return']),3),
                     'frozen_minus_fixed40_pp':round(100*(variants['frozen_manager']['net_return']-variants['fixed40']['net_return']),3)})
        print(json.dumps(rows[-1]),flush=True)
        OUT.write_text(json.dumps({'status':'IN_PROGRESS','years_completed':len(rows),'rows':rows},indent=2))
    wins=sum(r['frozen_minus_native_pp']>0 for r in rows)
    output={'status':'COMPLETED_RESEARCH_NOT_CERTIFIED','frozen_rule':'age >= 20 and unrealized_return <= 0.10',
            'training_year':2020,'evaluation_years':[r['year'] for r in rows],
            'wins_vs_native':wins,'years_tested':len(rows),'rows':rows,
            'limitations':'Years are reset to empty holdings; no interyear continuity, PIT certification, GA6 original ledger parity, earnings embargo or GA7. The rule was selected using 2020 data; earlier years are retrospective robustness checks, not prospective holdout.'}
    OUT.write_text(json.dumps(output,indent=2))
    print(json.dumps({'status':output['status'],'wins_vs_native':wins,'years_tested':len(rows)},indent=2))
if __name__=='__main__':main()

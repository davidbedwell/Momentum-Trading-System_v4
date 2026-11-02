"""Exploratory conditional manager: train-only search, chronological holdout.

Rules use contemporaneous position profit and age. No future information enters
the rule. This is a finite candidate search, NOT a genetic algorithm.
"""
import json
from pathlib import Path
from discovery.competitive_ga.ga6_native_position_replay import run
OUT=Path('/opt/mts/synthetic-market-lab/reports/ga6_conditional_manager_2020.json')
def make_manager(age_cutoff,profit_cutoff):
    def manager(age,row,state):
        profit=float(row['close'])/state.entry_price-1
        return age>=age_cutoff and profit<=profit_cutoff
    return manager
def at(replay,date):
    return next(v[1] for v in replay.nav if v[0]==date)
def main():
    rows=[]
    for age in (20,40,60,80):
        for profit in (-.05,0.,.05,.10):
            result,replay,_=run(manager=make_manager(age,profit),output=False,return_trace=True)
            start=at(replay,'2020-01-02')
            train=at(replay,'2020-09-30')
            end=at(replay,'2020-12-31')
            rows.append({'age':age,'profit_cutoff':profit,'train_return':round(train/start-1,6),
                         'test_return':round(end/train-1,6),'full_return':result['net_return'],
                         'full_mdd':result['max_drawdown'],'manager_exits':result['native_action_counts'].get('MANAGER_EXIT',0)})
    best=max(rows,key=lambda r:r['train_return'])
    output={'status':'EXPLORATORY_NOT_CERTIFIED',
            'rule':'Exit only if holding age >= threshold AND unrealized return <= profit cutoff',
            'training':'Jan-Sep 2020','holdout':'Oct-Dec 2020','candidates':rows,
            'selected_training_rule':best,
            'limitations':'Only 3 frozen GA6 chromosomes and 2020 data. This is grid search, not evolutionary GA. Inherited holdings confound test comparison; no PIT or evaluator parity certification.'}
    OUT.write_text(json.dumps(output,indent=2))
    print(json.dumps({'selected_training_rule':best,'top_five_training':sorted(rows,key=lambda r:r['train_return'],reverse=True)[:5]},indent=2))
if __name__=='__main__':main()

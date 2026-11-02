"""Causal chronological trade-management search; exploratory only.

Train on Jan-Sep 2020, freeze a simple policy, test Oct-Dec 2020.
No post-hoc tuning against the test window.
"""
import json
from pathlib import Path
from discovery.competitive_ga.ga6_native_position_replay import run
OUT=Path('/opt/mts/synthetic-market-lab/reports/ga6_trade_manager_2020_exploratory.json')
def policy(age,row,state,threshold=40):
    # Deliberately simple benchmark candidate; no future data used in decisions.
    return age>=threshold
def nav_at(replay,date):
    return next(float(v[1]) for v in replay.nav if v[0]==date)
def main():
    # All candidates start from identical initial conditions.
    # Only pre-cutoff NAV is used to choose the candidate.
    candidates=[None,20,30,40,50,60,80]
    runs=[]
    for threshold in candidates:
        manager=(lambda age,row,state,t=threshold: policy(age,row,state,t)) if threshold is not None else None
        result,replay,_=run(output=False,return_trace=True,manager=manager)
        nav0=nav_at(replay,'2020-01-02')
        train_end=nav_at(replay,'2020-09-30')
        test_end=nav_at(replay,'2020-12-31')
        runs.append({'threshold':threshold,'train_nav':round(train_end,2),
                     'train_return':round(train_end/nav0-1,6),
                     'test_return':round(test_end/train_end-1,6),
                     'full_return':result['net_return'],
                     'full_mdd':result['max_drawdown']})
    winner=max(runs,key=lambda r:r['train_return'])
    baseline=next(r for r in runs if r['threshold'] is None)
    result={'status':'EXPLORATORY_NOT_CERTIFIED',
            'method':'Select threshold using Jan-Sep NAV only; inspect untouched Oct-Dec NAV segment. Test return uses portfolios accumulated through training, not reset.',
            'candidate_results':runs,'selected_from_training':winner['threshold'],
            'selected_test_return':winner['test_return'],
            'no_override_test_return':baseline['test_return'],
            'test_excess_return':round(winner['test_return']-baseline['test_return'],6),
            'limitations':'Single 2020 path, three GA6 chromosomes, in-sample training period, no independent historical proof, no GA7, no execution parity, and thresholds alone are not a genetic algorithm.'}
    OUT.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

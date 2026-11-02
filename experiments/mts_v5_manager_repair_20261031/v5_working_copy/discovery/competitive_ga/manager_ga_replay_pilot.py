"""Bounded research-only evolution using observed GA6 native replay fitness.
This evolves an exit override only; it is NOT multi-family manager GA.
"""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from .manager_evolution_v1 import population,offspring,identity
from .manager_replay_fitness import evaluate


def run(*,size=4,generations=2,start_date='2020-01-01',end_date='2020-01-31',seed=7,evaluator=evaluate):
    if not 2<=size<=16 or not 1<=generations<=5:
        raise ValueError('research pilot bounded to 2-16 genomes and 1-5 generations')
    if start_date>end_date:raise ValueError('invalid chronological range')
    genomes=population(size,seed=seed)
    history=[]
    for generation in range(generations):
        scored=[];records=[]
        for g in genomes:
            replay,fitness=evaluator(g,start_date=start_date,end_date=end_date)
            if len(fitness)!=2:raise ValueError('pilot requires two observed replay objectives')
            scored.append((g,fitness))
            records.append({'genome':identity(g),'fitness':list(fitness),
                            'fills':replay['fills'],'sessions':replay['sessions'],
                            'native_action_counts':replay.get('native_action_counts',{})})
        history.append({'generation':generation,'evaluations':records})
        if generation+1<generations:
            genomes=offspring(scored,n=size,seed=seed+generation+1)
    return {'status':'RESEARCH_ONLY_GA6_ENTRY_CAP_AND_EXIT_OVERRIDE','window':[start_date,end_date],
            'size':size,'generations':generations,'history':history,
            'limitations':['GA6-only three preselected chromosomes',
                           'manager genome controls initial entry cap and conditional exit override',
                           'other manager genes not wired to replay',
                           'no native parity or PIT certification','not multi-family manager GA']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--size',type=int,default=4)
    parser.add_argument('--generations',type=int,default=2)
    parser.add_argument('--start-date',default='2020-01-01')
    parser.add_argument('--end-date',default='2020-01-31')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run(size=args.size,generations=args.generations,
               start_date=args.start_date,end_date=args.end_date)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__':main()

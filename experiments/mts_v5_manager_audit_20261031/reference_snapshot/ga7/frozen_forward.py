"""Standalone GA7 forward evidence after evolution stops; never feeds breeding."""
import argparse,hashlib,json
from pathlib import Path
from ga7.engine import Genome
from ga7.fold_promotion import freeze_cohort,forward_evidence
from ga7.ga7_folds import expanding_walk_forward
from ga7.runner import init_worker,passes


def read_final_generation(run_dir):
    paths=sorted(Path(run_dir).glob('generation_*.jsonl'))
    if not paths: raise ValueError('No completed generation to freeze')
    rows={}
    for line in paths[-1].read_text().splitlines():
        obj=json.loads(line)
        rows.setdefault(obj['group'],[]).append((Genome(**obj['genome']),obj['metrics']))
    if not rows: raise ValueError('Empty generation')
    return rows,paths[-1]


def run_forward(run_dir,output,fold_plan,data,tape,policy,per_group=8):
    import ga7.runner as runner
    run_dir=Path(run_dir);output=Path(output)
    if output.exists(): raise FileExistsError('Forward output already exists; immutable evidence')
    rows,source=read_final_generation(run_dir)
    cohort=freeze_cohort(rows,per_group)
    plan=json.loads(Path(fold_plan).read_text())
    init_worker(str(data),str(tape),str(policy))
    sessions=runner.SESSIONS
    windows=plan['chronological_folds']
    results=[]
    for group,chromosomes in sorted(cohort['chromosomes'].items()):
        for item in chromosomes:
            genome=Genome(**item)
            summary,detail=forward_evidence(genome,group,sessions,windows,plan['stock_folds'],passes)
            results.append({'group':group,'genome_id':genome.identity(),'summary':summary,'fold_results':detail})
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    report={'schema':'ga7-forward-evidence-v1','purpose':'independent frozen evaluation; no optimizer feedback',
            'source_generation':source.name,'source_sha256':source_hash,'cohort':cohort,
            'fold_plan_sha256':hashlib.sha256(Path(fold_plan).read_bytes()).hexdigest(),
            'status':'FORWARD_EVIDENCE_NOT_PORTFOLIO_CERTIFICATION','results':results}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f:json.dump(report,f,indent=2)
    return report

def main():
    p=argparse.ArgumentParser()
    for arg in ('run-dir','output','fold-plan','data','tape','policy'):p.add_argument('--'+arg,required=True)
    p.add_argument('--per-group',type=int,default=8)
    a=p.parse_args()
    r=run_forward(a.run_dir,a.output,a.fold_plan,a.data,a.tape,a.policy,a.per_group)
    print(json.dumps({'status':r['status'],'cohort_hash':r['cohort']['sha256'],'results':len(r['results'])}))
if __name__=='__main__':main()

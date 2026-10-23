"""Chronological train/validation/test protocol. No chromosome fitting on test."""
import argparse,json,sys
from pathlib import Path
from dataclasses import asdict
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from ga5_chromosome_contract import Genome
from guarded_evaluator import PreparedSessions,evaluate
from optimizer_v3 import fitness
from exit_objectives import pareto_front

def partition(frame,train_end,validation_end):
 if not train_end<validation_end:raise ValueError('Chronological boundaries must increase')
 d=frame.copy();d['date']=pd.to_datetime(d.date)
 a=d[d.date<pd.Timestamp(train_end)]
 b=d[(d.date>=pd.Timestamp(train_end))&(d.date<pd.Timestamp(validation_end))]
 c=d[d.date>=pd.Timestamp(validation_end)]
 if min(len(a),len(b),len(c))==0:raise ValueError('Empty chronological fold')
 assert a.date.max()<b.date.min()<c.date.min()
 return a,b,c

def run(argv=None):
 p=argparse.ArgumentParser()
 for name in ('features','policy-file','genomes','output','train-end','validation-end'):p.add_argument('--'+name,required=True)
 p.add_argument('--diagnostic-only',action='store_true')
 args=p.parse_args(argv)
 if not args.diagnostic_only:raise ValueError('Diagnostic only')
 source=Path(args.features)
 manifest=json.loads(source.with_suffix('.manifest.json').read_text())
 if manifest.get('engine')!='ga5-research-v4':raise ValueError('Feature manifest not accepted')
 frame=pd.read_parquet(source)
 folds=partition(frame,args.train_end,args.validation_end)
 policy=json.loads(Path(args.policy_file).read_text())
 membership={(d,t):v for d,t,v in policy['membership']}
 veto=policy['risk_veto'];blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
 genomes=[Genome(**g) for g in json.loads(Path(args.genomes).read_text())]
 if not genomes or not all(g.valid() for g in genomes):raise ValueError('Invalid genomes')
 prepared=[PreparedSessions(f) for f in folds]
 results=[]
 for g in genomes:
  folds_out=[evaluate(prep,g,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=policy['cash_proxy_annual_yield']) for prep in prepared]
  results.append({'identity':g.identity(),'genome':asdict(g),'train':folds_out[0],'validation':folds_out[1],'test':folds_out[2]})
 # Selection only on training + validation, never test outcomes.
 ranking=sorted(range(len(results)),key=lambda i:(-fitness(results[i]['validation']),-fitness(results[i]['train']),results[i]['identity']))
 selected=ranking[0]
 output={'status':'DIAGNOSTIC_ONLY_NOT_CERTIFIED','boundaries':{'train_end_exclusive':args.train_end,'validation_end_exclusive':args.validation_end},'fold_sizes':[len(f) for f in folds],'selected_identity':results[selected]['identity'],'selected_by':'validation_fitness_train_tiebreak','selected_test':results[selected]['test'],'candidates':results,'warnings':['Fixed chromosome set: no walk-forward evolutionary retraining','Provisional policy and historical membership not independently certified','Test outcomes excluded from candidate selection','Fold-boundary holdings are reset; this is not a continuous live portfolio']}
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(output,indent=2))
 print(json.dumps({'status':output['status'],'fold_sizes':output['fold_sizes'],'selected_identity':output['selected_identity'],'selected_test':output['selected_test']},indent=2))
if __name__=='__main__':run()

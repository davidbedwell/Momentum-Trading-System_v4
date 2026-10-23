"""Read-only controlled GA6 niche entry replay. Production untouched."""
import json,sys,hashlib,datetime,collections
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import pandas as pd
ROOT=Path('/opt/mts')
sys.path[:0]=[str(ROOT),str(ROOT/'ga5_redesign')]
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_ga6 import evaluate
RUN=ROOT/'ga6/runs/ga6_production_200_v1'
OUT=ROOT/'ga6/runs/GA6_NICHE_CONDITIONED_REPLAY_20261021'
OUT.mkdir(exist_ok=True)
rows=[json.loads(s) for s in open(RUN/'all_evaluations.jsonl')]
gen=max(x['generation'] for x in rows)
current=[x for x in rows if x['generation']==gen]
selected=[max((x for x in current if x['genome']['niche']==n),key=lambda x:x['fitness']) for n in sorted(set(x['genome']['niche'] for x in current))]
source=ROOT/'ga5_redesign/exploratory79_ga4_enriched.parquet'
frame=pd.read_parquet(source)
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
lf=pd.read_parquet(ROOT/'ga5_redesign/dev79_niche_ga_v1/labels.parquet')
labels={(str(r.date)[:10],r.ticker):r.research_niche for r in lf.itertuples(index=False)}
for key in prepared.membership_keys: labels.setdefault(key,None)
policy=json.load(open(ROOT/'ga5_redesign/exploratory79_policy.json'))
membership={(d,t):v for d,t,v in policy['membership']}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
veto=policy['risk_veto']
def run(job):
    item,mode=job
    genome=Genome(**item['genome'])
    if mode=='unrestricted': entry_labels=None
    elif mode=='assigned': entry_labels=labels
    else: entry_labels={k:(genome.niche if v is not None else None) for k,v in labels.items()}
    r=evaluate(prepared,genome,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=policy['cash_proxy_annual_yield'],niche_labels=entry_labels)
    trades=r['shadow'].pop('trades')
    wins=sum(t['net_return']>0 for t in trades)
    return {'niche':genome.niche,'chromosome_id':item['chromosome_id'],'mode':mode,'closed_trades':len(trades),'wins':wins,'win_rate':wins/len(trades) if trades else None,'mean_trade_return':sum(t['net_return'] for t in trades)/len(trades) if trades else None,'median_trade_return':sorted(t['net_return'] for t in trades)[len(trades)//2] if trades else None,'short_2_20_count':sum(2<=t['sessions']<=20 for t in trades),'short_2_20_wins_5pct':sum(2<=t['sessions']<=20 and t['net_return']>=.05 for t in trades),'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'signal_trace':r['signal_trace'],'research_only':True}
if __name__=='__main__':
    jobs=[(x,mode) for x in selected for mode in ('unrestricted','assigned','any_identified')]
    manifest={'generation':gen,'selection':'top fitness chromosome per each of 13 assigned niches','chromosomes':len(selected),'jobs':len(jobs),'mode_definitions':{'assigned':'only if assigned niche label at entry','any_identified':'any non-null identified niche label at entry','unrestricted':'no niche restriction'},'limitation':'retrospective replay; original sizing and exits; no new 1%-2% risk enforcement; not independent OOS certification'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    results=[]
    with ProcessPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run,j) for j in jobs]
        for f in as_completed(futures):
            result=f.result()
            results.append(result)
            (OUT/'partial_results.json').write_text(json.dumps(results,indent=2))
            print('DONE',len(results),'/',len(jobs),result['niche'],result['mode'],flush=True)
    (OUT/'results.json').write_text(json.dumps({'manifest':manifest,'results':results},indent=2))
    print('COMPLETE',OUT/'results.json',flush=True)

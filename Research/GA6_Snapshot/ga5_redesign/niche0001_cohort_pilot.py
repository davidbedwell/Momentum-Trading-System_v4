import json,collections,statistics,csv
from pathlib import Path
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019')
out=p/'niche0001_cohort_pilot';out.mkdir(exist_ok=True)
unique={}
for line in (p/'all_evaluations.jsonl').open():
 x=json.loads(line)
 if x.get('origin_niche')!='NICHE-0001':continue
 unique[x['chromosome_id']]=x
records=list(unique.values())
eligible=[x for x in records if x['result'].get('shadow',{}).get('closed_trades',0)>=50 and x['result'].get('fills',0)>=20]
eligible.sort(key=lambda x:x['result']['cagr_diagnostic'])
print('UNIQUE',len(records),'ELIGIBLE',len(eligible),flush=True)
if len(eligible)<9:raise RuntimeError('Insufficient cohort candidates')
cohorts={'bottom':eligible[:max(1,len(eligible)//3)],'middle':eligible[len(eligible)//3:2*len(eligible)//3],'top':eligible[2*len(eligible)//3:]}
fields=['entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature']
summary={}
for name,items in cohorts.items():
 r=[x['result'] for x in items]
 genes={}
 for field in fields:
  counts=collections.Counter(str(x['genome'].get(field)) for x in items)
  genes[field]=counts.most_common(8)
 summary[name]={'chromosomes':len(items),'cagr_median':statistics.median(v['cagr_diagnostic'] for v in r),'mdd_median':statistics.median(v['mdd_diagnostic'] for v in r),'fills_median':statistics.median(v['fills'] for v in r),'win_rate_median':statistics.median(v['shadow']['win_rate'] for v in r if v['shadow'].get('win_rate') is not None),'net_ev_median':statistics.median(v['shadow']['mean_net_return'] for v in r if v['shadow'].get('mean_net_return') is not None),'genes':genes}
 print(name,summary[name]['chromosomes'],'CAGR',round(summary[name]['cagr_median']*100,2),'MDD',round(summary[name]['mdd_median']*100,2),flush=True)
(out/'cohort_summary.json').write_text(json.dumps(summary,indent=2))
with (out/'all_unique_chromosomes.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['id','cohort','cagr','mdd','fills','closed_trades','win_rate','mean_net_return']+fields)
 assignment={x['chromosome_id']:name for name,items in cohorts.items() for x in items}
 for x in records:
  r=x['result'];sh=r.get('shadow',{});g=x['genome']
  w.writerow([x['chromosome_id'],assignment.get(x['chromosome_id'],'ineligible'),r.get('cagr_diagnostic'),r.get('mdd_diagnostic'),r.get('fills'),sh.get('closed_trades'),sh.get('win_rate'),sh.get('mean_net_return')]+[g.get(k) for k in fields])
print('SAVED',out,flush=True)

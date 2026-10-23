import json,statistics,collections,math
p='/opt/mts/ga6/runs/ga6_production_200_v1/all_evaluations.jsonl'
rows=[json.loads(s) for s in open(p)]
g=max(x['generation'] for x in rows);a=[x for x in rows if x['generation']==g]
def med(v):
 v=[z for z in v if isinstance(z,(int,float)) and math.isfinite(z)]
 return round(statistics.median(v),4) if v else None
def brief(x):
 r=x['result'];m=r['ga6_trade_metrics'];p=r.get('ga6_policy_oos') or {};v=p.get('validation') or {}
 return {'id':x['chromosome_id'][:12],'niche':x['genome']['niche'],'fitness':round(x['fitness'],2),'ev':round(m['net_ev'],4) if m['net_ev'] is not None else None,'tail':round(m['worst_5pct_mean'],4) if m['worst_5pct_mean'] is not None else None,'cagr':round(r['cagr_diagnostic'],4),'mdd':round(r['mdd_diagnostic'],4),'base_weight':x['genome']['base_weight'],'max_weight':x['genome']['max_weight'],'stop_loss':x['genome']['stop_loss'],'policy_validation_delta':v.get('mean_incremental'),'policy_validation_tail':v.get('tail_incremental')}
print('GENERATION',g,'COUNT',len(a))
print('LEADER',json.dumps(brief(max(a,key=lambda x:x['fitness']))))
for label,pred in [('lower_weight',lambda x:x['genome']['max_weight']<=.1),('lower_stop',lambda x:x['genome']['stop_loss']<=.15),('drawdown_under_20pct',lambda x:abs(x['result']['mdd_diagnostic'])<=.2),('drawdown_under_30pct',lambda x:abs(x['result']['mdd_diagnostic'])<=.3)]:
 z=[x for x in a if pred(x) and x['result']['ga6_trade_metrics']['net_ev'] is not None]
 print(label,'count',len(z),'median_mdd',med(abs(x['result']['mdd_diagnostic']) for x in z),'median_tail',med(x['result']['ga6_trade_metrics']['worst_5pct_mean'] for x in z))
 if z:print(' BEST_EV',json.dumps(brief(max(z,key=lambda x:x['result']['ga6_trade_metrics']['net_ev']))))
v=[x for x in a if (x['result'].get('ga6_policy_oos') or {}).get('eligible') and (x['result']['ga6_policy_oos'].get('validation') or {}).get('eligible')]
print('POLICY_VALIDATION','eligible',len(v),'median_train_delta',med(x['result']['ga6_policy_oos']['train'].get('mean_incremental') for x in v),'median_validation_delta',med(x['result']['ga6_policy_oos']['validation'].get('mean_incremental') for x in v),'median_validation_tail',med(x['result']['ga6_policy_oos']['validation'].get('tail_incremental') for x in v),'positive_validation_delta',sum((x['result']['ga6_policy_oos']['validation'].get('mean_incremental') or 0)>0 for x in v))

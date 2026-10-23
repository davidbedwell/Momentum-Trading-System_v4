"""Create a diagnostic evaluator copy; leave production evaluation unmodified."""
from pathlib import Path
p=Path('/opt/mts/ga6/structural_evolution_v3_20261022/structural_portfolio_evaluator.py');s=p.read_text()
s=s.replace('pending=None;positions={};completed_positions=[];', 'diagnostic_events=[];diagnostic_daily=[];diagnostic_active={};pending=None;positions={};completed_positions=[];')
needle='  risk_fill_cursor=len(ledger.fills)\n'
insert='''  for fill in ledger.fills[risk_fill_cursor:]:
   t=fill['security']; ds_fill=fill['execution_date'];r=rows.get(t,{})
   if fill['side']=='BUY':
    if t not in diagnostic_active:
     diagnostic_active[t]={'ticker':t,'entry_date':ds_fill,'entry_index':i,'entry_price':fill['price'],'entry_features':{k:float(v) if v is not None and isinstance(v,(int,float)) else str(v) for k,v in r.items() if k in feature_names},'fills':[],'high_water':fill['price'],'low_water':fill['price'],'entry_shares':0}
    diagnostic_active[t]['entry_shares']+=fill['shares']
   if t in diagnostic_active:
    diagnostic_active[t]['fills'].append(dict(fill))
    if fill['side']=='SELL' and not ledger.holdings.get(t,0):
     event=diagnostic_active.pop(t)
     event['exit_date']=ds_fill;event['exit_index']=i;event['exit_price']=fill['price'];event['held_sessions']=i-event['entry_index'];event['exit_features']={k:float(v) if v is not None and isinstance(v,(int,float)) else str(v) for k,v in r.items() if k in feature_names}
     event['gross_price_return']=fill['price']/event['entry_price']-1;event['mae_low']=event['low_water']/event['entry_price']-1;event['mfe_high']=event['high_water']/event['entry_price']-1
     event['exit_reason']='max_40_sessions' if event['held_sessions']>=40 else ('mandatory_risk_or_stop' if t in mandatory_exited else 'signal_or_scale_exit')
     diagnostic_events.append(event)
'''
s=s.replace(needle,insert+needle)
s=s.replace(' feature_pairs=tuple((name,LEGACY.get(name,name)) for name in set(fields)|tree_fields)',' feature_pairs=tuple((name,LEGACY.get(name,name)) for name in set(fields)|tree_fields)\n feature_names=set(source for _,source in feature_pairs)|set(fields)|tree_fields')
s=s.replace('  last.update(closes);nav.append((ds,ledger.nav(closes)))','''  for t,event in diagnostic_active.items():
   r=rows.get(t,{})
   if t in closes:
    event['high_water']=max(event['high_water'],float(r.get('high',closes[t])))
    event['low_water']=min(event['low_water'],float(r.get('low',closes[t])))
  last.update(closes);nav.append((ds,ledger.nav(closes)))
  diagnostic_daily.append({'date':ds,'nav':nav[-1][1],'holdings':{t:{'shares':q,'close':closes[t],'entry_price':diagnostic_active[t]['entry_price']} for t,q in ledger.holdings.items() if q and t in diagnostic_active}})''')
s=s.replace('"calendar_nav":nav}', '"calendar_nav":nav,"diagnostic_trades":diagnostic_events,"diagnostic_daily":diagnostic_daily}')
out=Path('/opt/mts/ga6/structural_dd_instrumented_20261022.py');out.write_text(s);compile(s,str(out),'exec');print('INSTRUMENTED',out)

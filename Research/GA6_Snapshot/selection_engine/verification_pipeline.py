"""Fail-closed GA6-v3 selector/trading engine certification pipeline.
No historical performance run is launched until all parity gates pass.
"""
import argparse,datetime,hashlib,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path('/opt/mts')
HERE=ROOT/'ga6_h/selection_engine'
OUT=ROOT/'ga6_h/audits/selector_certification'
OUT.mkdir(parents=True,exist_ok=True)
CHECKPOINT=ROOT/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json'
ENV={**os.environ,'PYTHONPATH':':'.join([str(ROOT),str(ROOT/'ga5_redesign'),str(HERE)])}

def record(name,cmd,timeout=180):
 start=time.monotonic()
 try:
  r=subprocess.run(cmd,cwd=HERE,env=ENV,capture_output=True,text=True,timeout=timeout)
  return {'name':name,'pass':r.returncode==0,'returncode':r.returncode,'seconds':round(time.monotonic()-start,2),'stdout_tail':r.stdout[-2500:],'stderr_tail':r.stderr[-2500:]}
 except subprocess.TimeoutExpired as e:
  return {'name':name,'pass':False,'error':'TIMEOUT','seconds':round(time.monotonic()-start,2)}

def main():
 p=argparse.ArgumentParser();p.add_argument('--run-history',action='store_true');a=p.parse_args()
 results=[]
 cp=json.loads(CHECKPOINT.read_text());n=len(cp['members']);results.append({'name':'checkpoint_lineage','pass':cp['generation']==269 and n==400,'generation':cp['generation'],'chromosomes':n,'sha256':hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()})
 results.append(record('defense_prior_session_no_obsolete_veto',[sys.executable,'-c',"from defense_policy_v3 import permissions;from ga6.crash_defense_A_v2_adapter import build_revised_daily_state;s=build_revised_daily_state().sort_values('date').reset_index(drop=True);d=s.date.dt.strftime('%Y-%m-%d').tolist();i=next(i for i in range(1,len(d)) if s.defensive.iloc[i-1]);j=next(i for i in range(1,len(d)) if not s.defensive.iloc[i-1]);v=permissions([d[i],d[j]]);assert not v[d[i]] and v[d[j]];import inspect;assert 'raw_risk_veto' not in inspect.getsource(permissions)"]))
 tests=['test_learning_ledger.py','test_chronological_selector.py','test_risk_allocator.py','test_shared_capital_execution.py','test_learned_shared_portfolio.py','test_policy_shadow_runner.py','test_shadow_replay.py','test_niche_signal_adapter.py','test_selector_core.py','test_research_niche_recognizer.py']
 for t in tests:results.append(record(t,[sys.executable,str(HERE/t)],timeout=120))
 # Parity must compare actual daily orders, fills, risk, corporate actions and NAV
 # against the GA6-v3 reference. An existence check is NOT sufficient.
 parity=HERE/'test_ga6v3_execution_parity.py'
 if parity.exists():results.append(record('ga6v3_execution_parity',[sys.executable,str(parity)],timeout=300))
 else:results.append({'name':'ga6v3_execution_parity','pass':False,'error':'PARITY HARNESS NOT IMPLEMENTED'})
 # Historical selection must be certified on verified point-in-time sectors and
 # genuine evaluator-equivalent shadow labels; do not treat synthetic smoke as parity.
 results.append({'name':'point_in_time_sector_provenance','pass':False,'error':'UNVERIFIED: research replay still uses UNVERIFIED_SECTOR'})
 results.append({'name':'evaluator_equivalent_mature_labels','pass':False,'error':'UNVERIFIED: shadow_replay omits original GA6 position accounting/scaling'})
 ok=all(z['pass'] for z in results)
 report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if ok else 'BLOCKED','checkpoint':str(CHECKPOINT),'gates':results,'historical_requested':a.run_history,'historical_started':False}
 if ok and a.run_history:
  report['historical_started']=True
  report['historical_launch']=record('historical', [sys.executable,str(HERE/'real_label_portfolio_replay.py'),'--symbols','3','--start','2023-09-01','--end','2024-05-01','--out',str(OUT/'historical_certified.sqlite')],timeout=7200)
  report['status']='PASS' if report['historical_launch']['pass'] else 'HISTORICAL_FAILED'
 dest=OUT/'latest.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2));tmp.replace(dest)
 print(json.dumps({'status':report['status'],'passed':sum(z['pass'] for z in results),'total':len(results),'failures':[z['name'] for z in results if not z['pass']],'report':str(dest),'historical_started':report['historical_started']}))
 return 0 if report['status']=='PASS' else 2
if __name__=='__main__':sys.exit(main())

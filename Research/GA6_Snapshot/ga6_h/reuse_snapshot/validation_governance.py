"""Fail-closed, pre-registered split sizing and single-use validation access."""
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,os,sqlite3

ROLES=('discovery','development_feedback','locked_validation','final_holdout')

@dataclass(frozen=True)
class InformationHorizon:
 holding_sessions:int
 feature_lookback_sessions:int
 state_carry_sessions:int
 def sessions(self):
  if min(self.holding_sessions,self.feature_lookback_sessions,self.state_carry_sessions)<0:raise ValueError('Negative information horizon')
  return max(self.holding_sessions,self.feature_lookback_sessions,self.state_carry_sessions)

def assess_splits(dates,regimes,horizon,minimum_sessions=252,minimum_regimes=2):
 dates=sorted(set(str(d)[:10] for d in dates));gap=horizon.sessions()
 if len(dates)<4*minimum_sessions+3*gap:return {'feasible':False,'reason':'Insufficient sessions after purging/embargo','available_sessions':len(dates),'required_sessions':4*minimum_sessions+3*gap,'horizon_sessions':gap}
 if any(d not in regimes for d in dates):return {'feasible':False,'reason':'Missing regime labels','horizon_sessions':gap}
 usable=len(dates)-3*gap;lengths=[usable//4]*4
 for i in range(usable%4):lengths[i]+=1
 segments=[];offset=0
 for role,length in zip(ROLES,lengths):
  segment=dates[offset:offset+length];labels=set(regimes[d] for d in segment)
  segments.append({'role':role,'start':segment[0],'end':segment[-1],'sessions':length,'regimes':sorted(labels),'regime_count':len(labels),'horizon_sessions':gap})
  offset+=length+gap
 feasible=all(s['sessions']>=minimum_sessions and s['regime_count']>=minimum_regimes for s in segments)
 return {'feasible':feasible,'reason':None if feasible else 'One or more segments lack sufficient length or distinct regimes','segments':segments,'horizon_sessions':gap,'required_sessions':4*minimum_sessions+3*gap}

class LockedAccess:
 def __init__(self,path):
  self.db=sqlite3.connect(path)
  self.db.execute('PRAGMA journal_mode=WAL')
  self.db.execute('CREATE TABLE IF NOT EXISTS registrations(role TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, criteria_hash TEXT NOT NULL, plan_json TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN (\'REGISTERED\',\'CONSUMED\',\'RETIRED\')), access_id TEXT, accessed_utc TEXT)')
  self.db.commit()
 def register(self,role,fingerprint,plan):
  if role not in ('locked_validation','final_holdout') or not fingerprint or not isinstance(plan,dict):raise ValueError('Invalid registration')
  required={'benchmark','loss_definition','pass_criteria','failure_policy','calendar_start','calendar_end','information_horizon_sessions','data_fingerprint','permitted_consultations'}
  if not required.issubset(plan) or plan['permitted_consultations']!=1 or plan['data_fingerprint']!=fingerprint:raise ValueError('Incomplete preregistration')
  canonical=json.dumps(plan,sort_keys=True);digest=hashlib.sha256(canonical.encode()).hexdigest()
  with self.db:self.db.execute('INSERT INTO registrations VALUES(?,?,?,?,?,?,?)',(role,fingerprint,digest,canonical,'REGISTERED',None,None))
  return digest
 def consume(self,role,fingerprint,criteria_hash):
  if role not in ('locked_validation','final_holdout'):raise ValueError('Protected role required')
  with self.db:
   row=self.db.execute('SELECT fingerprint,criteria_hash,state FROM registrations WHERE role=?',(role,)).fetchone()
   if row!=(fingerprint,criteria_hash,'REGISTERED'):raise PermissionError('Validation access denied: missing preregistration, mismatch, or already used')
   access_id=hashlib.sha256((role+fingerprint+criteria_hash).encode()).hexdigest()
   updated=self.db.execute('UPDATE registrations SET state=?,access_id=?,accessed_utc=? WHERE role=? AND state=?',('CONSUMED',access_id,datetime.now(timezone.utc).isoformat(),role,'REGISTERED'))
   if updated.rowcount!=1:raise PermissionError('Concurrent consultation rejected')
  return access_id
 def retire(self,role):
  with self.db:
   row=self.db.execute('UPDATE registrations SET state=? WHERE role=? AND state IN (?,?)',('RETIRED',role,'REGISTERED','CONSUMED'))
   if row.rowcount!=1:raise ValueError('Cannot retire unknown/already retired holdout')
 def close(self):self.db.close()

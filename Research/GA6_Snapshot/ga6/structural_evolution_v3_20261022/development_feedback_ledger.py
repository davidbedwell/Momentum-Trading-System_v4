"""Append-only development-feedback accounting, separate from locked validation.
A feedback record is a *development* observation, never certification.
"""
import hashlib,json,sqlite3,datetime
from pathlib import Path
from ga6.structural_evolution_v3_20261022.discovery_allocation import ACTIVITIES,Observation

class DevelopmentLedger:
 def __init__(self,path):
  self.db=sqlite3.connect(str(path))
  self.db.execute('PRAGMA journal_mode=WAL')
  self.db.executescript('''CREATE TABLE IF NOT EXISTS trials(
   trial_id TEXT PRIMARY KEY, chromosome_id TEXT NOT NULL, activity TEXT NOT NULL,
   niche TEXT NOT NULL, generation INTEGER NOT NULL, role TEXT NOT NULL CHECK(role IN ('discovery','development_feedback')),
   difficulty_bucket TEXT NOT NULL, cpu_seconds REAL NOT NULL CHECK(cpu_seconds>=0),
   reward REAL, reward_status TEXT NOT NULL CHECK(reward_status IN ('PENDING','CREDITED')),
   evidence_hash TEXT, created_utc TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS decisions(generation INTEGER PRIMARY KEY, weights_json TEXT NOT NULL,
   credited_through INTEGER NOT NULL, ledger_hash TEXT NOT NULL, created_utc TEXT NOT NULL);''')
  self.db.commit()
 def record_trial(self,trial_id,chromosome_id,activity,niche,generation,role,difficulty_bucket,cpu_seconds):
  if (activity not in ACTIVITIES and not (activity=='protected_niche' and role=='discovery')) or role not in ('discovery','development_feedback'):raise ValueError('Invalid provenance')
  now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  with self.db:self.db.execute('INSERT INTO trials VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
   (trial_id,chromosome_id,activity,niche,generation,role,difficulty_bucket,cpu_seconds,None,'PENDING',None,now))
 def credit(self,trial_id,reward,evidence_hash):
  if not evidence_hash or not isinstance(reward,(int,float)) or not 0<=reward<=1:raise ValueError('Invalid reward')
  with self.db:
   r=self.db.execute('SELECT role,reward_status FROM trials WHERE trial_id=?',(trial_id,)).fetchone()
   if not r or r!=('development_feedback','PENDING'):raise ValueError('Only pending development-feedback trials may be credited once')
   self.db.execute('UPDATE trials SET reward=?,reward_status=?,evidence_hash=? WHERE trial_id=?',(float(reward),'CREDITED',evidence_hash,trial_id))
 def observations(self,generation,lag=2):
  # Lag prevents using same-generation feedback to allocate its own trials.
  rows=self.db.execute('SELECT activity,difficulty_bucket,COUNT(*),SUM(reward),SUM(cpu_seconds) FROM trials WHERE role=? AND reward_status=? AND generation<=? GROUP BY activity,difficulty_bucket',('development_feedback','CREDITED',generation-lag)).fetchall()
  by_bucket={}
  for a,b,n,r,c in rows:by_bucket.setdefault(b,[]).append((a,n,r,c))
  # Difficulty normalization requires comparable activities in the SAME bucket.
  # Do not collapse raw successes across unequal test regimes.
  totals={a:[0,0.,0.] for a in ACTIVITIES}
  for bucket,items in by_bucket.items():
   if len({a for a,_,_,_ in items})<2:continue
   bucket_rate=sum(r for _,_,r,_ in items)/max(1,sum(n for _,n,_,_ in items))
   if bucket_rate<=0:continue
   for a,n,r,c in items:
    totals[a][0]+=n
    totals[a][1]+=min(n,max(0,r/bucket_rate))
    totals[a][2]+=c
  return {a:Observation(n,int(round(r)),c) for a,(n,r,c) in totals.items() if n>0}
 def record_decision(self,generation,weights,credited_through):
  if set(weights)!=set(ACTIVITIES):raise ValueError('Incomplete allocation')
  ledger_hash=hashlib.sha256(json.dumps(self.db.execute('SELECT trial_id,role,reward_status,evidence_hash FROM trials ORDER BY trial_id').fetchall()).encode()).hexdigest()
  with self.db:self.db.execute('INSERT INTO decisions VALUES(?,?,?,?,?)',(generation,json.dumps(weights,sort_keys=True),credited_through,ledger_hash,datetime.datetime.now(datetime.timezone.utc).isoformat()))
 def close(self):self.db.close()

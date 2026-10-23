"""Single guarded GA5 research evaluation interface. NOT production certified."""
import hashlib,json,sqlite3
from pathlib import Path
import pandas as pd
from ga5_feature_families import compute
from ga5_chromosome_portfolio_pilot import evaluate as pilot_evaluate

ENGINE_VERSION="ga5-research-v4"
REQUIRED=("date","ticker","open","high","low","close","volume")
def digest_file(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def prepare(raw_path,feature_path,sector_map=None):
 raw_path=Path(raw_path);feature_path=Path(feature_path)
 if not raw_path.exists():raise FileNotFoundError(raw_path)
 source=digest_file(raw_path)
 meta=feature_path.with_suffix(".manifest.json")
 config={"source_sha256":source,"sector_map":sector_map,"engine":ENGINE_VERSION}
 if feature_path.exists() and meta.exists() and json.loads(meta.read_text())==config:
  return config
 d=pd.read_parquet(raw_path)
 if not set(REQUIRED).issubset(d):raise ValueError("Missing OHLCV columns")
 if d.duplicated(["date","ticker"]).any():raise ValueError("Duplicate daily bars")
 if d[list(REQUIRED[2:])].isna().any().any():raise ValueError("Missing OHLCV values")
 if sector_map is None:raise ValueError("PIT sector mapping required for full eight-family evaluation")
 d=compute(d,sector_map=sector_map)
 feature_path.parent.mkdir(parents=True,exist_ok=True)
 temp=feature_path.with_suffix(".tmp.parquet");d.to_parquet(temp,index=False);temp.replace(feature_path)
 tempmeta=meta.with_suffix(".tmp.json");tempmeta.write_text(json.dumps(config,sort_keys=True));tempmeta.replace(meta)
 return config
class ResultCache:
 def __init__(self,path):
  self.db=sqlite3.connect(path,timeout=60)
  self.db.execute("PRAGMA journal_mode=WAL")
  self.db.execute("CREATE TABLE IF NOT EXISTS evaluations (key TEXT PRIMARY KEY, result TEXT NOT NULL)")
 def key(self,genome,data_sha,fold,policy):
  return hashlib.sha256(json.dumps([ENGINE_VERSION,genome.identity(),data_sha,fold,policy],sort_keys=True).encode()).hexdigest()
 def get(self,key):
  row=self.db.execute("SELECT result FROM evaluations WHERE key=?",(key,)).fetchone()
  return json.loads(row[0]) if row else None
 def put(self,key,result):
  self.db.execute("INSERT OR IGNORE INTO evaluations VALUES (?,?)",(key,json.dumps(result,sort_keys=True)))
  self.db.commit()
 def close(self):self.db.close()
def validate_science(policy):
 needed=("pit_membership_verified","pit_earnings_verified","corporate_actions_verified",
         "t_plus_one_enforced","cash_proxy_verified","risk_veto_enforced",
         "chronological_folds_verified","blind_reserved")
 missing=[k for k in needed if policy.get(k) is not True]
 if missing:raise ValueError("Certification gate closed: "+", ".join(missing))
 # The pilot simulator is incapable of enforcing all these flags, even if supplied.
 raise NotImplementedError("Canonical certified simulator not implemented; flags cannot override enforcement")
def diagnostic_evaluate(prepared,genome,cache=None,data_sha=None,fold="development",policy="diagnostic-v1"):
 """Explicit diagnostic only; never use for certified strategy promotion."""
 if not isinstance(prepared,pd.DataFrame):raise TypeError("Prepared dataframe required")
 if cache is not None:
  if not data_sha:raise ValueError("Cache requires immutable data fingerprint")
  key=cache.key(genome,data_sha,fold,policy)
  cached=cache.get(key)
  if cached is not None:return cached,True
 result=pilot_evaluate(prepared,genome,prepared=True)
 if cache is not None:cache.put(key,result)
 return result,False

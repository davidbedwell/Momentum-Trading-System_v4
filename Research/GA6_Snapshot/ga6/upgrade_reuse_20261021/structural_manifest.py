"""Append-only, reproducible structural candidate definitions and trial occurrences."""
import hashlib
import json
import sqlite3
from ga6.upgrade_reuse_20261021.structural_candidate import StructuralCandidate

class StructuralManifest:
 def __init__(self,path):
  self.db=sqlite3.connect(str(path))
  self.db.execute("PRAGMA journal_mode=WAL")
  self.db.execute("CREATE TABLE IF NOT EXISTS candidates (structural_id TEXT PRIMARY KEY, definition_json TEXT NOT NULL, digest TEXT NOT NULL)")
  self.db.execute("CREATE TABLE IF NOT EXISTS occurrences (trial_id TEXT PRIMARY KEY, structural_id TEXT NOT NULL, activity TEXT NOT NULL, generation INTEGER NOT NULL, role TEXT NOT NULL)")
  self.db.commit()
 def record(self,trial_id,candidate,activity,generation,role):
  if not isinstance(candidate,StructuralCandidate):raise TypeError("Expected structural candidate")
  definition=json.dumps(candidate.checkpoint(),sort_keys=True,separators=(",",":"))
  digest=hashlib.sha256(definition.encode()).hexdigest()
  identity=candidate.identity()
  with self.db:
   existing=self.db.execute("SELECT definition_json,digest FROM candidates WHERE structural_id=?",(identity,)).fetchone()
   if existing and existing!=(definition,digest):raise ValueError("Conflicting chromosome definition")
   if existing is None:self.db.execute("INSERT INTO candidates VALUES(?,?,?)",(identity,definition,digest))
   occurrence=(identity,activity,generation,role)
   previous=self.db.execute("SELECT structural_id,activity,generation,role FROM occurrences WHERE trial_id=?",(trial_id,)).fetchone()
   if previous and previous!=occurrence:raise ValueError("Conflicting trial occurrence")
   if previous is None:self.db.execute("INSERT INTO occurrences VALUES(?,?,?,?,?)",(trial_id,*occurrence))
 def restore(self,identity):
  record=self.db.execute("SELECT definition_json,digest FROM candidates WHERE structural_id=?",(identity,)).fetchone()
  if record is None:raise KeyError(identity)
  if hashlib.sha256(record[0].encode()).hexdigest()!=record[1]:raise ValueError("Altered chromosome definition")
  return StructuralCandidate.restore(json.loads(record[0]))
 def close(self):self.db.close()

"""Verify one-to-one trial provenance and reproducible definitions."""
import hashlib
import json
import sqlite3
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate

def audit(trial_path,manifest_path):
 trials=sqlite3.connect(str(trial_path))
 manifest=sqlite3.connect(str(manifest_path))
 try:
  a=trials.execute("SELECT trial_id,chromosome_id,activity,generation,role FROM trials ORDER BY trial_id").fetchall()
  b=manifest.execute("SELECT trial_id,structural_id,activity,generation,role FROM occurrences ORDER BY trial_id").fetchall()
  if a!=b:raise ValueError("Trial ledger and manifest occurrences disagree")
  rows=manifest.execute("SELECT structural_id,definition_json,digest FROM candidates").fetchall()
  for identity,definition,digest in rows:
   if hashlib.sha256(definition.encode()).hexdigest()!=digest:raise ValueError("Definition checksum mismatch")
   if StructuralCandidate.restore(json.loads(definition)).identity()!=identity:raise ValueError("Definition identity mismatch")
  missing={x[1] for x in a}-{x[0] for x in rows}
  if missing:raise ValueError("Missing chromosome definitions")
  return {'trials':len(a),'occurrences':len(b),'definitions':len(rows),'missing_definitions':0,'verified':True}
 finally:
  trials.close()
  manifest.close()

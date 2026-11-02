"""Causal fold-by-fold selector learning and frozen proof evaluation.
Consumes completed shadow-ledger rows; never invents trade outcomes.
"""
import json,hashlib
from pathlib import Path
from ga6.selector_learning_fourfold_20261025 import FOLDS,OUT,ShadowLedger,RetainedSelectorMemory,fold_for
class FoldTrainer:
 def __init__(self,ledger,prior_strength=20):
  self.ledger=ledger;self.memory=RetainedSelectorMemory(prior_strength)
  self.snapshots=[]
 def learn_until(self,cutoff):
  # Only outcomes strictly matured before cutoff; no lookahead.
  matured=sorted(self.ledger.matured(cutoff),key=lambda r:(r['outcome_available_at'],r['signal_id']))
  new=0
  for row in matured:
   if row['signal_id'] in self.memory.seen:continue
   self.memory.observe(row,cutoff);new+=1
  return new
 def run(self):
  for fold,start,end,role in FOLDS:
   if role=='proof':
    assert fold=='F4'
    before=self.memory.snapshot(OUT/'selector_FROZEN_V1.json','2022-12-31')
    self.snapshots.append({'fold':fold,'role':role,'training_updates':0,'frozen_sha256':hashlib.sha256((OUT/'selector_FROZEN_V1.json').read_bytes()).hexdigest(),'observations':before['observation_count']})
    break
   # A fold can teach the NEXT fold only after the fold ends.
   n=self.learn_until(end)
   snap=self.memory.snapshot(OUT/f'selector_after_{fold}.json',str(end)[:10] if end<'2023-01-01' else '2022-12-31')
   self.snapshots.append({'fold':fold,'role':role,'training_updates':n,'observations':snap['observation_count']})
  (OUT/'learning_fold_audit.json').write_text(json.dumps(self.snapshots,indent=2))
  return self.snapshots
if __name__=='__main__':
 p=OUT/'shadow_ledger.jsonl'
 if not p.exists():raise SystemExit('No actual shadow outcomes yet; refusing to manufacture training data')
 print(json.dumps(FoldTrainer(ShadowLedger(p)).run(),indent=2))

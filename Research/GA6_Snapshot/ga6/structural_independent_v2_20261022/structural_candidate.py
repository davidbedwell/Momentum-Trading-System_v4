"""Checkpoint-safe structural chromosome identity and executable replay adapter."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
from ga5_chromosome_contract import Genome
from ga6.structural_independent_v2_20261022.family_logic import validate
from ga6.structural_independent_v2_20261022.structural_portfolio_evaluator import evaluate

@dataclass(frozen=True)
class StructuralCandidate:
 genome:Genome
 entry_tree:dict
 def __post_init__(self):
  if not self.genome.valid():raise ValueError('Invalid base genome')
  validate(self.entry_tree)
 def identity(self):
  return sha256(json.dumps({'genome':asdict(self.genome),'entry_tree':self.entry_tree},sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def checkpoint(self):
  return {'genome':asdict(self.genome),'entry_tree':self.entry_tree,'structural_id':self.identity()}
 @classmethod
 def restore(cls,record):
  candidate=cls(Genome(**record['genome']),record['entry_tree'])
  if candidate.identity()!=record['structural_id']:raise ValueError('Structural checkpoint fingerprint mismatch')
  return candidate
 def replay(self,prepared,**kwargs):
  return evaluate(prepared,self.genome,entry_tree=self.entry_tree,**kwargs)

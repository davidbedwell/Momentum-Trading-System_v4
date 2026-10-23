from niche_signal_adapter import evaluate_all
from types import SimpleNamespace
from ga5_chromosome_contract import Genome
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from dataclasses import replace
from ga5_feature_families import FAMILIES
import json
from pathlib import Path
path=Path('/opt/mts/ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json')
data=json.loads(path.read_text())
cs=[StructuralCandidate.restore(z) for z in data['members']]
assert len(cs)==400
features={k:0.2 for k in FAMILIES}
from niche_signal_adapter import required_features
from ga5_feature_adapter import LEGACY
for c in cs:
 for f in required_features(c):features[LEGACY.get(f,f)]=0.2
niche=cs[0].genome.niche
r=evaluate_all(asof='2024-06-01',symbol='XYZ',market_features=features,recognized_niches={niche},niche_evidence_cutoff='2024-06-01',candidates=cs,close_price=100)
assert r['eligible_chromosomes']==sum(c.genome.niche==niche for c in cs)
assert len(r['decisions'])==r['eligible_chromosomes'],r
assert all(x['niche']==niche for x in r['decisions'])
try:
 evaluate_all(asof='2024-06-01',symbol='XYZ',market_features=features,recognized_niches=None,niche_evidence_cutoff=None,candidates=cs,close_price=100)
 raise AssertionError('unrecognized niches permitted')
except ValueError:pass
print('PASS: all 400 checkpoint fingerprints, mandatory niche evidence, complete matching chromosome decisions',len(r['decisions']))

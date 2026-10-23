from ga6.structural_evolution_v3_20261022 import structural_decision as module
from ga5_redesign.niche_seeds import initial
from ga5_chromosome_decisions import PositionState
from ga5_feature_families import FAMILIES

families=list(FAMILIES)
tree={'op':'AND','children':[{'family':families[0],'threshold':-0.5,'comparison':'>='},{'family':families[1],'threshold':-0.5,'comparison':'>='}]}
module.legacy_decision=lambda *args:('NO_ENTRY',0.)
genome=initial('NICHE-0001')
features={families[0]:0.,families[1]:0.}
result=module.decision(genome,features,PositionState(),100,tree)
assert result[0]=='ENTER' and result[1]>0,result
print('PASS independent structural entry despite legacy rejection',result)
features[families[0]]=-1.
result=module.decision(genome,features,PositionState(),100,tree)
assert result==('NO_ENTRY',0.),result
print('PASS structural entry correctly rejects false tree')

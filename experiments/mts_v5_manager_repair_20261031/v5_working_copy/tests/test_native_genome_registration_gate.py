import pytest
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.genome_identity import GenomeIdentityRegistry
from engines.portfolio_replay.kernel import Bar

def test_native_replay_rejects_reused_id_for_different_genome():
    days=[('2026-01-02',{'AAA':Bar(100,100)}),('2026-01-03',{'AAA':Bar(101,101)})]
    candidates=[Candidate('same','GA6','A',.02),Candidate('same','GA7',None,.02)]
    registry=GenomeIdentityRegistry()
    def replay(genomes):
        return run_slice(days,candidates,
            classify=lambda t,d:NicheObservation(d,'2025-12-31','synthetic',(('A',.1),)),
            eligible=lambda *args:True,native=lambda *args:None,
            native_genomes=genomes,genome_registry=registry)
    original={('GA6','same'):{'entry':1,'exit':2},('GA7','same'):{'entry':9,'exit':8}}
    replay(original)
    replay(original)
    with pytest.raises(ValueError,match='reused'):
        replay({**original,('GA6','same'):{'entry':3,'exit':2}})
    with pytest.raises(ValueError,match='complete'):
        replay({('GA6','same'):{'entry':1}})

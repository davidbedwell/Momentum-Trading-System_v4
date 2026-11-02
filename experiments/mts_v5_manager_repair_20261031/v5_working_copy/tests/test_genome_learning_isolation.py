import pytest
from discovery.competitive_ga.causal_calibration import TradeOutcome
from discovery.competitive_ga.shadow_learning_interface import ShadowLearningView
from discovery.competitive_ga.evolved_selection_policy import SelectionGenes,score
from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
from discovery.competitive_ga.genome_identity import GenomeIdentityRegistry,fingerprint
from engines.portfolio_replay.kernel import Bar

def test_changed_genome_cannot_inherit_matured_shadow_edge():
    view=ShadowLearningView(min_samples=2,prior_strength=0)
    old=fingerprint({'entry':1,'exit':2})
    new=fingerprint({'entry':2,'exit':2})
    for i in range(3):
        view.ingest(TradeOutcome('42',('A','A',.2),i,i+3,.12,'shadow',f'T{i}','GA6',old))
    candidate=Candidate('42','GA6','A',.02)
    genes=SelectionGenes(0,1,0,0)
    snap=view.snapshot(8)
    snap['genome_hashes']={('GA6','42'):old}
    assert score(genes,candidate,'A',(('A',.2),),.01,snap)>.1
    snap['genome_hashes']={('GA6','42'):new}
    assert score(genes,candidate,'A',(('A',.2),),.01,snap)==.01
    assert all(k[2]==old for k in snap['estimates'])

def test_production_requires_pre_registered_unchanged_genomes():
    candidates=[Candidate('42','GA6','A',.02)]
    days=[('2026-01-02',{'AAA':Bar(100,100)}),('2026-01-03',{'AAA':Bar(101,101)})]
    reg=GenomeIdentityRegistry()
    native_genomes={('GA6','42'):{'entry':1,'exit':2}}
    def replay(genomes=None,registry=None):
        return run_slice(days,candidates,
            classify=lambda t,d:NicheObservation(d,'2025-12-31','fixture',(('A',.1),)),
            eligible=lambda *args:True,native=lambda *args:None,
            native_genomes=genomes,genome_registry=registry,require_genome_identity=True)
    with pytest.raises(ValueError,match='production requires'):replay()
    with pytest.raises(ValueError,match='unregistered'):replay(native_genomes,reg)
    reg.register('GA6','42',native_genomes[('GA6','42')])
    replay(native_genomes,reg)
    with pytest.raises(ValueError,match='mismatch'):
        replay({('GA6','42'):{'entry':9,'exit':2}},reg)

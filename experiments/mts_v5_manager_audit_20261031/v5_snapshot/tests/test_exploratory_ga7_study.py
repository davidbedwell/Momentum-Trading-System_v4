import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from discovery.competitive_ga.exploratory_ga7_study import Policy
from discovery.competitive_ga.causal_calibration import TradeOutcome

class ExploratoryStudyTests(unittest.TestCase):
    def test_today_exit_is_not_learned_until_next_session(self):
        p=Policy([('GA6','a','NICHE-0001',{})])
        o=TradeOutcome('a',('PIT-NICHE-0001','PIT-NICHE-0001',.2),1,3,.02,'shadow','AAA','GA6','hash')
        p.on_session(3,'2027-01-07',[o])
        self.assertEqual(len(p.stats),0)
        p.on_session(4,'2027-01-08',[])
        self.assertEqual(p.stats['GA6','a'][0],1)
        self.assertEqual(p.max_maturity,3)

    def test_joint_evolution_is_deterministic_and_strict_past(self):
        policies=[Policy([('GA6','a','NICHE-0001',{}),('GA7','b','NON_NICHE',{})],seed=12) for _ in range(2)]
        for p in policies:
            p.stats['GA6','a'][:]=(10,.2,.004)
            p.stats['GA7','b'][:]=(10,-.2,.004)
            p.max_maturity=250
            with tempfile.TemporaryDirectory() as directory, patch('discovery.competitive_ga.exploratory_ga7_study.OUT',Path(directory)):
                p.on_session(252,'2028-01-04',[])
            self.assertEqual(p.events[0]['training_maturity_max'],250)
            self.assertEqual(len(p.events[0]['chromosome_allocation']),2)
        self.assertEqual(policies[0].events,policies[1].events)

class DynamicNativeRegistryTests(unittest.TestCase):
    def test_new_genome_gets_independent_shadow_identity(self):
        from discovery.competitive_ga.functional_niche_manager import Candidate,NicheObservation,run_slice
        from discovery.competitive_ga.genome_identity import GenomeIdentityRegistry
        from discovery.competitive_ga.native_signal_contract import NativeProposal
        from engines.portfolio_replay.kernel import Bar
        candidates=[Candidate('parent','GA7',None,.02)]
        genomes={('GA7','parent'):{'threshold':.4}}
        registry=GenomeIdentityRegistry();registry.register('GA7','parent',genomes['GA7','parent'])
        dates=['2027-01-04','2027-01-05','2027-01-06','2027-01-07','2027-01-08']
        def hook(session,date,matured):
            if session==1:
                genomes['GA7','child']={'threshold':.5}
                registry.register('GA7','child',genomes['GA7','child'])
                candidates.append(Candidate('child','GA7',None,.02))
        def native(c,t,d,held):
            return NativeProposal(d,t,'GA7',c.chromosome_id,'EXIT' if held else 'ENTER',0 if held else .1,0.,'net_return_fraction',registry.by_id['GA7',c.chromosome_id],'snapshot','2026-10-28')
        result=run_slice([(d,{'AAA':Bar(100,100)}) for d in dates],candidates,
            classify=lambda t,d:NicheObservation(d,'2026-10-28','test',()),eligible=lambda *a:True,native=native,
            native_shadow=True,native_genomes=genomes,genome_registry=registry,require_genome_identity=True,
            session_hook=hook,candidate_provider=lambda:candidates,retain_audit=False,funded_entry_scale=lambda:.5)
        outcomes={o.chromosome_id:o.genome_hash for o in result['native_shadow_outcomes']}
        self.assertEqual(outcomes['child'],registry.by_id['GA7','child'])
        self.assertNotEqual(outcomes['parent'],outcomes['child'])
        self.assertEqual(result['decisions'],[])
        self.assertEqual(result['learning_snapshots'],[])
        self.assertLess(result['ledger'][0][3]*result['ledger'][0][4],5100)

if __name__=='__main__':unittest.main()

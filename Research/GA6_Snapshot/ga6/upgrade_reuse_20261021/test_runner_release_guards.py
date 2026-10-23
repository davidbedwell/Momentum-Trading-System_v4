"""Fail-closed release checks for experimental GA6 discovery runner."""
import ast,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
class ReleaseGuards(unittest.TestCase):
 def test_no_fitness_reward(self):
  text=(BASE/'production_discovery_v2_20261021.py').read_text()
  self.assertIn("'adaptive_reward_status']='DISABLED_PENDING_INDEPENDENT_DEV_FEEDBACK'",text)
  self.assertIn('propose(scored,rng,a.population,generation+1,None)',text)
  self.assertNotIn('if score>0:novel[activity]+=1',text)
 def test_fingerprint_dependencies(self):
  text=(BASE/'production_discovery_v2_20261021.py').read_text()
  for name in ('discovery_population.py','discovery_allocation.py','development_feedback_ledger.py'):
   self.assertIn('"'+name+'"',text)
 def test_experimental_not_certified(self):
  text=(BASE/'production_discovery_v2_20261021.py').read_text()
  self.assertIn('NOT CERTIFIED',text)
  self.assertIn('MAX_SWING_SESSIONS=40',(BASE/'fast_portfolio_evaluator_20261021.py').read_text())
 def test_full_grammar_not_misrepresented(self):
  text=(BASE/'upgrade_reuse_20261021'/'discovery_population.py').read_text()
  self.assertIn('No claims that separate boolean catalog expressions execute',text)
if __name__=='__main__':unittest.main()

import unittest,inspect
from ga6.upgrade_reuse_20261021.structural_portfolio_evaluator import evaluate
class IntegrationContract(unittest.TestCase):
 def test_tree_parameter_and_chronological_replay_preserved(self):
  self.assertIn('entry_tree',inspect.signature(evaluate).parameters)
  src=inspect.getsource(evaluate)
  for required in ('SettledLedger','entry_allowed','MAX_SWING_SESSIONS','risk_veto','membership','structural_signal','validate_tree','ledger.execute_open'):
   self.assertIn(required,src)
if __name__=='__main__':unittest.main()

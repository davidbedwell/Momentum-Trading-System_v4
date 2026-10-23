import tempfile
import unittest
from pathlib import Path
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6.structural_independent_v2_20261022.structural_manifest import StructuralManifest

class ManifestTests(unittest.TestCase):
 def test_restore_replay_and_conflicts(self):
  c=StructuralCandidate(initial(NICHES[0]),{'family':'trend','threshold':0.1,'comparison':'>='})
  with tempfile.TemporaryDirectory() as directory:
   m=StructuralManifest(Path(directory)/'manifest.sqlite')
   m.record('trial1',c,'evolution',1,'discovery')
   m.record('trial1',c,'evolution',1,'discovery')
   self.assertEqual(m.restore(c.identity()).identity(),c.identity())
   with self.assertRaises(ValueError):m.record('trial1',c,'challengers',1,'discovery')
   with self.assertRaises(KeyError):m.restore('missing')
   m.close()
if __name__=='__main__':unittest.main()

import fcntl
import json
import tempfile
from pathlib import Path
import unittest
from ga9.supervisor import Supervisor, atomic, target

class Tests(unittest.TestCase):
    def test_objective_strict(self):
        self.assertFalse(target(.30,.10,.09,.079))
        self.assertFalse(target(.31,.10,.09,.08))
        self.assertFalse(target(.31,.10,.12,.07))
        self.assertTrue(target(.33,.10,.12,.079))
        self.assertFalse(target(float('nan'),.1,.1,.01))

    def test_durable_resume_and_single_instance(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            a = Supervisor(p)
            with self.assertRaises(BlockingIOError): Supervisor(p)
            a.state['steps']['reserved'] = {'status':'RUNNING'}
            a.save('TEST')
            a.lock.close()
            b = Supervisor(p)
            b.step('reserved', ['/does/not/exist'], 1)
            self.assertEqual(b.state['steps']['reserved']['status'], 'RUNNING')
            self.assertFalse(b.state['research_enabled'])
            b.lock.close()
            self.assertEqual(json.loads((p/'state.json').read_text())['codex_calls'],0)

    def test_timeout_and_restart_no_repeat(self):
        import sys
        with tempfile.TemporaryDirectory() as d:
            a = Supervisor(Path(d))
            a.step('timeout', [sys.executable,'-c','import time; time.sleep(30)'], .1)
            self.assertEqual(a.state['steps']['timeout']['status'],'TIMEOUT')
            a.step('timeout', ['/does/not/exist'], 1)
            a.lock.close()

if __name__ == '__main__': unittest.main()

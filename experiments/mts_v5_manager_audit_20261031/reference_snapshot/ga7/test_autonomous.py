import json
import sys
import tempfile
import unittest
from pathlib import Path
from ga7.autonomous import STAGES, run

class AutonomousTests(unittest.TestCase):
    def test_stages_complete_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.txt"
            source.write_text("immutable")
            stages = {}
            for stage in STAGES:
                artifact = root / (stage + ".json")
                stages[stage] = {
                    "argv": [sys.executable, "-c", "import pathlib; pathlib.Path(%r).write_text('ok')" % str(artifact)],
                    "outputs": [str(artifact)]
                }
            plan = root / "plan.json"
            plan.write_text(json.dumps({"inputs": {"source": str(source)}, "stages": stages}))
            run(plan, root / "output")
            self.assertTrue((root / "output" / "pipeline_complete.json").exists())
            run(plan, root / "output")
            source.write_text("changed")
            with self.assertRaises(ValueError):
                run(plan, root / "output")

if __name__ == "__main__":
    unittest.main()

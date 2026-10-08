"""Behavioral guards for the G2 orchestration certification boundary."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import run_mts_g2_workflow_20261006 as wf

class WorkflowFailClosedTests(unittest.TestCase):
    def test_bare_pass_is_not_certification(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "evidence.json"
            p.write_text(json.dumps({"passed": True}))
            m = Path(d) / "manifest.json"
            m.write_text(json.dumps({"stage_evidence_bindings": {}}))
            with patch.dict(wf.EVIDENCE, {"NULL_CALIBRATION": p}), patch.object(wf, "MANIFEST", m):
                self.assertFalse(wf.evidence_ok("NULL_CALIBRATION"))

    def test_wrong_evidence_hash_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "evidence.json"
            p.write_text(json.dumps({"passed": True}))
            m = Path(d) / "manifest.json"
            m.write_text(json.dumps({"stage_evidence_bindings": {"NULL_CALIBRATION": {"sha256": "0"*64}}}))
            with patch.dict(wf.EVIDENCE, {"NULL_CALIBRATION": p}), patch.object(wf, "MANIFEST", m):
                self.assertFalse(wf.evidence_ok("NULL_CALIBRATION"))

    def test_matching_bound_evidence_passes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "evidence.json"
            p.write_text(json.dumps({"passed": True}))
            m = Path(d) / "manifest.json"
            m.write_text(json.dumps({"stage_evidence_bindings": {"NULL_CALIBRATION": {"sha256": wf.sha(p)}}}))
            with patch.dict(wf.EVIDENCE, {"NULL_CALIBRATION": p}), patch.object(wf, "MANIFEST", m):
                self.assertTrue(wf.evidence_ok("NULL_CALIBRATION"))

if __name__ == "__main__":
    unittest.main()

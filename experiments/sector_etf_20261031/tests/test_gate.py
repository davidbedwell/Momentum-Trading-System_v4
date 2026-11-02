"""Safety/validity tests of acquisition gate, not market-result tests."""
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_gate', ROOT / 'run.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def payload(day='2020-05-27', value=100):
    stamp = int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp())
    return {'chart': {'result': [{'timestamp': [stamp], 'indicators': {'adjclose': [{'adjclose': [value]}]}}]}}


class GateTests(unittest.TestCase):
    def test_frozen_protocol(self):
        self.assertEqual(gate.verify_protocol()['status'], 'frozen before price download and outcomes')

    def test_protocol_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'PREREGISTRATION.md').write_text('modified')
            (root / 'preregistration.lock.json').write_text((ROOT / 'preregistration.lock.json').read_text())
            with self.assertRaises(ValueError):
                gate.verify_protocol(root)

    def test_sgov_preinception_rejected(self):
        with self.assertRaises(ValueError):
            gate.parse_chart(payload('2019-01-02'), 'SGOV')

    def test_valid_adjusted_close(self):
        self.assertEqual(gate.parse_chart(payload(), 'SGOV')[0]['adjusted_close'], 100)

    def test_unadjusted_not_silently_accepted(self):
        p = payload()
        p['chart']['result'][0]['indicators'] = {'quote': [{'close': [100]}]}
        with self.assertRaises(KeyError):
            gate.parse_chart(p, 'SPY')

    def test_invalid_price_rejected(self):
        for price in [0, -1, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                gate.parse_chart(payload(value=price), 'SPY')

    def test_post_cutoff_not_admitted(self):
        with self.assertRaises(ValueError):
            gate.parse_chart(payload('2026-01-02'), 'SPY')

    def test_network_failure_preserves_sealed_validation(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'data').mkdir()
            for filename in ['PREREGISTRATION.md', 'preregistration.lock.json']:
                (root / filename).write_bytes((ROOT / filename).read_bytes())
            with patch.object(gate.socket, 'getaddrinfo', side_effect=OSError('offline')):
                self.assertEqual(gate.acquire(root), 2)
            evidence = json.loads((root / 'outputs/acquisition.json').read_text())
            self.assertFalse(evidence['validation_opened'])
            self.assertFalse(evidence['outcomes_computed'])
            self.assertEqual(evidence['acquired'], {})


if __name__ == '__main__':
    unittest.main()

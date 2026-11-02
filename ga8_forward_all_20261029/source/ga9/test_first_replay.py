import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from .first_replay import ingest, empty_proof

ROOT = Path(__file__).parent/'artifacts'
GAPS = ROOT/'nasdaq_archive_audit_final_20261029/missing_projected_bars.csv'
BATCHES = [ROOT/n for n in ('alpaca_stock_recovery_batch_20261029', 'alpaca_stock_recovery_second_20261029', 'identity_retrieval_host_20261029')]

class FirstReplayTests(unittest.TestCase):
    def test_exact_reconciliation_and_determinism(self):
        a = ingest(GAPS, BATCHES)
        self.assertEqual(a, ingest(GAPS, reversed(BATCHES)))
        self.assertEqual((a['original_gaps'],len(a['raw']),len(a['corrections']),len(a['remaining'])), (5506,4498,5,1003))
        self.assertEqual({r['ticker'] for r in a['remaining']}, {'GOOGL'})
        self.assertEqual(sum(r['ticker']=='FB' for r in a['raw']),109)
        self.assertTrue(all(r['admission']=='QUARANTINED_RAW_ONLY' for r in a['raw']))
        self.assertTrue(all(not r['lineage']['trading_eligible'] for r in a['raw'] if 'lineage' in r))

    def test_tampered_response_rejected(self):
        batch = BATCHES[-1]
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            for name in ('report.json','recovered_raw.json','response_0001.json','response_0002.json'):
                (dest/name).write_bytes((batch/name).read_bytes())
            with (dest/'response_0001.json').open('a') as f: f.write(' ')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                ingest(GAPS,[dest])

    def test_no_admission_no_orders_no_fills(self):
        dates = pd.to_datetime(['2022-01-03','2022-01-04','2022-01-05'])
        r = empty_proof(dates)
        self.assertEqual(r['fills'], [])
        self.assertEqual(r['metrics']['final_nav'],100000)
        self.assertEqual(r['metrics']['max_drawdown'],0)
        self.assertEqual(len(r['execution_stages']),2)
        self.assertTrue(all(e['decision']=='NO_TRADE' and e['eligible']==0 for e in r['events']))
        self.assertTrue(all(e['nav']==100000 and e['holdings']==0 for e in r['equity']))
        with self.assertRaises(ValueError): empty_proof(dates[::-1])

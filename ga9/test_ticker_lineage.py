from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from ga9.ticker_lineage import FB, XLNX, MERGER, historical_identity
from ga9.repair_ticker_identities import run, prior_recoveries
from ga9.alpaca_repair import Client


class LineageTests(unittest.TestCase):
    def test_immutable_content_addressed_lineage(self):
        with self.assertRaises(FrozenInstanceError): FB.new_symbol = 'AMD'
        self.assertEqual(MERGER.predecessor, XLNX.digest)
        self.assertNotEqual(replace(XLNX, detail='correction').digest, XLNX.digest)
        self.assertIsNone(MERGER.known_at)
        self.assertFalse(MERGER.visible('2026-10-29T00:00:00Z'))

    def test_known_and_effective_are_separate(self):
        self.assertFalse(FB.visible('2022-06-03T23:59:59Z'))
        self.assertTrue(FB.visible('2022-06-04T04:00:00Z'))
        self.assertEqual(historical_identity('META','2022-06-08')['effective_symbol'],'FB')
        self.assertEqual(historical_identity('FB','2022-06-09')['effective_symbol'],'META')
        self.assertEqual(historical_identity('FB','2022-01-03')['security_id'],historical_identity('META','2023-01-03')['security_id'])
        with self.assertRaises(ValueError): FB.visible('2022-06-04')

    def test_merger_is_not_rename_or_permission(self):
        self.assertFalse(historical_identity('XLNX','2022-02-11')['post_last_trade'])
        self.assertTrue(historical_identity('XLNX','2022-02-14')['post_last_trade'])
        self.assertFalse(historical_identity('FB','2022-01-03')['trading_eligible'])
        with self.assertRaises(ValueError): historical_identity('AMD','2022-01-03')

    def test_retrieval_counts_only_requested_valid_dates_and_never_admits(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); gaps=p/'gaps.csv'
            gaps.write_text('ticker,date\nFB,2022-01-03\nFB,2022-01-03\nXLNX,2022-02-11\nXLNX,2022-02-14\n')
            calls=[]
            def get(client,endpoint,params):
                calls.append(params.copy())
                symbol=params['symbols']
                dates=['2022-01-03'] if symbol=='FB' else ['2022-02-11','2022-02-14']
                record=dict(source_file='response.json',source_sha256='a'*64,http_status=200)
                client.requests.append(record)
                return {'bars':{symbol:[dict(t=d+'T05:00:00Z',o=2,h=3,l=1,c=2,v=5) for d in dates]}},record
            with patch('ga9.repair_ticker_identities.credentials',return_value={}),patch.object(Client,'get',get):
                r=run(gaps,p/'out')
            self.assertEqual(r['baseline_remaining'],3)
            self.assertEqual(r['raw_recovered_gaps'],2)
            self.assertEqual(r['certified_recovered_gaps'],0)
            self.assertEqual(json.loads((p/'out/accepted_raw.json').read_text()),[])
            self.assertEqual([c['symbols'] for c in calls],['FB','XLNX'])
            self.assertEqual([c['asof'] for c in calls],['2022-06-08','2022-02-11'])
            self.assertEqual(r['remaining'][0]['diagnosis'],'POST_LAST_TRADE_NO_XLNX_BAR_EXPECTED')
            self.assertEqual(r['work'][1]['unexpected_post_last_trade_bars'],['2022-02-14'])
            with self.assertRaises(FileExistsError):run(gaps,p/'out')

    def test_prior_evidence_requires_intact_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); raw=json.dumps({'bars':{'XLNX':[{'t':'2022-02-11T05:00:00Z'}]}}).encode()
            (p/'response.json').write_bytes(raw)
            rec=dict(http_status=200,source_file='response.json',source_sha256=hashlib.sha256(raw).hexdigest(),params=dict(symbols='XLNX',feed='sip',adjustment='raw',asof='2022-02-11'))
            (p/'report.json').write_text(json.dumps(dict(requests=[rec,rec])))
            self.assertEqual(prior_recoveries([p]),{('XLNX','2022-02-11')})
            (p/'response.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'hash'):prior_recoveries([p])

    def test_bounds_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); gaps=p/'gaps.csv';gaps.write_text('ticker,date\nFB,2021-12-31\n')
            with self.assertRaises(ValueError):run(gaps,p/'out')
            with self.assertRaises(ValueError):run(gaps,p/'out',budget=17)

if __name__=='__main__': unittest.main()

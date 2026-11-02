import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import socket
from ga9.alpaca_repair import Client, bars, reconcile, blocked_symbols
from ga9.nasdaq_archive import load_alpaca_diagnostics


class RepairTests(unittest.TestCase):
    def test_window_bound_before_network(self):
        with self.assertRaises(ValueError): bars(None,'QQQ','2021-12-31','2022-01-03')

    def test_request_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=Client(tmp,{},0)
            with self.assertRaisesRegex(RuntimeError,'budget'):c.get('/v2/stocks/bars',{})

    def test_dns_error_is_sanitized(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=Client(tmp,{'APCA-API-SECRET-KEY':'SENSITIVE'},1)
            with patch('urllib.request.urlopen',side_effect=urllib.error.URLError(socket.gaierror(-3,'SENSITIVE'))):
                with self.assertRaises(RuntimeError):c.get('/v2/stocks/bars',{'symbols':'QQQ'})
            self.assertNotIn('SENSITIVE',json.dumps(c.requests))
            self.assertEqual(c.requests[0]['error_type'],'URLError')

    def test_repeated_pagination_rejected(self):
        c=Client('/tmp',{},4)
        with patch.object(c,'get',return_value=({'next_page_token':'repeat'},{})):
            with self.assertRaisesRegex(ValueError,'Repeated'):c.pages('/v2/stocks/bars',{})

    def test_mapping_mismatch_blocks(self):
        b=dict(date='2022-01-03',o=2,h=3,l=1,c=2,v=20)
        variants={k:[b.copy()] for k in ('raw','split','dividend','all','unmapped')}
        variants['unmapped'][0]['c']=3
        self.assertEqual(reconcile(variants)['status'],'SYMBOL_MAPPING_MISMATCH')
        variants['split']=[]
        self.assertEqual(reconcile(variants)['status'],'INCOMPLETE_VARIANTS')

    def test_no_adj_or_action_invention(self):
        b=dict(date='2022-01-03',o=2,h=3,l=1,c=2,v=20)
        r=reconcile({k:[b.copy()] for k in ('raw','split','dividend','all','unmapped')})
        self.assertIn('REQUIRES_EVENT_LEVEL',r['actions_status'])

    def test_empty_repair_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'accepted_raw.json').write_text('[]');(p/'report.json').write_text('{"requests":[]}')
            with patch('ga9.alpaca_repair.blocked_symbols',return_value=set()):
                self.assertTrue(load_alpaca_diagnostics(p,p).empty)

    def test_quarantine_cannot_be_overridden(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'accepted_raw.json').write_text('[{"ticker":"FB","source_file":"response.json"}]')
            (p/'report.json').write_text('{"requests":[]}')
            with patch('ga9.alpaca_repair.blocked_symbols',return_value={'FB'}):
                with self.assertRaisesRegex(ValueError,'Quarantined'):load_alpaca_diagnostics(p,p)



class ActionTests(unittest.TestCase):
    def test_split_price_and_volume_must_both_reconcile(self):
        from ga9.alpaca_repair import reconcile_declared_actions
        a=dict(date='2022-01-03',o=100,h=100,l=100,c=100,v=10)
        b=dict(date='2022-01-04',o=50,h=50,l=50,c=50,v=20)
        variants={k:[a.copy(),b.copy()] for k in ('raw','split','dividend','all','unmapped')}
        variants['split'][0].update(o=50,h=50,l=50,c=50,v=20)
        event=dict(type='split',ex_date=b['date'],old_rate=1,new_rate=2,source_sha256='a'*64)
        self.assertEqual(reconcile_declared_actions(variants,[event])['checks'][0]['status'],'NUMERIC_MATCH_ONLY')
        variants['split'][0]['v']=10
        self.assertEqual(reconcile_declared_actions(variants,[event])['checks'][0]['status'],'MISMATCH')

    def test_dividend_and_unknown_event_provenance(self):
        from ga9.alpaca_repair import reconcile_declared_actions
        a=dict(date='2022-01-03',o=100,h=100,l=100,c=100,v=10)
        b=dict(date='2022-01-04',o=99,h=99,l=99,c=99,v=10)
        variants={k:[a.copy(),b.copy()] for k in ('raw','split','dividend','all','unmapped')}
        variants['dividend'][0]['c']=99
        event=dict(type='cash_dividend',ex_date=b['date'],cash=1,source_sha256='a'*64)
        self.assertEqual(reconcile_declared_actions(variants,[event])['checks'][0]['status'],'NUMERIC_MATCH_ONLY')
        del event['source_sha256']
        self.assertEqual(reconcile_declared_actions(variants,[event])['checks'][0]['status'],'UNRESOLVED')

if __name__=='__main__':unittest.main()


class WorkflowTests(unittest.TestCase):
    def test_raw_first_budget_and_admission_gate(self):
        from ga9.alpaca_repair import run
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gaps = root/'gaps.csv'
            gaps.write_text('ticker,date\nFB,2022-01-03\nAPP,2022-01-03\nAPP,2022-01-04\nAPP,2022-01-04\n')
            calls = []
            def get(client, endpoint, params):
                calls.append(params.copy())
                record = dict(source_file='response.json', source_sha256='a'*64, http_status=200)
                client.requests.append(record)
                return {'bars': {'APP': [dict(t='2022-01-03T05:00:00Z',o=2,h=3,l=1,c=2,v=5)]}}, record
            with patch('ga9.alpaca_repair.acquisition_quarantine',return_value={'FB'}), \
                 patch('ga9.alpaca_repair.blocked_symbols',return_value={'FB','APP'}), \
                 patch('ga9.alpaca_repair.credentials',return_value={}), \
                 patch.object(Client,'get',get):
                r=run(root,gaps,root/'out','unused',budget=1,max_symbols=1,max_dates=1)
            self.assertEqual([x['symbols'] for x in calls], ['APP'])
            self.assertEqual(r['raw_recovered_gaps'],1)
            self.assertEqual(r['certified_recovered_gaps'],0)
            self.assertEqual(r['accepted_raw_rows'],0)
            self.assertEqual(r['baseline_gaps'],3)
            self.assertTrue(r['budget_exhausted'])
            self.assertEqual(len(json.loads((root/'out/recovered_raw.json').read_text())),1)

    def test_cached_qqq_hash_and_unique_sessions(self):
        from ga9.alpaca_repair import reuse_benchmark
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            raw=json.dumps({'bars':{'QQQ':[{'t':'2022-01-03T05:00:00Z'}]}}).encode()
            (root/'response.json').write_bytes(raw)
            record=dict(http_status=200,endpoint='/v2/stocks/bars',source_file='response.json',
                        source_sha256=hashlib.sha256(raw).hexdigest(),
                        params=dict(symbols='QQQ',feed='sip',adjustment='raw',asof='2022-01-03'))
            (root/'report.json').write_text(json.dumps({'requests':[record,record]}))
            self.assertEqual(reuse_benchmark(root)['rows'],1)
            (root/'response.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'hash'): reuse_benchmark(root)

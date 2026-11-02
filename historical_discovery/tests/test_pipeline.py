import json
from dataclasses import replace
from unittest.mock import patch
import unittest
import tempfile
from pathlib import Path
from historical_discovery.core import Config, features, labels, universe, usable_at, timestamp, metrics
from historical_discovery.adapters import JsonAdapter, validate
from historical_discovery.fixture import synthetic, FixtureAdapter
from historical_discovery.pipeline import freeze, run, verify_freeze



class PipelineTests(unittest.TestCase):

    def test_holdouts_rejected_before_io(self):
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        for year in (2010,2011,2012,2004):
            with patch('pathlib.Path.read_text',side_effect=AssertionError('Opened file')):
                with self.assertRaises(ValueError):JsonAdapter(tmp_path/'missing').load(year)
            with self.assertRaises(ValueError):labels({},year,Config())
            with self.assertRaises(ValueError):features({},year,Config())
            with self.assertRaises(ValueError):run({year:None},tmp_path)

    def test_universe_ipo_delisting_and_types(self):
        d=synthetic(2005)
        assert 'SYN5' not in universe(d,'2005-06-30')[0]
        assert 'SYN6' not in universe(d,'2005-01-05')[0]
        assert 'SYN6' in universe(d,'2005-06-30')[0]
        assert 'SYN7' not in universe(d,'2005-12-31')[0]
        assert labels(d,2005,Config())['SYN7']['calendar_return']==-1

    def test_pit_future_reports_and_restatements(self):
        d=synthetic(2005);cfg=Config()
        before=features(d,2005,cfg)[1]
        r=dict(d['financials'][0],version=2,revenue=99999,available_at='2005-01-01',recorded_at='2005-01-01T00:00:00Z')
        d['financials'].append(r)
        future=dict(d['financials'][1],period_end='2005-01-01',available_at='2005-07-01',recorded_at='2005-07-01T00:00:00Z',revenue=99999)
        d['financials'].append(future)
        assert features(d,2005,cfg)[1]==before
        future['available_at']='2005-06-01';future['recorded_at']='2005-07-01T00:00:00Z'
        assert features(d,2005,cfg)[1]==before

    def test_date_precision_lag(self):
        row={'available_at':'2005-06-28','recorded_at':'2005-06-28T01:00:00Z'}
        assert usable_at(row,Config())==timestamp('2005-07-01T00:00:00Z')

    def test_future_prices_and_caps_do_not_change_features(self):
        d=synthetic(2005);before=features(d,2005,Config())[1]
        for p in d['prices']:
            if p['date']>'2005-06-30':
                for k in ('open','high','low','close'):p[k]*=100
        d['market_caps'].append({'id':'SYN0','date':'2005-01-01','available_at':'2006-01-01T00:00:00Z','value':999,'source':'test'})
        assert features(d,2005,Config())[1]==before

    def test_missing_is_not_zero(self):
        x=features(synthetic(2005),2005,Config())[1]
        assert x['SYN4']['revenue_growth'] is None
        assert x['SYN3']['revenue_growth'] is not None

    def test_chronological_low_high_not_unordered_extrema(self):
        d=synthetic(2005)
        rows=[p for p in d['prices'] if p['id']=='SYN0']
        for i,p in enumerate(rows):
            p.update(open=100-i*.1,close=100-i*.1,high=100-i*.1,low=100-i*.1)
        result=labels(d,2005,Config())['SYN0']
        assert result['advance']<0
        assert result['start']<result['peak']

    def test_schema_price(self):
        damage='price'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_schema_duplicate(self):
        damage='duplicate'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_schema_restatement(self):
        damage='restatement'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_schema_source(self):
        damage='source'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_schema_delisting(self):
        damage='delisting'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_schema_overlap(self):
        damage='overlap'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_schema_nan(self):
        damage='nan'
        d=synthetic(2005)
        if damage=='price':d['prices'].pop(0)
        if damage=='duplicate':d['prices'].append(d['prices'][0])
        if damage=='restatement':d['financials'][0]['revision_policy']='latest_restated'
        if damage=='source':del d['prices'][0]['source']
        if damage=='delisting':d['delistings']=[]
        if damage=='overlap':d['listings'].append(dict(d['listings'][0]))
        if damage=='nan':d['prices'][0]['close']=float('nan')
        with self.assertRaises(ValueError):validate(d,2005)

    def test_freeze_tamper_and_config(self):
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        freeze(tmp_path)
        with self.assertRaises(ValueError):verify_freeze(tmp_path,replace(Config(),top_k=1))
        path=tmp_path/'freeze.json';doc=json.loads(path.read_text());doc['arms']={};path.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):verify_freeze(tmp_path,Config())

    def test_freeze_predictions_before_labels_and_equal_intersection(self):
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        from historical_discovery import pipeline
        freeze(tmp_path)
        original=pipeline.labels
        def checked(data,year,cfg):
            assert (tmp_path/f'{year}_predictions.json').exists()
            assert not (tmp_path/f'{year}_evaluation.json').exists()
            return original(data,year,cfg)
        with patch.object(pipeline,'labels',side_effect=checked):
            reports=run({y:FixtureAdapter(y) for y in (2005,2006)},tmp_path)
        pred=json.loads((tmp_path/'2006_predictions.json').read_text())
        assert pred['training_years']==[2005]
        for candidate in Config().candidates:
            assert set(pred['scores'][candidate+'/chart'])==set(pred['scores'][candidate+'/fundamentals'])==set(pred['scores'][candidate+'/combined'])
        assert pred['missing_fundamentals']==['SYN4']
        assert reports[-1]['incremental_value']
        with self.assertRaises(FileExistsError):run({2005:FixtureAdapter(2005)},tmp_path)

    def test_metrics_hand_computed(self):
        actual={'a':{'winner':True,'rank_value':2,'peak':'2005-07-10'},'b':{'winner':False,'rank_value':0,'peak':'2005-06-01'}}
        xs={s:{'snapshot_close':10,'future_high':15} for s in actual}
        m=metrics({'a':2,'b':1},actual,xs,'2005-06-30',1)
        assert m['precision_at_k']==m['recall_at_k']==m['spearman']==1
        assert m['top'][0]['lead_days']==10 and m['top'][0]['remaining_upside']==.5

    def test_deterministic_full_pipeline(self):
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        a=tmp_path/'a';b=tmp_path/'b'
        for out in (a,b):
            freeze(out)
            run({y:FixtureAdapter(y) for y in range(2005,2010)},out)
        assert {p.name:p.read_bytes() for p in a.iterdir()}=={p.name:p.read_bytes() for p in b.iterdir()}


    def test_manifest_admission_and_json_roundtrip(self):
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        payload=tmp_path/'payload.json'
        payload.write_text(json.dumps(synthetic(2005)))
        meta={'schema_version':1,'years':[2005],'payload':'payload.json',
              'source':'invented_fixture_v1','release_date':'2026-10-30',
              'revision_policy':'original_as_reported','coverage':'synthetic only',
              'adjustment_policy':'identity synthetic',
              'historical_listing_membership':True,'includes_delistings':True,
              'corporate_actions_reconciled':True,'pit_financial_availability':True,
              'asof_adjusted_ohlcv':True,'complete_exchange_sessions':True}
        manifest=tmp_path/'manifest.json'
        manifest.write_text(json.dumps(meta))
        assert JsonAdapter(manifest).load(2005)==synthetic(2005)
        meta['years']=[2005,2010]
        manifest.write_text(json.dumps(meta))
        # An invalid partition is refused before the payload can be opened.
        payload.unlink()
        with self.assertRaises(ValueError):JsonAdapter(manifest).load(2005)
        meta['years']=[2005];meta['includes_delistings']=False
        manifest.write_text(json.dumps(meta))
        with self.assertRaises(ValueError):JsonAdapter(manifest).load(2005)

    def test_prediction_independent_of_current_future_labels(self):
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        class Changed(FixtureAdapter):
            def load(self,year):
                d=super().load(year)
                for p in d['prices']:
                    if p['date']>'2006-06-30':
                        for k in ('open','high','low','close'):p[k]*=10
                return d
        predictions=[]
        for name,adapter in [('original',FixtureAdapter(2006)),('changed',Changed(2006))]:
            out=tmp_path/name
            freeze(out)
            run({2005:FixtureAdapter(2005),2006:adapter},out)
            predictions.append(json.loads((out/'2006_predictions.json').read_text()))
        assert predictions[0]['scores']==predictions[1]['scores']
        assert predictions[0]['fits']==predictions[1]['fits']
        assert predictions[0]['input_hash']!=predictions[1]['input_hash']

    def test_split_and_dividend_reconciled_adjusted_inputs(self):
        d=synthetic(2005)
        expected=features(d,2005,Config())[1]
        # Adjustments are a provider responsibility: reconciled total-return OHLCV
        # stays on the same basis when raw-price corporate actions are present.
        d['actions']=[{'id':'SYN0','date':'2005-04-01','kind':'split',
                       'adjustment_reference':'fixture_identity_basis','source':'synthetic'},
                      {'id':'SYN0','date':'2005-05-01','kind':'dividend',
                       'adjustment_reference':'fixture_identity_basis','source':'synthetic'}]
        validate(d,2005)
        assert features(d,2005,Config())[1]==expected
        del d['actions'][0]['adjustment_reference']
        with self.assertRaises(ValueError):validate(d,2005)

    def test_audit_never_opens_payload_or_credentials(self):
        from historical_discovery.audit import audit
        tmp_path=Path(self.enterContext(tempfile.TemporaryDirectory()))
        (tmp_path/'opaque.csv').write_text('DO NOT READ')
        with patch('pathlib.Path.read_text',side_effect=AssertionError('Read payload')):
            result=audit([tmp_path])
        assert result['inventory'][str(tmp_path)]['files']==1
        assert not result['holdout_labels_accessed']


if __name__=="__main__":
    unittest.main()

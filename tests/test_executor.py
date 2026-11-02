"""Artificial fixtures only; never research observations."""
import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from sector_pipeline import executor as ex
from sector_pipeline.storage import digest, publish, resume_source
from sector_pipeline.core import metrics, technical, calendar_hac
from sector_pipeline.adapters import earnings_signal


def test_atomic_once_concurrent(tmp_path):
    path = tmp_path/'ledger.json'
    def write(i):
        try:
            publish(path,{'i':i})
            return True
        except FileExistsError:
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(write,range(32))) == 1
    assert json.loads(path.read_text())['i'] in range(32)


def test_resume_adapter_and_corrupt_checkpoint(tmp_path):
    calls = []
    def loader():
        calls.append(1)
        return {'observations':[1,2]}
    assert resume_source(tmp_path,'fixture',{'id':'A'},loader)=={'observations':[1,2]}
    resume_source(tmp_path,'fixture',{'id':'A'},loader)
    assert len(calls)==1
    path = next(tmp_path.glob('*.json'))
    data = json.loads(path.read_text()); data['payload'] = {}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='Corrupt'):
        resume_source(tmp_path,'fixture',{'id':'A'},loader)


def test_stage2_does_not_open_input(tmp_path,monkeypatch):
    monkeypatch.setattr(ex,'STATE',tmp_path)
    monkeypatch.setattr(ex,'configuration',lambda m:m)
    monkeypatch.setattr(ex,'local',lambda p:pytest.fail('blind path touched'))
    with pytest.raises(ValueError,match='SEALED'):
        ex.execute('blind.json',2,{'protocol_version':2,'stage1':list(range(2006,2016)),'stage2':list(range(2016,2027)),'contaminated_years':[2019,2020]})


def test_once_only_resume_and_configuration_binding(tmp_path,monkeypatch):
    monkeypatch.setattr(ex,'STATE',tmp_path/'state')
    monkeypatch.setattr(ex,'local',lambda p:p)
    monkeypatch.setattr(ex,'configuration',lambda m:m)
    monkeypatch.setattr(ex,'verify_coverage',lambda b,y:[])
    calls = []
    def evaluate(*a):
        calls.append(1)
        return {'summary':{'H1_1':{'complete':True,'exploratory':False,'passed':True}}}
    monkeypatch.setattr(ex,'evaluate',evaluate)
    path = tmp_path/'fixture.json'; path.write_text('{"stage":1}')
    manifest = {'protocol_version':2,'stage1':list(range(2006,2016)),'stage2':list(range(2016,2027)),'contaminated_years':[2019,2020]}
    result = ex.execute(path,1,manifest)
    assert result['valid'] and result['passers']==['H1_1']
    assert ex.execute(path,1,manifest)==result and len(calls)==1
    with pytest.raises(ValueError,match='different configuration'):
        ex.execute(path,1,dict(manifest,changed=True))
    path.write_text('{"stage":1,"changed":true}')
    with pytest.raises(ValueError,match='different configuration'):
        ex.execute(path,1,manifest)


def test_ledger_integrity(tmp_path):
    path = tmp_path/'record'
    ex.commit(path,{'passers':[]})
    record = json.loads(path.read_text()); record['body']['passers']=['H1_1']
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError,match='integrity'):
        ex.load_record(path)


def test_momentum_eleven_inclusive_monthly_returns():
    rows=[]
    for i in range(14):
        year,month=divmod(2005*12+i,12)
        rows.append({'date':f'{year}-{month+1:02d}-28','adj_close':2.0**i})
    # Formation Feb 2006: Jan-Nov 2005 returns, starting Dec 2004 close.
    assert technical(rows)['H1']==2**11-1
    del rows[0]
    assert technical(rows)['H1'] is None


def fixture_rows(dates=('2006-01-31','2006-02-28'),drift=True):
    rows=[]
    for date in dates:
        for i in range(20):
            rows.append(dict(asof=date,sector='T',horizon=1,symbol=str(i),
                excess=i/100,rebalance_return=(.5 if i==19 and drift else 0),
                **{f'H{h}_rank':(i+1)/20 for h in range(1,7)}))
    return rows


def test_weighted_drift_and_both_leg_cost():
    monthly,_=metrics(fixture_rows(),{'H1_1'})
    assert monthly[0]['turnover']==2
    assert monthly[0]['net_spread_15bps']==pytest.approx(monthly[0]['spread']-.003)
    # Two names per leg. One long appreciates 50%, shifting .5/.5 to .4/.6.
    assert monthly[1]['turnover']==pytest.approx(.2)
    assert monthly[1]['net_spread_15bps']==pytest.approx(monthly[1]['spread']-.0003)
    flat,_=metrics(fixture_rows(drift=False),{'H1_1'})
    assert flat[1]['turnover']==0


def test_gap_invalidates_turnover():
    monthly,_=metrics(fixture_rows(('2006-01-31','2006-03-31')),{'H1_1'})
    assert monthly[1]['turnover'] is None
    assert monthly[1]['net_spread_15bps'] is None


def test_actual_availability_excludes_delayed_release():
    events=[dict(reportedDate=f'2005-{i:02d}-01',reportedEPS=i,estimatedEPS=0,
                 available_at='2007-01-01T00:00:00+00:00') for i in range(1,10)]
    assert earnings_signal({'quarterlyEarnings':events},'2006-01-31') is None


def test_evidence_cannot_be_boolean(tmp_path,monkeypatch):
    monkeypatch.setattr(ex,'local',lambda p:p)
    b={'sessions':['2006-01-31'],'closes':{'2006-01-31':'2006-01-31T21:00:00Z'},'opens':{'2006-01-31':'2006-01-31T14:30:00Z'},'evidence':{'calendar':{'status':'verified'}}}
    b.update(members=[],inventory={},prices={},fundamentals={},earnings={})
    with pytest.raises(ValueError,match='Unverified source'):
        ex.verify_coverage(b,[2006])


def test_calendar_hac_does_not_bridge_exclusions():
    dates=['2018-09-30','2018-10-31','2018-11-30','2018-12-31','2021-01-31','2021-02-28']
    from sector_pipeline.core import hac
    values=[.1,.2,-.1,.3,-.2,.4]
    assert calendar_hac(dates,values,3)['se'] != hac(values,3)['se']


def test_real_evaluator_synthetic_fixture():
    import datetime as dt
    from sector_pipeline.core import form_rows
    sessions=[]
    date=dt.date(2004,10,1)
    while date<=dt.date(2006,8,31):
        if date.weekday()<5:
            sessions.append(str(date))
        date+=dt.timedelta(days=1)
    prices={}
    members=[]
    earnings={}
    fundamentals={}
    for i in range(20):
        symbol=str(i)
        prices[symbol]=[dict(date=d,adj_close=100*(1+(i+1)*.0001)**j*(1+(.001+i*.0001)*(j%3)),
                             adj_open=100*(1+(i+1)*.0001)**j) for j,d in enumerate(sessions)]
        members.append(dict(symbol=symbol,sector='T',start='2006-01-01',end='2006-02-01'))
        earnings[symbol]={'quarterlyEarnings':[dict(reportedDate=f'2005-{m:02d}-01',reportedEPS=m+i*(m%2),estimatedEPS=0) for m in range(1,10)]}
        fundamentals[symbol]={'facts':{'us-gaap':{
            'GrossProfit':{'units':{'USD':[dict(start='2004-01-01',end='2004-12-31',filed='2005-03-01',form='10-K',val=i+1)]}},
            'Assets':{'units':{'USD':[dict(end='2004-12-31',filed='2005-03-01',form='10-K',val=100)]}}}}}
    bundle=dict(sessions=sessions,closes={d:d+'T21:00:00Z' for d in sessions},prices=prices,members=members,earnings=earnings,fundamentals=fundamentals)
    result=ex.evaluate(bundle,[2006],['2006-01-31'])
    assert len(result['summary'])==18
    assert not result['missingness']
    assert all(v['placebo']['shuffles']==1000 for v in result['summary'].values() if v['placebo']['real'] is not None)
    assert any(v['placebo']['shuffles']==1000 for v in result['summary'].values())
    assert all(not v['passed'] for v in result['summary'].values()) # one month cannot establish inference
    assert len(result['decay'])==6
    assert all(v['holm_p'] is None for v in result['summary'].values())


def test_variant_registry_requires_expanded_family(tmp_path,monkeypatch):
    monkeypatch.setattr(ex,'STATE',tmp_path)
    with pytest.raises(ValueError,match='twelve'):
        ex.register_variant('variant',{},['variant'])
    family=[f'H{s}_{h}' for s in range(1,7) for h in (1,3)]+['variant']
    ex.register_variant('variant',{'frozen':True},family)
    with pytest.raises(FileExistsError):
        ex.register_variant('variant',{'changed':True},family)


def test_valid_release_passers_only_and_exclusion_controls(tmp_path,monkeypatch):
    monkeypatch.setattr(ex,'STATE',tmp_path/'state')
    monkeypatch.setattr(ex,'configuration',lambda m:m)
    monkeypatch.setattr(ex,'local',lambda p:p)
    manifest={'protocol_version':2,'stage1':list(range(2006,2016)),'stage2':list(range(2016,2027)),'contaminated_years':[2019,2020]}
    config_hash=digest(manifest)
    claim={'configuration_hash':config_hash,'input_hash':'fixture'}
    ex.commit(ex.STATE/'stage1-claim.json',claim)
    summaries={f'H{s}_{h}':dict(mean=.02,t=3.2,positive_blocks=3,complete=True,placebo_pass=True,exploratory=False)
               for s in range(1,7) for h in (1,3)}
    for key,value in summaries.items():
        if key!='H1_1':
            value['mean']=0
    ex.commit(ex.STATE/'stage1-result.json',dict(configuration_hash=config_hash,claim_hash=digest(claim),valid=True,
              passers=['H1_1'],result={'summary':summaries}))
    path=tmp_path/'blind-fixture.json';path.write_text('{"stage":2}')
    monkeypatch.setattr(ex,'verify_coverage',lambda *a:['2018-12-31','2019-01-31','2021-01-31'])
    calls=[]
    def evaluate(bundle,years,dates,allowed):
        calls.append((years,dates,allowed))
        return {'summary':{'H1_1':dict(complete=True,exploratory=False,passed=2019 in years)}}
    monkeypatch.setattr(ex,'evaluate',evaluate)
    result=ex.execute(path,2,manifest)
    assert result['passers']==[] # Full-period pass cannot override excluded-year failure.
    assert len(calls)==2 and all(c[2]==['H1_1'] for c in calls)
    assert 2019 not in calls[1][0] and 2020 not in calls[1][0]
    assert calls[1][1]==['2018-12-31','2021-01-31']


def test_missing_entire_month_is_in_missingness_ledger():
    bundle={'members':[dict(symbol='delisted',start='2006-01-01',end='2007-01-01')]}
    ledger=ex.missingness(bundle,[],['2006-01-31'])
    assert len(ledger)==3 and all(r['symbol']=='delisted' for r in ledger)


def test_primary_holm_family_remains_twelve_with_missing_tests():
    from sector_pipeline.core import holm
    assert holm({'H6_1':.01,'H1_1':None},family_size=12)=={'H6_1':.12}


def test_within_sector_ic_equal_monthly_sector_weighting():
    rows=fixture_rows(('2006-01-31',))
    # A larger second sector with perfect inverse ordering must have equal weight.
    for i in range(40):
        rows.append(dict(asof='2006-01-31',sector='U',horizon=1,symbol='u'+str(i),
                         H1_rank=(i+1)/40,excess=-i,rebalance_return=0))
    monthly,summary=metrics(rows,{'H1_1'})
    assert [r['ic'] for r in monthly]==pytest.approx([1,-1])
    assert summary['H1_1']['mean']==pytest.approx(0)


def test_full_coverage_verifier_and_terminal_availability(tmp_path,monkeypatch):
    import datetime as dt
    from sector_pipeline.storage import file_hash
    monkeypatch.setattr(ex,'local',lambda p:p)
    dates=[]
    day=dt.date(2004,10,1)
    while day<=dt.date(2007,7,3):
        if day.weekday()<5:
            dates.append(str(day))
        day+=dt.timedelta(days=1)
    closes={d:d+'T21:00:00Z' for d in dates}; opens={d:d+'T14:30:00Z' for d in dates}
    months={d[:7]:d for d in dates}
    members=[dict(symbol='fixture',identity='fixture-only',sector='T',start='2006-01-01',end='2007-01-01',available_at='2005-01-01T00:00:00Z')]
    bundle=dict(sessions=dates,closes=closes,opens=opens,members=members,
                inventory={d:['fixture'] for m,d in months.items() if m.startswith('2006')},
                prices={'fixture':[dict(date=d,adj_open=100,adj_close=101,available_at=closes[d],open_available_at=opens[d]) for d in dates]},
                fundamentals={},earnings={'fixture':{'quarterlyEarnings':[dict(available_at='2005-01-01T00:00:00Z')]}})
    def bind():
        normalized=dict(calendar=dict(sessions=dates,closes=closes,opens=opens),membership=dict(members=members,inventory=bundle['inventory']),
                        gics=members,identities=members,prices=bundle['prices'],fundamentals=bundle['fundamentals'],earnings=bundle['earnings'])
        bundle['evidence']={}
        for kind,value in normalized.items():
            path=tmp_path/(kind+'.json')
            path.write_text(json.dumps({'normalized_hash':digest(value),'notice':'ARTIFICIAL TEST FIXTURE'}))
            bundle['evidence'][kind]=dict(status='verified',reviewer='fixture-test',method='fixture-only',provider='fixture',path=path,sha256=file_hash(path))
    bind()
    assert len(ex.verify_coverage(bundle,[2006]))==12
    # A rebound source still fails semantic checks when a terminal quote is missing.
    lost=bundle['prices']['fixture'].pop(-1)
    bind()
    # Lost July date lies beyond all June endpoints, so target a required June date.
    required=next(r for r in bundle['prices']['fixture'] if r['date']=='2007-06-29')
    bundle['prices']['fixture'].remove(required)
    bind()
    with pytest.raises(ValueError,match='terminal price'):
        ex.verify_coverage(bundle,[2006])
    bundle['prices']['fixture'].append(required)
    bundle['prices']['fixture'].sort(key=lambda r:r['date'])
    required['open_available_at']='2008-01-01T00:00:00Z';bind()
    with pytest.raises(ValueError,match='Open availability'):
        ex.verify_coverage(bundle,[2006])

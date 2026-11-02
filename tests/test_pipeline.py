import datetime as dt
import json
import pytest
from sector_pipeline.adapters import ROOT, local, sec_quality, earnings_signal
from sector_pipeline.core import ranks, technical, price_issues, hac, holm, form_rows


def test_rank_ties_missing():
    assert ranks([1,1,3,None]) == [.5,.5,1,None]


def test_no_fundamentals_fabricated():
    assert sec_quality({},'2019-01-01') is None
    assert earnings_signal({},'2019-01-01') is None


def test_filing_lookahead_and_restatement():
    facts = {'facts':{'us-gaap':{'GrossProfit':{'units':{'USD':[dict(start='2017-01-01',end='2017-12-31',filed='2018-03-01',form='10-K',val=20),dict(start='2017-01-01',end='2017-12-31',filed='2020-01-01',form='10-K/A',val=90)]}},'Assets':{'units':{'USD':[dict(end='2017-12-31',filed='2018-03-01',form='10-K',val=100)]}}}}}
    assert sec_quality(facts,'2018-03-01') is None
    assert sec_quality(facts,'2019-01-01') == .2


def test_earnings_date_conservative():
    data = {'quarterlyEarnings':[dict(reportedDate=f'2018-0{i}-01',reportedEPS=i,estimatedEPS=0) for i in range(1,7)]}
    assert earnings_signal(data,'2018-05-01') is None
    assert earnings_signal(data,'2018-06-01') is None


def test_frozen_splits():
    m = json.loads((ROOT/'manifest.json').read_text())
    assert m['protocol_version'] == 2
    assert m['stage1'] == list(range(2006,2016))
    assert m['stage2'] == list(range(2016,2027))
    assert m['contaminated_years'] == [2019,2020]
    assert m['stage2_sealed'] and not m['certified']


def test_no_mts_contamination():
    for path in ['/opt/mts/DEV79/data.csv', ROOT/'secrets/key', ROOT/'../outside.csv']:
        with pytest.raises(ValueError):
            local(path)
    assert local(ROOT/'reports') == ROOT/'reports'


def test_corporate_action_gaps_and_adjustments():
    rows = [dict(date='2019-01-01',adj_close=50,close=100),dict(date='2019-01-02',adj_close=50,close=50)]
    assert not price_issues({'A':rows})  # adjusted split has no artificial return
    rows.append(dict(date='2019-02-01',adj_close=5))
    assert len(price_issues({'A':rows})) == 1


def test_signal_windows_no_future():
    h = [dict(date=f'{year}-{month:02d}-28',adj_close=i+1)
         for i,(year,month) in enumerate(( (2018+i//12, i%12+1) for i in range(26)))]
    assert technical(h)['H1'] == 24/13-1
    assert technical(h)['H2'] is None
    daily = [dict(adj_close=i+1) for i in range(253)]
    assert technical(daily)['H2'] == 1
    assert technical(daily)['H5'] > 0


def test_hac_and_holm():
    assert hac([1,2],5)['p'] is None
    assert holm({'a':.01,'b':.03,'c':None}) == {'a':.02,'b':.03}


def test_membership_and_next_open():
    rows = []
    day = dt.date(2018,1,1)
    for i in range(1000):
        d = day+dt.timedelta(days=i)
        if d.weekday()<5:
            rows.append(dict(date=str(d),adj_close=100,adj_open=80))
    members = [dict(symbol='A',sector='Tech',start='2019-01-01',end='2019-02-01')]
    result = form_rows({'A':rows},members,[2019],{}, {})
    assert len(result)==3
    assert all(r['asof']=='2019-01-31' and r['forward_return']==.25 for r in result)


def test_terminal_missingness_does_not_change_formation_ranks():
    day = dt.date(2018,1,1)
    a, b = [], []
    for i in range(1000):
        d = day+dt.timedelta(days=i)
        if d.weekday()<5:
            a.append(dict(date=str(d),adj_close=100+i,adj_open=100+i))
            if d < dt.date(2019,2,1):
                b.append(dict(date=str(d),adj_close=100,adj_open=100))
    members = [dict(symbol=s,sector='Tech',start='2019-01-01',end='2019-02-01') for s in ('A','B')]
    result = form_rows({'A':a,'B':b},members,[2019],{}, {})
    assert result and all(r['symbol']=='A' and r['H2_rank']==.75 and r['excess'] is None for r in result)


def test_blind_cli_rejects_before_reading_inputs(tmp_path):
    import subprocess
    import sys
    r = subprocess.run([sys.executable,'-m','sector_pipeline','run','--prices','absent.csv','--members','absent.csv','--years','2016'],capture_output=True,text=True,cwd=ROOT)
    assert r.returncode == 2
    assert 'Stage2 SEALED' in r.stderr


def test_eight_prior_surprises_exact():
    import statistics
    events = [dict(reportedDate=f'2018-{i:02d}-01',reportedEPS=i,estimatedEPS=0) for i in range(1,10)]
    assert earnings_signal({'quarterlyEarnings':events},'2018-09-01') is None
    assert earnings_signal({'quarterlyEarnings':events},'2018-09-02') == 9/statistics.stdev(range(1,9))
    events[0]['reportedEPS'] = 'None'
    assert earnings_signal({'quarterlyEarnings':events},'2018-09-02') is None


def test_stage_gates_and_seal():
    from sector_pipeline.gate import stage_gate, authorize
    good = dict(mean=.02,t=3.1,positive_blocks=3,complete=True,placebo_pass=True)
    assert stage_gate(good)
    for key,value in [('mean',.01),('t',3),('positive_blocks',2),('complete',False),('placebo_pass',False)]:
        assert not stage_gate(dict(good,**{key:value}))
    assert stage_gate(dict(good,t=2.1,same_sign=True,net_spread=.001),2)
    assert not stage_gate(dict(good,t=2.1,same_sign=True,net_spread=0),2)
    m = json.loads((ROOT/'manifest.json').read_text())
    for years in ([2006],[2016],[2019],[2026],[2006,2016]):
        with pytest.raises(ValueError):
            authorize(years,m)


def test_missing_open_has_no_proxy():
    rows = [dict(date='2019-01-31',adj_close=100),dict(date='2019-02-01',adj_close=100),dict(date='2019-03-31',adj_close=100)]
    assert not form_rows({'A':rows},[dict(symbol='A',sector='T',start='2019-01-01',end='2019-02-01')],[2019],{}, {})


def test_placebo_direction():
    from sector_pipeline.core import placebo
    rows = [dict(asof='2006-01-31',sector='T',horizon=1,H5_rank=(i+1)/20,excess=-i) for i in range(20)]
    result = placebo(rows,'H5',1)
    assert result['real'] == pytest.approx(1) and result['passed'] and result['shuffles'] == 1000

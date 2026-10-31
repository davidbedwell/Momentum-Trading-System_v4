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
    assert earnings_signal(data,'2018-06-01') is not None


def test_frozen_splits():
    m = json.loads((ROOT/'manifest.json').read_text())
    assert len(m['discovery']) == len(m['blind']) == 4
    assert not set(m['discovery']) & set(m['blind'])
    assert not {2019,2020} & set(m['blind'])
    assert m['holdout_locked']


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
    h = [dict(adj_close=i+1) for i in range(253)]
    assert technical(h)['H1'] == 232/1-1
    assert technical(h)['H2'] == 253/190-1
    assert technical(h)['H3'] == 1


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
    assert result and all(r['symbol']=='A' and r['H2_rank']==1 for r in result)


def test_blind_cli_rejects_before_reading_inputs(tmp_path):
    import subprocess
    import sys
    r = subprocess.run([sys.executable,'-m','sector_pipeline','run','--prices','absent.csv','--members','absent.csv','--years','2015'],capture_output=True,text=True,cwd=ROOT)
    assert r.returncode == 2
    assert 'Blind years are locked' in r.stderr

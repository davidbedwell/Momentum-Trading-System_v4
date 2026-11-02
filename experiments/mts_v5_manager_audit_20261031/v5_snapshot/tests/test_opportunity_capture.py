import pytest
from discovery.competitive_ga.opportunity_capture import FundingDecision,summarize

def test_funding_capture_reports_shortfall_without_invented_profit():
    rows=[FundingDecision('2026-01-02','AAA',('HORIZONS','h'),.1,.04,.04,.3,'SETTLED_CASH'),
          FundingDecision('2026-01-02','BBB',('GA7','g'),.1,.1,.1,.3,'FUNDED')]
    report=summarize(rows)
    assert report['underfunded_requests']==1
    assert abs(report['capture_fraction']-.7)<1e-10
    assert abs(report['missed_weight_sum']-.06)<1e-10
    assert report['reasons']=={'SETTLED_CASH':1}
    assert 'missed_profit' not in report

def test_empty_demand_and_invalid_funding():
    assert summarize([])['capture_fraction'] is None
    with pytest.raises(ValueError):
        FundingDecision('2026-01-02','AAA',('GA6','x'),.1,.2,.1,0,'BAD')

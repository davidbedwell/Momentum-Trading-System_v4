import pandas as pd
import pytest
from discovery.competitive_ga.first_year_earnings import native_earnings_clear, SOURCES
from discovery.competitive_ga.first_year_manifest import digest

D=('2026-01-02','2026-01-05','2026-01-06','2026-01-07','2026-01-08')


def inputs():
    events=pd.DataFrame([dict(ticker='A',event_date='2026-01-04',available_at='2026-01-01T12:00:00Z',source_hash='fixture')])
    coverage=pd.DataFrame([dict(ticker=t,schedule_through=D[-1],available_at='2026-01-01T12:00:00Z',source_hash='fixture') for t in ('A','B')])
    return events,coverage


def call(events,coverage,contract='ga5_immutable_1_session',date=D[0]):
    return native_earnings_clear(events=events,coverage=coverage,sessions=D,tickers=('A','B'),decision_date=date,
        decision_at=date+'T21:00:00Z',contract=contract,source_hash=digest(SOURCES[contract]))


@pytest.mark.parametrize('contract',SOURCES)
def test_authentic_weekend_report_uses_selected_native_session_embargo(contract):
    events,coverage=inputs()
    assert call(events,coverage,contract)==dict(A=False,B=True)
    # The future-study GA6 version blocks one additional following session.
    assert call(events,coverage,contract,date=D[3])['A']==(contract=='ga5_immutable_1_session')


def test_unpublished_event_is_not_retroactively_visible():
    events,coverage=inputs();events.loc[0,'available_at']='2026-01-05T20:00:00Z'
    assert call(events,coverage)==dict(A=True,B=True)


@pytest.mark.parametrize('kind',['no_coverage','future_coverage','short_coverage','missing_event_time'])
def test_earnings_absence_requires_causal_coverage(kind):
    events,coverage=inputs()
    if kind=='no_coverage':coverage=coverage.iloc[:1]
    if kind=='future_coverage':coverage.loc[0,'available_at']='2026-01-03T00:00:00Z'
    if kind=='short_coverage':coverage.loc[0,'schedule_through']=D[1]
    if kind=='missing_event_time':events.loc[0,'available_at']=None
    with pytest.raises(ValueError):call(events,coverage)

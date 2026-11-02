"""Entirely invented securities and prices; no real winner lists or market data."""
from copy import deepcopy
from datetime import date, timedelta
from .core import development_year
from .adapters import validate


def synthetic(year):
    development_year(year)
    days=[]
    day=date(year,1,1)
    while day.year==year:
        if day.weekday()<5:days.append(day.isoformat())
        day+=timedelta(days=1)
    source='invented_fixture_v1'
    data={k:[] for k in ('listings','prices','financials','market','actions','delistings','sessions','market_caps')}
    for exchange in ('NYSE','NASDAQ'):
        data['sessions'].extend({'exchange':exchange,'date':d,'source':source} for d in days)
    data['market']=[{'date':d,'close':100+i/20,'source':source} for i,d in enumerate(days)]
    for j in range(8):
        sid=f'SYN{j}'
        start=days[30] if j==6 else days[0]
        end=days[-30] if j==7 else days[-1]
        data['listings'].append({'id':sid,'ticker':f'FAKE{j}','start':start,'end':end,
                                 'end_reason':'delisting' if j==7 else 'partition_boundary',
                                 'exchange':'NYSE' if j%2 else 'NASDAQ','kind':'common' if j!=5 else 'etf','source':source})
        rate=[1.8,-.55,.9,.05,-.25,.4,1.2,-.8][j]
        for i,d in enumerate(days):
            if not start<=d<=end:continue
            close=20*(1+rate*i/(len(days)-1))
            data['prices'].append({'id':sid,'date':d,'open':close*.999,'high':close*1.01,'low':close*.99,
                                   'close':close,'volume':1000*(j+1),'source':source})
        if j==7:
            data['delistings'].append({'id':sid,'date':end,'terminal_adjusted_value':0,'source':source})
        if j!=4:
            for lag in (2,1):
                data['financials'].append({'id':sid,'period_end':f'{year-lag}-12-31','period_type':'annual',
                    'available_at':f'{year-lag+1}-03-01','recorded_at':f'{year-lag+1}-03-01T12:00:00Z',
                    'revenue':100 if lag==2 else 100+rate*30,'version':1,'revision_policy':'original_as_reported','source':source})
        data['market_caps'].append({'id':sid,'date':days[0],'available_at':days[0]+'T21:00:00Z','value':1e6*(j+1),'source':source})
    return validate(data,year)


class FixtureAdapter:
    def __init__(self, year):
        development_year(year)
        self.year=year
    def load(self,year):
        development_year(year)
        if year!=self.year:raise ValueError('Wrong partition')
        return deepcopy(synthetic(year))
    def provenance(self):
        return {'source':'invented_fixture_v1','synthetic':True,'years':[self.year],
                'release_date':'2026-10-30','coverage':'Invented weekday sessions; not an exchange calendar',
                'revision_policy':'original_as_reported','adjustment_policy':'Identity; synthetic corporate actions absent'}

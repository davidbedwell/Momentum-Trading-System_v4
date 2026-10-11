"""Read-only, date-exact Stage1 contextual metadata join for DEV80 evidence."""
import pandas as pd

SECTOR_ETF={'Basic Materials':'XLB','Communication Services':'XLC','Consumer Cyclical':'XLY','Consumer Defensive':'XLP','Energy':'XLE','Financial Services':'XLF','Healthcare':'XLV','Industrials':'XLI','Real Estate':'XLRE','Technology':'XLK','Utilities':'XLU'}

def attach_context(predictors, galaxy, sectors):
    required={'security_id','effective_date','sector_id'}
    if not required.issubset(predictors.columns):raise ValueError('Missing stock alignment keys')
    if not {'date','state','strength','trajectory','rv20'}.issubset(galaxy.columns):raise ValueError('Missing Galaxy fields')
    if not {'date','context_key','state','strength','trajectory','rv20','rel20','rel60'}.issubset(sectors.columns):raise ValueError('Missing Sector fields')
    d=predictors[['security_id','effective_date','sector_id']].copy()
    if d.duplicated(['security_id','effective_date']).any():raise ValueError('Duplicate stock/date')
    d['effective_date']=pd.to_datetime(d.effective_date)
    d['sector_etf']=d.sector_id.map(SECTOR_ETF)
    if d.sector_id.notna().any() and d.loc[d.sector_id.notna(),'sector_etf'].isna().any():raise ValueError('Unmapped sector')
    g=galaxy[['date','state','strength','trajectory','rv20']].copy()
    s=sectors[['date','context_key','state','strength','trajectory','rv20','rel20','rel60']].copy()
    g['date']=pd.to_datetime(g.date);s['date']=pd.to_datetime(s.date)
    if g.date.duplicated().any() or s.duplicated(['date','context_key']).any():raise ValueError('Duplicate context date')
    g=g.rename(columns={'date':'effective_date',**{x:'galaxy_'+x for x in ['state','strength','trajectory','rv20']}})
    s=s.rename(columns={'date':'effective_date','context_key':'sector_etf',**{x:'sector_'+x for x in ['state','strength','trajectory','rv20','rel20','rel60']}})
    out=d.merge(g,on='effective_date',how='left',validate='many_to_one').merge(s,on=['effective_date','sector_etf'],how='left',validate='many_to_one')
    if len(out)!=len(d):raise ValueError('Context join changed row count')
    return out

"""PROVISIONAL free-source Stage1. Never accesses the certified ledger or Stage2."""
import argparse
import copy
import datetime as dt
import json
import statistics
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser
from . import adapters, core
from .storage import resume_source, digest
from .executor import lookahead

WARNING = ('PROVISIONAL exploratory only; not certified PIT. Wikipedia reconstructed membership is incomplete; '
           'historical sectors use current Wikipedia proxies where available, otherwise UNKNOWN. '
           'Yahoo retrospective adjustments, missing delisted securities and terminal prices, SEC companyfacts '
           'retrieval vintages and Alpha Vantage coverage cause source/availability/survivorship bias. '
           'No exploratory result releases Stage2. 2019/2020 remain contaminated.')

class Tables(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables=[]; self.table=None; self.row=None; self.cell=None; self.spans={}; self.colspan=1; self.rowspan=1
    def handle_starttag(self, tag, attrs):
        if tag=='table': self.table=[]; self.spans={}
        elif tag=='tr' and self.table is not None: self.row=[]
        elif tag in ('td','th') and self.row is not None:
            self.cell=''; a=dict(attrs); self.colspan=int(a.get('colspan',1)); self.rowspan=int(a.get('rowspan',1))
    def handle_data(self, data):
        if self.cell is not None: self.cell+=data
    def handle_endtag(self, tag):
        if tag in ('td','th') and self.cell is not None:
            while len(self.row) in self.spans:
                col=len(self.row); value,remaining=self.spans.pop(col); self.row.append(value)
                if remaining>1: self.spans[col]=(value,remaining-1)
            for _ in range(self.colspan):
                col=len(self.row); self.row.append(self.cell.strip())
                if self.rowspan>1: self.spans[col]=(self.cell.strip(),self.rowspan-1)
            self.cell=None
        elif tag=='tr' and self.row is not None:
            self.table.append(self.row); self.row=None
        elif tag=='table' and self.table is not None:
            self.tables.append(self.table); self.table=None

def wikipedia():
    url='https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:
        html=r.read().decode()
    p=Tables(); p.feed(html)
    current=next(t for t in p.tables if t and t[0][:1]==['Symbol'])
    changes=next(t for t in p.tables if t and 'Added' in t[0] and 'Removed' in t[0])
    return dict(url=url,retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),html=html,current=current,changes=changes)

def reconstruct(wiki):
    current={r[0]:r for r in wiki['current'][1:] if len(r)>=7}
    sectors={s:r[2] for s,r in current.items()}
    ciks={s:r[6] for s,r in current.items() if r[6].isdigit()}
    active={s:'9999-12-31' for s in current}; intervals=[]; failures=[]
    changes=[]
    for r in wiki['changes']:
        if len(r)<5: continue
        try: date=str(dt.datetime.strptime(r[0],'%B %d, %Y').date())
        except ValueError: continue
        changes.append((date,r[1],r[3]))
    if not changes: raise ValueError('Wikipedia changes table parsed zero events')
    for date,added,removed in sorted(changes,reverse=True):
        if added:
            end=active.pop(added,None)
            if end: intervals.append(dict(symbol=added,start=date,end=end))
            else: failures.append(dict(date=date,symbol=added,issue='addition absent during reverse reconstruction'))
        if removed:
            if removed in active: failures.append(dict(date=date,symbol=removed,issue='duplicate removal'))
            else: active[removed]=date
    intervals += [dict(symbol=s,start='1900-01-01',end=e) for s,e in active.items()]
    for m in intervals:
        m.update(sector=sectors.get(m['symbol'],'UNKNOWN'),sector_provenance='current proxy' if m['symbol'] in sectors else 'missing',identity=m['symbol'])
    return intervals,ciks,failures

def run(out, symbols=None, start='2006', end='2015'):
    if not 2006 <= int(start) <= int(end) <= 2015: raise ValueError('Exploration restricted to Stage1 2006–2015')
    out=adapters.local(out); out.mkdir(parents=True,exist_ok=True); cache=out/'cache'
    errors=[]
    def get(provider,request,loader):
        try: return resume_source(cache,provider,request,loader)
        except Exception as exc:
            errors.append(dict(provider=provider,request=request,error=(type(exc).__name__+': '+str(exc))[:240])); return None
    wiki=get('wikipedia',{'page':'S&P500'},wikipedia)
    if wiki is None:
        report=dict(label=WARNING,status='BLOCKED: Wikipedia unavailable',stage2='SEALED',attempted_at=dt.datetime.now(dt.timezone.utc).isoformat(),errors=errors)
        (out/'report.json').write_text(json.dumps(report,indent=2)); return report
    members,ciks,reconstruction_errors=reconstruct(wiki)
    inventory=[m for m in members if m['start'] < f'{int(end)+1}-01-01' and m['end'] > f'{start}-01-01']
    universe=sorted({m['symbol'] for m in inventory})
    selected=universe if symbols is None else [s for s in symbols if s in universe]
    (out/'inventory.json').write_text(json.dumps(dict(label=WARNING,members=inventory,selected=selected,reconstruction_errors=reconstruction_errors),indent=2))
    prices={}; fundamentals={}; earnings={} 
    for s in selected:
        request=dict(symbol=s.replace('.','-'),start=f'{int(start)-2}-01-01',end=f'{int(end)+1}-07-02')
        prices[s]=get('yahoo',request,lambda r=request:adapters.yahoo(**r)) or []
        if s in ciks:
            data=get('sec',dict(cik=ciks[s]),lambda s=s:adapters.sec_companyfacts(ciks[s]))
            if data: fundamentals[s]=data
        else: errors.append(dict(provider='sec',symbol=s,error='No current Wikipedia CIK; historical identity unresolved'))
        data=get('alpha',dict(symbol=s),lambda s=s:adapters.alpha_earnings(s))
        if data: earnings[s]=data
        print(json.dumps(dict(symbol=s,prices=len(prices[s]),sec=s in fundamentals,earnings=s in earnings)),flush=True)
    # Never derive observations for absent symbols/tags/events. Date availability remains filing+1 / report+1.
    years=list(range(int(start),int(end)+1))
    rows=core.form_rows(prices,inventory,years,fundamentals,earnings)
    scenarios={}
    for name,known,balanced in [('available',False,False),('complete_H1_H3_H4_H5',True,False),('balanced_price_coverage',False,True)]:
        chosen=copy.deepcopy([r for r in rows if r['sector']!='UNKNOWN'])
        if known: chosen=[r for r in chosen if all(r[k+'_rank'] is not None for k in ('H1','H3','H4','H5'))]
        if balanced:
            dates={r['asof'] for r in rows}
            counts=defaultdict(set)
            for r in rows: counts[r['symbol']].add(r['asof'])
            chosen=[r for r in chosen if counts[r['symbol']]==dates]
        groups=defaultdict(list)
        for r in chosen: groups[r['asof'],r['sector'],r['horizon']].append(r)
        # Explicit available-stock sector median sensitivity; primary frozen signal definitions unchanged.
        for g in groups.values():
            median=statistics.median(r['forward_return'] for r in g)
            for r in g: r['excess']=r['forward_return']-median
        monthly,summary=core.metrics(chosen)
        for key,value in summary.items():
            signal,h=key.split('_')
            value['placebo']=core.placebo(chosen,signal,int(h),shuffles=1000)
            direction=-1 if signal=='H5' else 1
            value['direction_oriented_mean']=value['mean']*direction if value['mean'] is not None else None
            value['direction_oriented_t']=value['t']*direction if value['t'] is not None else None
            value['frozen_numeric_thresholds_met']=(int(h) in (1,3) and value['direction_oriented_mean'] is not None and value['direction_oriented_mean']>.01 and value['direction_oriented_t'] is not None and value['direction_oriented_t']>3 and value['positive_blocks']>=3 and value['placebo']['passed'])
            value['certified_pass']=False
        scenarios[name]=dict(summary=summary,monthly=monthly,lookahead=lookahead(chosen))
    coverage=[]
    sessions=sorted({r['date'] for v in prices.values() for r in v}); months={d[:7]:d for d in sessions if int(d[:4]) in years}
    for date in months.values():
        expected={m['symbol'] for m in inventory if m['start']<=date<m['end']}
        present={s for s,v in prices.items() if any(r['date']==date for r in v)} & expected
        coverage.append(dict(asof=date,reconstructed_members=len(expected),priced=len(present),missing_symbols=sorted(expected-present),available_outcomes={str(h):sum(r['asof']==date and r['horizon']==h for r in rows) for h in (1,3,6)},signal_available={s:sum(r['asof']==date and r['horizon']==1 and r[s+'_rank'] is not None for r in rows) for s in core.SIGNALS},unknown_sector=sum(m['sector']=='UNKNOWN' for m in inventory if m['start']<=date<m['end'])))
    report=dict(label=WARNING,status=('BLOCKED: no evaluable known-sector real-data rows' if not any(r['sector']!='UNKNOWN' for r in rows) else ('PROVISIONAL pilot' if symbols is not None else 'PROVISIONAL Stage1')),stage2='SEALED; exploratory results never authorize release',years=years,selected=selected,reconstructed_universe=len(universe),reconstruction_errors=reconstruction_errors,coverage=coverage,errors=errors,source_hashes=dict(wikipedia=digest(wiki)),signal_rows={s:sum(r[s+'_rank'] is not None for r in rows if r['horizon']==1) for s in core.SIGNALS},strict_full_membership_benchmark_rows=sum(r['excess'] is not None for r in rows),scenarios=scenarios)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    return report

def main():
    p=argparse.ArgumentParser(description=WARNING); p.add_argument('--out',required=True); p.add_argument('--symbols',help='comma separated pilot; omit for full reconstructed Stage1'); p.add_argument('--start',default='2006'); p.add_argument('--end',default='2015')
    a=p.parse_args(); r=run(a.out,a.symbols.split(',') if a.symbols else None,a.start,a.end)
    print(json.dumps({k:r[k] for k in ('status','label')},indent=2))
    if r['status'].startswith('BLOCKED'): raise SystemExit(2)
if __name__=='__main__': main()

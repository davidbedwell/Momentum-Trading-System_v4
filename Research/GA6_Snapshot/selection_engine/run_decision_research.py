"""Chronological GA6 all-candidate decision capture. RESEARCH ONLY.
No allocation, no fills, no shadow outcomes, no validated predictive scoring.
Frozen retrospective niche centers prevent OOS performance claims.
"""
import argparse,csv,json,hashlib
from pathlib import Path
import pandas as pd
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from research_niche_recognizer import label_frame
from niche_signal_adapter import evaluate_all
from learning_ledger import LearningLedger
ROOT=Path('/opt/mts')
SOURCES={'DEV79':'ga5_redesign/exploratory79_ga4_enriched.parquet','DEV87':'thunder-migration/mts-certification-20261011/dev87/dev87_ga6_enriched.parquet','DEV50b':'ga6_h/dev50b/DEV50b_enriched.parquet'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--cohort',choices=SOURCES,default='DEV79');p.add_argument('--symbols',type=int,default=1);p.add_argument('--start',default='2024-01-01');p.add_argument('--end',default='2024-03-01');p.add_argument('--out',default='/opt/mts/ga6_h/selection_engine/research_decisions.sqlite');a=p.parse_args()
 if a.symbols<1:raise ValueError('symbols must be positive')
 cp=json.loads((ROOT/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text())
 if cp['generation']!=269 or len(cp['members'])!=400:raise ValueError('checkpoint mismatch')
 candidates=[StructuralCandidate.restore(z) for z in cp['members']]
 frame=pd.read_parquet(ROOT/SOURCES[a.cohort]);names=sorted(frame.ticker.unique())[:a.symbols]
 # Retain pre-start rows for rolling indicators and niche warmup.
 frame=frame[(frame.ticker.isin(names))&(frame.date<a.end)].sort_values(['ticker','date'])
 labels=label_frame(frame)
 labels=labels[(labels.date>=a.start)&(labels.date<a.end)]
 lookup={(str(r.date)[:10],r.ticker):r for r in labels.itertuples(index=False)}
 ledger=LearningLedger(a.out);decisions=0;counts={};signal_counts={}
 try:
  for row in frame.itertuples(index=False):
   ds=str(row.date)[:10];key=(ds,row.ticker)
   if key not in lookup:continue
   label=lookup[key];market=row._asdict()
   if not pd.notna(market.get('adj_close')):continue
   result=evaluate_all(asof=ds,symbol=row.ticker,market_features=market,recognized_niches={label.research_niche},niche_evidence_cutoff=ds,candidates=candidates,close_price=float(market['adj_close']))
   counts[label.research_niche]=counts.get(label.research_niche,0)+1
   for d in result['decisions']:
    key_id=hashlib.sha256(f"{a.cohort}|{ds}|{row.ticker}|{d['identity']}".encode()).hexdigest()
    ledger.record_decision(decision_id=key_id,asof=ds,symbol=row.ticker,niche=d['niche'],chromosome=d['chromosome'],action=d['action'],features=d['features'],proposal={'raw_weight':d['raw_weight'],'niche_distance':float(label.niche_distance),'status':'UNSCORED_SHADOW_DECISION'},selected=False,evidence_cutoff=ds)
    decisions+=1;signal_counts[d['action']]=signal_counts.get(d['action'],0)+1
 finally:ledger.close()
 print(json.dumps({'status':'RESEARCH_ONLY_DECISIONS_NO_FILLS','cohort':a.cohort,'symbols':names,'start':a.start,'end_exclusive':a.end,'niche_days':counts,'decisions':decisions,'actions':signal_counts,'output':a.out,'limitations':['retrospective niche centers','flat-position signals only','no executed trades or learned ranking','not certified PIT or OOS']},indent=2))
if __name__=='__main__':main()

"""Daily-qualified A v2 and frozen B/B1/C/R1 declarations for GA6.
No intraday or live data promise. Signal from close is actionable next session.
"""
from pathlib import Path
import pandas as pd
from ga6.abc_b1_r1_state_controller import build_state_tape
ROOT=Path('/opt/mts')
BASE=ROOT/'thunder-migration/mts-certification-20261011/isolated_abc_b1_r1_20261022/COMBINED_STATE_TAPE.csv'
FAST=ROOT/'crash-defense-intraday-2020/STRICT4_SPY_DAILY_ALL_HISTORY.csv'
def build_revised_daily_state():
 b=pd.read_csv(BASE,parse_dates=['date']).set_index('date')
 p=pd.read_csv(FAST,parse_dates=['date']).set_index('date')
 if not b.index.equals(p.index):raise ValueError('unaligned daily inputs')
 required=['funding_pct','vvix_pct','b20_badpct','drawdown_badpct','spy_down10']
 if any(v not in p for v in required):raise ValueError('missing Path A inputs')
 ranks=p[required[:4]].ge(.95).all(axis=1)
 fast=(ranks&p.spy_down10.le(-.10)).fillna(False)
 rows=[dict(date=str(d.date()),A=bool(z.A or fast.loc[d]),B=bool(z.B),B1=bool(z.b1_active),C=bool(z.C),R1_evidence=bool(z.R1_evidence)) for d,z in b.iterrows()]
 states=build_state_tape(rows)
 result=pd.DataFrame({'date':b.index,'A_v2':[q['A'] for q in rows],'A_fast':fast.to_numpy(),'B':b.B.to_numpy(),'B1':b.b1_active.to_numpy(),'C':b.C.to_numpy(),'R1':b.R1_evidence.to_numpy(),'defensive':[z.defensive for z in states],'entry':[z.entered_defensive for z in states],'exit':[z.exited_defensive for z in states]})
 return result
if __name__=='__main__':
 out=ROOT/'ga6/data/crash_defense_A_v2'
 out.mkdir(parents=True,exist_ok=True)
 result=build_revised_daily_state()
 result.to_csv(out/'STATE_TAPE_HISTORICAL.csv',index=False)
 print('rows',len(result),'defensive',int(result.defensive.sum()),'entries',result.loc[result.entry,'date'].dt.strftime('%Y-%m-%d').tolist())

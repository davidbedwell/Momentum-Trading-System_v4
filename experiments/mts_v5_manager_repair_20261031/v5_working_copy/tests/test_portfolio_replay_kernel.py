import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engines.portfolio_replay.kernel import Bar, Signal, Replay

def test_next_open_and_fee_and_mark_to_market():
 r=Replay(); s=Signal('AAA','GA6','x',.10)
 assert r.day('d1',{'AAA':Bar(100,110)},[s])==100000
 r.day('d2',{'AAA':Bar(120,125)})
 assert r.ledger[0][0]=='d2' and r.ledger[0][2]=='BUY'
 assert r.nav[-1][1]>100000

def test_family_execution_parity():
 def run(family):
  r=Replay()
  for i in range(4):
   r.day(str(i),{'AAA':Bar(100+i,101+i)},[Signal('AAA',family,'x',.1)] if i==0 else [])
  return r.nav,r.ledger
 assert run('GA6')==run('GA7')

def test_defense_next_open_liquidation_and_entry_block():
 r=Replay(); b={'AAA':Bar(100,100)}
 r.day('d1',b,[Signal('AAA','GA7','x',.1)])
 r.day('d2',b)
 assert r.shares
 r.day('d3',b,[Signal('AAA','GA7','x',.1)],defense=True)
 assert not r.shares and r.ledger[-1][2]=='SELL'
 r.day('d4',b,defense=True)
 assert not r.shares

def test_cash_settlement_conservative():
 r=Replay(); b={'AAA':Bar(100,100),'BBB':Bar(100,100)}
 r.day('d1',b,[Signal('AAA','GA6','a',.1)])
 r.day('d2',b,[Signal('AAA','GA6','a',0),Signal('BBB','GA7','b',.1)])
 r.day('d3',b)
 assert r.cash>=-1e-8
 assert r.nav[-1][1]>0

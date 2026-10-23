import sys
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga6.test_parity import test_replay_parity
from ga6.test_optimizer import test_ev_beats_winrate,test_fresh_niche_breeding
for f in (test_ev_beats_winrate,test_fresh_niche_breeding,test_replay_parity):
 print('RUN',f.__name__,flush=True)
 f()
 print('PASS',f.__name__,flush=True)

import sys
sys.path.insert(0,'/opt/mts')
from ga6.test_parity import test_replay_parity
print('PARITY START',flush=True)
test_replay_parity()
print('PARITY PASS',flush=True)

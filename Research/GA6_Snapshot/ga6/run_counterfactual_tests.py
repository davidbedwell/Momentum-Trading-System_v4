import sys
sys.path.insert(0,'/opt/mts')
from ga6.test_counterfactuals import test_exit_avoids_loss,test_false_alarm,test_costs_and_cash
for f in (test_exit_avoids_loss,test_false_alarm,test_costs_and_cash):
 print('RUN',f.__name__,flush=True)
 f()
 print('PASS',f.__name__,flush=True)

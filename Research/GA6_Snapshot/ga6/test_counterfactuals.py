import sys
sys.path.insert(0,'/opt/mts')
from ga6.counterfactuals import compare_path,classify

def test_exit_avoids_loss():
 x=compare_path(100,98,85,100,5,10)
 assert x['incremental_net']>0 and x['exit_avoided_loss']
 assert classify([x])['avoided_loss']['count']==1

def test_false_alarm():
 x=compare_path(100,102,110,120,5,10)
 assert x['hold_net']>0 and x['incremental_net']<0
 assert classify([x])['false_alarm_winner']['count']==1

def test_costs_and_cash():
 x=compare_path(100,100,100,100,5,10)
 assert x['exit_reentry_net']<x['hold_net']
 assert x['cash_sessions']==5

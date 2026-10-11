from scripts.thirteen_window_statistical_guard_20261011 import adjusted_lcb,family_screen
x=adjusted_lcb(.1,.02,1);y=adjusted_lcb(.1,.02,6400)
assert y<x<.1
p=family_screen([{'horizon':2,'ev_net':.1,'se_cluster':.02,'effective_n':50}],100)
assert p[0]['multiplicity_tests']==6400 and p[0]['qualified_fwer']
try:adjusted_lcb(.1,.02,0)
except ValueError:pass
else:raise AssertionError('fail-closed')
print('MULTIPLICITY_GUARD_TEST_PASS')

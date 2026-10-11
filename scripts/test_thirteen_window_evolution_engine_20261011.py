from scripts.thirteen_window_evolution_engine_20261011 import WINDOWS,HORIZONS,window_checkpoint,select_parents
assert len(WINDOWS)==13
assert tuple(h for a,b in WINDOWS for h in range(a,b+1))==HORIZONS
f={'2':{'best_ev_net':.1,'best_lcb95':.01,'qualified_count':1}}
h=[{'generation':g,'frontier':f,'stale_checkpoints':0} for g in (25,50,75,100)]
for g in (125,150,175):
 x=window_checkpoint(h,f,g);h.append(x);assert x['stop']==(g==175)
assert all(not v for v in select_parents({}, {}, {},side='LONG').values())
print('THIRTEEN_WINDOW_EVOLUTION_ENGINE_TEST_PASS')

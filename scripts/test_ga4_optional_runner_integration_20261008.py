from scripts import run_ga4_parallel_dev80 as runner
s=runner.initialize()
assert len(s[6])==len(s[0].frame)
print('PRESENT_CONTEXT_OK',len(s[6]),s[7]['status'],flush=True)
runner.STATE=None
original=runner.load_optional_context
runner.load_optional_context=lambda pred,*args:(None,{'status':'UNAVAILABLE_OPTIONAL','scope':'DEV80'})
try:
 t=runner.initialize()
 assert t[6] is None
 assert len(t[0].frame)==len(s[0].frame)
 print('MISSING_CONTEXT_OK',len(t[0].frame),flush=True)
finally:
 runner.load_optional_context=original
 runner.STATE=None

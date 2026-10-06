"""Execution-only compute planning. Does not alter scientific search configuration."""
from __future__ import annotations
import os
def available_cpus():
 try:return len(os.sched_getaffinity(0))
 except Exception:return os.cpu_count() or 1
def plan(total_workers=None,folds=4,min_workers_per_fold=6):
 n=int(total_workers or os.environ.get("MTS_TOTAL_WORKERS") or available_cpus())
 reserve=int(os.environ.get("MTS_CPU_RESERVE","2" if n>=16 else "0"))
 usable=max(1,n-reserve)
 # Parallelize folds only when each can retain at least the historically validated 6 workers.
 parallel=max(1,min(folds,usable//min_workers_per_fold))
 per=max(1,usable//parallel)
 return {"detected_cpus":available_cpus(),"requested_workers":n,"reserved_cpus":reserve,
         "usable_workers":usable,"parallel_folds":parallel,"workers_per_fold":per,
         "scientific_configuration_changed":False}

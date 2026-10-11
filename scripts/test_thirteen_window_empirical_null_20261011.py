#!/usr/bin/env python3
"""Reproducible Gaussian-null calibration diagnostic, NOT adaptive GA certification."""
import json,sys,pathlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.thirteen_window_statistical_guard_20261011 import adjusted_lcb
rng=np.random.default_rng(20261011)
replicates=5000; hypotheses=256; alpha=.05
# Simulated independent standardized null scores. A genome selection procedure
# is NOT represented, and this test cannot certify the live adaptive search.
z=rng.standard_normal((replicates,hypotheses))
from statistics import NormalDist
cut=NormalDist().inv_cdf(1-alpha/hypotheses)
false_positive=(z.max(axis=1)>cut)
rate=float(false_positive.mean())
assert rate<=.065,(rate,'Gaussian null FWER above tolerance')
assert abs(adjusted_lcb(0,1,hypotheses)+cut)<1e-10
print(json.dumps({'status':'PASS_IDEALIZED_NULL_DIAGNOSTIC_ONLY','replicates':replicates,'hypotheses':hypotheses,'empirical_fwer':rate,'alpha':alpha,'adaptive_ga_certified':False,'real_market_calibrated':False}))

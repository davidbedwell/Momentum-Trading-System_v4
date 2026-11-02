"""Iteration3: frozen conditional EV fit; independent calibration; safety-only holdout monitor."""
import sys,json,math,statistics as st,time,subprocess,gzip,csv,hashlib,importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('iteration2_reference',OUT.parent/'discrimination_iteration2/experiment.py')
previous_model=importlib.util.module_from_spec(spec);sys.modules[spec.name]=previous_model;spec.loader.exec_module(previous_model)
b=previous_model.b
m,k,r,s=b.m,b.k,b.r,b.s
TIERS,EDGES,tier,infer,observed,sha=b.TIERS,b.EDGES,b.tier,b.infer,b.observed,b.sha
generate=previous_model.generate


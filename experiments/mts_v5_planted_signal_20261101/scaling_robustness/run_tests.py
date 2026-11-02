"""Resolve test modules relative to this file, independently of working directory."""
from pathlib import Path
import sys, unittest
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import experiment
import test_reliability
assert Path(test_reliability.__file__).resolve()==OUT/'test_reliability.py'
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_regression','test_reliability'])
with (OUT/'resume_tests.log').open('w') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
print((OUT/'resume_tests.log').read_text())
raise SystemExit(0 if result.wasSuccessful() else 1)

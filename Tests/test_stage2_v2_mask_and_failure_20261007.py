import importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd, pytest
SCRIPT=Path(__file__).parents[1]/'scripts'/'run_stage2_v2_20261007.py'
spec=importlib.util.spec_from_file_location('stage2v2',SCRIPT);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_pmask_nullable_context_is_dense_bool():
    d=pd.DataFrame({'galaxy_state':pd.Series(['Up',pd.NA,'Down'],dtype='string')})
    x=m.pmask(d,{'feature':'galaxy_state','op':'==','value':'Up'})
    assert x.dtype==np.bool_
    assert x.tolist()==[True,False,False]

def test_pmask_numeric_nan_is_dense_bool_and_composable():
    d=pd.DataFrame({'ret20':[.2,np.nan,-.1]})
    x=m.pmask(d,{'feature':'ret20','op':'>=','thr':0.0})
    base=np.ones(len(d),dtype=bool);base &= x
    assert base.tolist()==[True,False,False]

def test_fatal_writer_changes_status_from_preflight(tmp_path,monkeypatch):
    monkeypatch.setattr(m,'RUN',tmp_path)
    try: raise RuntimeError('sentinel')
    except RuntimeError as e: m._record_fatal(e)
    st=json.loads((tmp_path/'status.json').read_text());fail=json.loads((tmp_path/'failure.json').read_text())
    assert st['state']=='ERROR' and fail['exception_type']=='RuntimeError' and 'sentinel' in st['message']

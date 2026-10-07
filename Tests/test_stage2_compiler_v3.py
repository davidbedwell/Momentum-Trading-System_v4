import random,sys
from pathlib import Path
import numpy as np,pandas as pd
from Core.layered_ga.stage2_compiler_v3 import VectorSignalCompiler,stage2_search_spaces,random_genome,CERTIFIED_ROOT
from Core.layered_ga.stage2_features_v3 import _source_factory
root=str(CERTIFIED_ROOT)
if root not in sys.path:sys.path.insert(0,root)
from MTS_V4.search_candidate_analysis import _compile_signal

def predictors_fixture():
    dates=pd.bdate_range('2023-01-02',periods=330);rows=[]
    for j,(t,sec) in enumerate([('A','S1'),('B','S1'),('C','S2'),('D','S2')]):
        x=np.arange(len(dates));close=(40+7*j)*np.exp((.0001+.00005*j)*x+.025*np.sin(x/(9+j)))
        for i,dt in enumerate(dates):
            c=close[i]; rows.append({'security_id':t,'date':str(dt.date()),'open':c*(1+.002*np.sin(i)),'high':c*1.012,'low':c*.988,'close':c,'volume':900000+5000*j+1000*(i%17),'eligible':True,'ticker':t,'sector_id':sec,'industry_id':'I'})
    return list(_source_factory()(rows))

def test_vector_compiler_matches_recovered_oracle_for_all_families():
    rows=predictors_fixture();df=pd.DataFrame(rows);c=VectorSignalCompiler(df);rng=random.Random(20261007)
    for fam,space in stage2_search_spaces().items():
        for _ in range(20):
            g=random_genome(space,rng)
            oracle=np.asarray(_compile_signal(rows,{'family_id':fam,'genome':g}),dtype=bool)
            got=c.compile(fam,g)
            assert np.array_equal(got,oracle),(fam,g,int(np.sum(got!=oracle)))

def test_noncausal_and_unavailable_features_are_not_executable():
    spaces=stage2_search_spaces()
    vals={v for s in spaces.values() for g in s.genes for v in g.values if isinstance(v,str)}
    assert 'turnover__v1' not in vals
    assert 'turnover_relative_20__v1' not in vals
    assert 'sector_return_252_percentile__v1' not in vals

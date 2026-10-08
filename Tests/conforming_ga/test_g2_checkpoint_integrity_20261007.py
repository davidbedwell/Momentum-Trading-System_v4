import hashlib,pickle
import pytest
from Core.conforming_ga.ga_g2 import evolve_g2

@pytest.mark.parametrize('mode',['missing','tampered'])
def test_resume_rejects_unverified_checkpoint(tmp_path,mode):
    p=tmp_path/'checkpoint.pkl'
    p.write_bytes(pickle.dumps({'master_seed':'test','fold':0}))
    if mode=='tampered':
        p.with_suffix('.pkl.sha256').write_text(hashlib.sha256(b'other').hexdigest()+'\n')
    with pytest.raises(ValueError,match='checkpoint integrity'):
        evolve_g2(evaluator=lambda g:{},master_seed='test',fold=0,resume_path=p)

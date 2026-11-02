"""Smoke tests for complete-library availability and strict causal feedback."""
import tempfile
from pathlib import Path
from contextual_library import ContextLibrary, Candidate, Observation

with tempfile.TemporaryDirectory() as d:
    lib=ContextLibrary(str(Path(d)/"library.sqlite"))
    lib.register([Candidate(f"chr-{i}","GA7","family","specialist","archive") for i in range(50000)])
    assert sum(lib.inventory().values())==50000
    lib.record(Observation("chr-49999",(1.,0.),10,20,0.5))
    lib.record(Observation("chr-1",(1.,0.),10,20,-0.2))
    before=lib.select((1.,0.),19,{"chr-49999","chr-1"},limit=2)
    assert all(x["effective_samples"]==0 for x in before),before
    after=lib.select((1.,0.),21,{"chr-49999","chr-1"},limit=2,exploration=0)
    assert any(x["chromosome_id"]=="chr-49999" and x["effective_samples"]>0 for x in after),after
    rare=lib.select_from_gate((1.,0.),21,lambda c,ctx,t:c.chromosome_id=="chr-49999",limit=5)
    assert [x["chromosome_id"] for x in rare]==["chr-49999"],rare
    assert sum(lib.inventory().values())==50000
    print("PASS: 50000 preserved; future outcomes withheld; rare specialist accessible")

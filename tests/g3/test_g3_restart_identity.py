import random,tempfile
from pathlib import Path
from Core.g3.starter import checkpoint,restore,random_specialist

def test_restart_restores_rng_and_next_population_identity():
    rng=random.Random(90210)
    population=[random_specialist(rng,12) for _ in range(20)]
    state={"generation":11,"population":population,"rng_state":rng.getstate(),"archive":population[:3]}
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.pkl"; h=checkpoint(p,state)
        expected=[random_specialist(rng,12) for _ in range(10)]
        restored=restore(p)
        rr=random.Random(); rr.setstate(restored["rng_state"])
        actual=[random_specialist(rr,12) for _ in range(10)]
        assert actual==expected
        assert checkpoint(p,restored)==h

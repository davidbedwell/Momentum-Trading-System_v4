from pathlib import Path
from Core.conforming_ga.ga_g2 import (
    evolve_g2, receiving_migrants, update_archive, island_feasible, evaluation_jobs, canonical_raw_metric_cache, ISLANDS
)
from Core.conforming_ga.g2evolution import initial_population_g2
from Core.conforming_ga.g2schema import genome_hash

def metric(cagr=.10,mdd=-.05):
    return {"cagr":cagr,"mdd":mdd,"gross":.5,"safe_fraction":.5,"short_share":0.,
            "turnover":.1,"holdings_hhi":.2,"gfc_return":0.,"recovery_capture":0.}

def smoke_eval(g):
    # deterministic island-independent raw simulation metric
    h=int(genome_hash(g)[:8],16)
    return metric(.05+(h%1000)/100000.,-.05)

def test_band_archive_rejects_infeasible_candidate():
    g=initial_population_g2("a",0,0,1)[0]
    assert not island_feasible("band_10",metric(mdd=-.11))
    assert update_archive([],[(g,metric(mdd=-.11))],"band_10")==[]
    assert update_archive([],[(g,metric(mdd=-.10))],"band_10")

def test_migrant_must_survive_receiver_feasibility_and_ranking():
    gs=initial_population_g2("m",0,0,4)
    recv=[(gs[0],metric(.20,-.05)),(gs[1],metric(.19,-.05))]
    # infeasible high-return migrant is rejected by band_10
    assert receiving_migrants("band_10",recv,[(gs[2],metric(.99,-.20))],1)==[]
    # feasible but inferior migrant loses receiver ranking for fixed population slots
    assert receiving_migrants("band_10",recv,[(gs[2],metric(.01,-.05))],1)==[]
    # feasible superior migrant survives receiver semantics
    got=receiving_migrants("band_10",recv,[(gs[3],metric(.30,-.05))],1)
    assert [genome_hash(x) for x in got]==[genome_hash(gs[3])]


def test_second_plateau_freeze_removes_only_work_not_scientific_budget():
    pops={k:initial_population_g2("realloc",0,i,4) for i,k in enumerate(ISLANDS)}
    state={k:{"frozen":False} for k in ISLANDS}
    frozen=ISLANDS[0];state[frozen]["frozen"]=True
    jobs=evaluation_jobs(pops,state)
    assert not any(name==frozen for name,_,_ in jobs)
    assert len(jobs)==(len(ISLANDS)-1)*4
    assert all(len(pops[k])==4 for k in ISLANDS)  # no population redistribution
    assert {name for name,_,_ in jobs}==set(ISLANDS)-{frozen}

def test_migrant_cached_raw_metrics_are_reinterpreted_by_receiver():
    gs=initial_population_g2("cached-migrant",0,0,4)
    raw=metric(.30,-.15)  # deterministic cached simulation result
    source=[(gs[0],raw)]
    cache=canonical_raw_metric_cache({"source":source})
    cached_source=[(gs[0],cache[genome_hash(gs[0])])]
    # Global accepts the cached raw outcome; band_10 independently rejects it.
    weak=[(gs[1],metric(.01,-.05))]
    assert receiving_migrants("global",weak,cached_source,1)==[gs[0]]
    assert receiving_migrants("band_10",weak,cached_source,1)==[]
    # A feasible cached migrant is then ranked against receiver residents from scratch.
    cached=metric(.30,-.05)
    residents=[(gs[1],metric(.20,-.05)),(gs[2],metric(.19,-.05))]
    got=receiving_migrants("band_10",residents,[(gs[0],cached)],1)
    assert [genome_hash(x) for x in got]==[genome_hash(gs[0])]
    assert update_archive([],[(gs[0],cached)],"band_10")  # receiver archive admission anew

def _hash_pops(r):
    return {k:[genome_hash(g) for g in v] for k,v in r["populations"].items()}

def test_tiny_full_controller_smoke_extension_plateau_freeze_reallocation_migration_checkpoint_resume(tmp_path:Path):
    mechanics={"plateau_window":1,"plateau_gain_threshold":999.,
               "migration_interval":1,"checkpoint_interval":1,
               "extension_base":2,"extension_step":1,"extension_max":3,
               "extension_window":1,"extension_threshold":-1.}
    full=evolve_g2(evaluator=smoke_eval,master_seed="SMOKE",fold=0,generations=2,
                   population_size=4,workers=2,checkpoint_dir=tmp_path/"full",mechanics=mechanics)
    assert full["final_budget"]==3 and full["completed_generations"]==3
    assert all(x["frozen"] for x in full["plateau_state"].values())
    # Frozen islands consume no generation-3 simulation work: histories stop at 2
    # even though controller terminates at extended generation 3.
    assert all(len(v)==2 for v in full["history"].values())
    assert full["events"]["extensions"]==1
    assert full["events"]["migration_events"]>=1
    assert full["events"]["freeze_events"]==9
    assert full["events"]["frozen_island_generation_skips"]==9
    ck=tmp_path/"full"/"g2_fold0_gen0001.pkl"
    resumed=evolve_g2(evaluator=smoke_eval,master_seed="SMOKE",fold=0,generations=2,
                      population_size=4,workers=2,resume_path=ck,
                      checkpoint_dir=tmp_path/"resume",mechanics=mechanics)
    assert resumed["final_budget"]==3 and resumed["completed_generations"]==3
    assert _hash_pops(resumed)==_hash_pops(full)
    assert resumed["plateau_state"]==full["plateau_state"]
    assert resumed["aggregate_hv_history"]==full["aggregate_hv_history"]
    assert resumed["events"]==full["events"]

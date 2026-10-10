#!/usr/bin/env python3
"""Read-only preflight for the frozen 13-window exploratory archive."""
import argparse,csv,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
REL=pathlib.Path("Research/Runs/gen1-merit-screen-20261008/holding_window_chromosome_archive_20261009")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(source,output):
    m=json.loads((source/"manifest.json").read_text())
    assert m["status"]=="FROZEN_EXPLORATORY_GENOME_DEFINITIONS"
    assert len(m["windows"])==13
    assert sha(source/"unique_evaluated_genomes.jsonl")==m["unique_genomes_sha256"]
    pairs=0; assignments=0; seen=set(); summary=[]
    for w in m["windows"]:
        p=source/w["file"];assert sha(p)==w["sha256"],p
        d=json.loads(p.read_text())
        assert d["genome_count"]==w["genomes"]==len(d["genomes"])
        assert d["evaluated_pairs"]==w["evaluated_pairs"]
        assert all("chromosomes" in g and "horizons" in g for g in d["genomes"])
        pairs+=w["evaluated_pairs"];assignments+=w["genomes"]
        summary.append({"window":w["window"],"genomes":w["genomes"],"evaluated_pairs":w["evaluated_pairs"],"sha256":w["sha256"]})
    with (source/"unique_evaluated_genomes.jsonl").open() as f:
        for line in f:
            if line.strip():
                g=json.loads(line);assert "chromosomes" in g and "horizons" in g
                seen.add(json.dumps(g["chromosomes"],sort_keys=True))
    assert len(seen)==m["unique_evaluated_genomes"]
    assert pairs==m["evaluated_pairs"]
    report={"source_commit":"a5679fe2897ccbc78722915feda820fd280776d8","source_status":m["status"],"source_manifest_sha256":sha(source/"manifest.json"),"windows":summary,"unique_genomes":len(seen),"window_assignments":assignments,"evaluated_pairs":pairs,"generation_lineage":"NOT_PRESENT_IN_FROZEN_ARCHIVE","next_run_requirements":["record generation and offspring_id","record parent_hashes and genome_hash","journal candidate intent before evaluation","journal evaluation and per-generation archive changes","checkpoint RNG and controller state atomically","record EV_net LCB95 CVaR5 MAE-tail and effective_n","track economic improvement separately from genetic novelty","never read protected heldouts during design"]}
    output.mkdir(parents=True,exist_ok=True)
    target=output/"preflight.json";target.write_text(json.dumps(report,indent=2)+"\n")
    return report
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--source",type=pathlib.Path,default=ROOT/"Research/Preparation/horizon_generational_20261010"/REL);a.add_argument("--output",type=pathlib.Path,default=ROOT/"Research/Preparation/horizon_generational_20261010")
    x=a.parse_args();r=prepare(x.source,x.output)
    print("PREFLIGHT_PASS",len(r["windows"]),r["unique_genomes"],r["evaluated_pairs"])

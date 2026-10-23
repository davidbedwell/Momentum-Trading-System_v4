"""External stagnation stop for the already-running GA6 structural research.

Does not alter runner source/checkpoint fingerprint. Counts consecutive
completed generations without STRICT improvement in best fitness.
"""
import json, os, pathlib, signal, subprocess, time

ROOT=pathlib.Path('/opt/mts/ga6/runs/structural_v3_calibrated_active')
TARGET=467776
LIMIT=100
LOG=ROOT/'stagnation_watch_status.json'

def alive(pid):
    try:
        os.kill(pid,0)
        return True
    except ProcessLookupError:
        return False

def status():
    reports=sorted(ROOT.glob('generation_*.json'))
    if not reports:
        return None
    best=float('-inf'); last_improvement=0
    for path in reports:
        data=json.loads(path.read_text())
        value=float(data['best_exploratory_fitness'])
        if value>best+1e-12:
            best=value;last_improvement=int(data['generation'])
    latest=int(json.loads(reports[-1].read_text())['generation'])
    return dict(latest_generation=latest,last_improvement_generation=last_improvement,stagnant_generations=latest-last_improvement,best_exploratory_fitness=best,limit=LIMIT)

while alive(TARGET):
    try:
        info=status()
        if info is not None:
            info['runner_alive']=True
            if info['stagnant_generations']>=LIMIT:
                # Preserve the last complete checkpoint before interrupting the next generation.
                checkpoint=ROOT/'structural_checkpoint.json'
                saved=json.loads(checkpoint.read_text())
                if int(saved['generation'])>=info['latest_generation']:
                    info['stop_reason']='100_completed_generations_without_fitness_improvement'
                    info['checkpoint_generation']=saved['generation']
                    LOG.write_text(json.dumps(info,indent=2))
                    children=subprocess.check_output(['pgrep','-P',str(TARGET)],text=True).split() if subprocess.run(['pgrep','-P',str(TARGET)],stdout=subprocess.DEVNULL).returncode==0 else []
                    os.kill(TARGET,signal.SIGTERM)
                    for child in children:
                        try:os.kill(int(child),signal.SIGTERM)
                        except ProcessLookupError:pass
                    break
            LOG.write_text(json.dumps(info,indent=2))
    except Exception as exc:
        LOG.write_text(json.dumps({'watch_error':str(exc)},indent=2))
    time.sleep(15)

#!/usr/bin/env python3
"""External GA6 stagnation guard: preserves unmodified active runner and checkpoint."""
import argparse,json,os,signal,time
from pathlib import Path

def status(folder):
    best=float('-inf');last=0;latest=0;value=None;count=0
    for path in sorted(folder.glob('generation_*.json')):
        try:
            item=json.loads(path.read_text());g=int(item['generation']);f=float(item['best_exploratory_fitness'])
        except (ValueError,KeyError,OSError,TypeError):continue
        count+=1
        if f>best+1e-12:best=f;last=g
        if g>latest:latest=g;value=f
    return {'latest_generation':latest,'last_improvement_generation':last,'stagnant_generations':latest-last,'best_fitness':best if count else None,'latest_fitness':value,'reports':count}

def live(pid):
    try:os.kill(pid,0);return True
    except ProcessLookupError:return False

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run',required=True);p.add_argument('--pid',type=int,required=True)
    p.add_argument('--patience',type=int,default=100);p.add_argument('--poll',type=int,default=30)
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args();folder=Path(a.run);state_file=folder/'stagnation_guard_status.json'
    while True:
        s=status(folder);s.update({'patience':a.patience,'target_pid':a.pid,'runner_alive':live(a.pid),'guard_mode':'dry_run' if a.dry_run else 'active'})
        checkpoint=folder/'structural_checkpoint.json'
        try:cp=json.loads(checkpoint.read_text());checkpoint_generation=int(cp['generation'])
        except (OSError,ValueError,KeyError):checkpoint_generation=-1
        s['checkpoint_generation']=checkpoint_generation
        if not s['runner_alive']:
            s['action']='runner_exited';state_file.write_text(json.dumps(s,indent=2));print(json.dumps(s),flush=True);break
        if s['stagnant_generations']>=a.patience and s['latest_generation']>0 and checkpoint_generation>=s['latest_generation']:
            # SIGINT invokes Python KeyboardInterrupt/finally and closes evaluation pool.
            # Confirm PID command is the expected GA6 structural runner before signalling.
            try:cmd=(Path('/proc')/str(a.pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode()
            except OSError:cmd=''
            if 'ga6.structural_independent_v2_20261022.structural_runner_A_v2' not in cmd or str(folder) not in cmd:
                s['action']='unsafe_pid_or_run_mismatch'
            elif a.dry_run:s['action']='would_signal_SIGINT'
            else:
                os.kill(a.pid,signal.SIGINT);s['action']='signalled_SIGINT_after_checkpoint'
            state_file.write_text(json.dumps(s,indent=2));print(json.dumps(s),flush=True);break
        s['action']='watching';state_file.write_text(json.dumps(s,indent=2))
        if a.dry_run:print(json.dumps(s),flush=True);break
        time.sleep(a.poll)
if __name__=='__main__':main()

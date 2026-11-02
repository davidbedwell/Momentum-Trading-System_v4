"""Fail-closed persistent GA9 audit/engineering supervisor; never runs market search."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'ga9/artifacts/autonomous_supervisor'
STOP = False
CHILD = None


def atomic(path, value):
    tmp = path.with_suffix('.tmp')
    with tmp.open('w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def terminate(*_):
    global STOP
    STOP = True
    if CHILD and CHILD.poll() is None:
        os.killpg(CHILD.pid, signal.SIGTERM)


def target(net_cagr, spy_cagr, qqq_cagr, mdd):
    # Fractions, identical periods and net costs must be validated by a future adapter.
    import math
    return all(math.isfinite(x) for x in (net_cagr, spy_cagr, qqq_cagr, mdd)) and net_cagr > max(spy_cagr, qqq_cagr) + .20 and 0 <= mdd < .08


class Supervisor:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.lock = (directory/'instance.lock').open('a+')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise
        self.state_path = directory/'state.json'
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {'schema': 1, 'steps': {}, 'started': time.time()}
        self.state.setdefault('codex_calls',0)
        self.state.setdefault('llm_spend_usd',0)
        self.state.update(pid=os.getpid(), status='STARTING', research_enabled=False)
        self.save('START')

    def save(self, event, **details):
        self.state['updated'] = time.time()
        # Durable journal before checkpoint; interrupted steps are never repeated automatically.
        with (self.directory/'audit.jsonl').open('a') as f:
            f.write(json.dumps(dict(time=time.time(), event=event, pid=os.getpid(), **details))+'\n')
            f.flush(); os.fsync(f.fileno())
        atomic(self.state_path, self.state)

    def step(self, name, args, seconds):
        global CHILD
        if name in self.state['steps']:
            return  # running at crash => indeterminate, requires review; no duplicate API spend
        if STOP: return
        self.state['steps'][name] = dict(status='RUNNING', argv=args, timeout=seconds)
        self.save('STEP_RESERVED', name=name)
        log = self.directory/(name+'.log')
        with log.open('xb') as out:
            env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(self.directory))
            CHILD = subprocess.Popen(args, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            deadline = time.monotonic()+seconds
            timed_out = False
            heartbeat = time.monotonic()+10
            while CHILD.poll() is None:
                if STOP or time.monotonic() >= deadline:
                    timed_out = not STOP
                    os.killpg(CHILD.pid, signal.SIGTERM)
                    try: CHILD.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(CHILD.pid, signal.SIGKILL); CHILD.wait()
                    break
                if time.monotonic() >= heartbeat:
                    self.save('STEP_PROGRESS',name=name,child_pid=CHILD.pid,remaining_seconds=max(0,deadline-time.monotonic()))
                    heartbeat=time.monotonic()+10
                time.sleep(.2)
            code = CHILD.returncode
            CHILD = None
        self.state['steps'][name].update(status='INTERRUPTED' if STOP else 'TIMEOUT' if timed_out else 'DONE', returncode=code)
        self.save('STEP_FINISHED', name=name, returncode=code)

    def recover_zero(self, kind, source):
        """Two durable offline attempts; at most 600 seconds total, $0 API spend.

        Only interrupted/timed-out phases can get one fresh process retry. Completed
        failed diagnoses/tests/experiments are blockers, never identical reruns.
        """
        ledger=self.state.setdefault('recovery', {}).setdefault(kind, {'attempts': []})
        if ledger.get('terminal'):
            if ledger.get('report') and Path(ledger['report']).exists():
                self.state.setdefault('exploratory_results',{})[kind]=json.loads(Path(ledger['report']).read_text())
            return
        for number in range(2):
            attempts=ledger['attempts']
            if number >= len(attempts):
                attempts.append(dict(started=time.time(),deadline=time.time()+300,profile='edge_units_v2'))
                self.save('RECOVERY_RESERVED',kind=kind,attempt=number,max_seconds=300,max_cost_usd=0)
            attempt=attempts[number]
            prefix=f'recovery_{kind}_edge_units_v2_{number}'
            self.state.update(status='EXPLORATORY_DIAGNOSING',research_enabled=True)
            phases=[('diagnosis',60,[sys.executable,'-B','-m','ga9.recovery','--source',str(source),
                                    '--output',str(self.directory/(prefix+'_diagnosis.json'))]),
                    ('tests',90,[sys.executable,'-B','-m','unittest','ga9.test_recovery','ga9.test_opportunity','ga9.test_execution']),
                    ('experiment',150,[sys.executable,'-B','-m','ga9.exploratory','--kind',kind,
                         '--output',str(self.directory/(prefix+'_experiment')),'--seconds','120','--evaluations','48',
                         '--repair','edge_units_v2'])]
            retry=False
            for phase,limit,args in phases:
                name=prefix+'_'+phase
                previous=self.state['steps'].get(name,{})
                remaining=attempt['deadline']-time.time()
                if remaining<=6 or previous.get('status') in ('RUNNING','INTERRUPTED','TIMEOUT'):
                    retry=True;break
                self.state['status']='EXPLORATORY_'+phase.upper()
                self.step(name,args,min(limit,remaining-6))
                record=self.state['steps'].get(name,{})
                if STOP: return
                if record.get('status') in ('TIMEOUT','INTERRUPTED'): retry=True;break
                if record.get('returncode') != 0:
                    ledger.update(terminal=True,outcome='BLOCKED',blocker=f'{name} failed; inspect {name}.log')
                    break
                if phase=='diagnosis':
                    diagnosis=json.loads((self.directory/(prefix+'_diagnosis.json')).read_text())
                    self.save('ZERO_FILL_DIAGNOSED',kind=kind,classification=diagnosis['classification'])
                    if diagnosis['classification']!='EDGE_UNIT_MISMATCH':
                        ledger.update(terminal=True,outcome='BLOCKED',blocker=diagnosis['action']);break
                if phase=='experiment':
                    report=json.loads((self.directory/name/'report.json').read_text())
                    self.state.setdefault('exploratory_results',{})[kind]=report
                    active=report.get('total_fills',0)>0
                    ledger.update(terminal=True,outcome='RECOVERED' if active else 'BLOCKED',
                                  report=str(self.directory/name/'report.json'),
                                  blocker=None if active else 'Repair produced no fills; inspect forecasts and allocator audits; unknown class')
                    self.save('AUTOMATIC_RECOVERY_OUTCOME',kind=kind,outcome=ledger['outcome'],fills=report.get('total_fills',0))
            if ledger.get('terminal'): break
            if retry: self.save('RECOVERY_SAFE_RETRY',kind=kind,attempt=number,reason='Interrupted offline phase; new output namespace, unchanged lifetime cap')
        if not ledger.get('terminal'):
            ledger.update(terminal=True,outcome='BLOCKED',blocker='Two offline attempts exhausted (600s / $0); inspect phase logs')
        self.save('RECOVERY_CHECKPOINT',kind=kind)

    def exploratory(self, once=False):
        self.state.update(status='EXPLORATORY_RUNNING', research_enabled=True, mode='EXPLORATORY_DEVELOPMENT_ONLY',
                          certified=False, promotion_allowed=False, production_allowed=False,
                          final_validation_allowed=False)
        self.save('EXPLORATORY_AUTHORIZED')
        for kind in ('synthetic', 'real'):
            for retry in range(1):
                name = f'exploratory_{kind}_v1_retry{retry}'
                self.step(name, [sys.executable, '-B', '-m', 'ga9.exploratory',
                          '--kind', kind, '--output', str(self.directory/name),
                          '--seconds', '120', '--evaluations', '48'], 150)
                record = self.state['steps'].get(name, {})
                report = self.directory/name/'report.json'
                if record.get('status') == 'DONE' and record.get('returncode') == 0 and report.exists():
                    self.state.setdefault('exploratory_results', {})[kind] = json.loads(report.read_text())
                    self.save('EXPERIMENT_OUTCOME', kind=kind)
                    break
                if STOP or record.get('status') in ('RUNNING', 'INTERRUPTED'): break
                self.state.setdefault('experiment_blockers',{})[kind]=f'{name}: inspect child log; unknown execution failure, no identical retry'
                self.save('EXPERIMENT_BLOCKED',kind=kind,name=name)
        for kind, report in list(self.state.get('exploratory_results', {}).items()):
            best=report.get('best') or {}
            folds=best.get('folds', [])
            if folds and sum(f['metrics']['fills'] for f in folds)==0 and not STOP:
                # Retain the original report and all reservations; never reset state.
                source=self.directory/f'exploratory_{kind}_v1_retry0'
                self.recover_zero(kind,source)
        outcomes=[r.get('outcome') for r in self.state.get('recovery',{}).values()]
        self.state.update(status='STOPPED' if STOP else 'EXPLORATORY_BLOCKED' if 'BLOCKED' in outcomes or self.state.get('experiment_blockers') else 'EXPLORATORY_RECOVERED' if 'RECOVERED' in outcomes else 'EXPLORATORY_HALTED',
                          next_action='Bounded development cycle complete. Review recovery ledger and reports; unknown classes require engineering. No final evaluation or promotion.')
        self.save(self.state['status'])
        while not once and not STOP: time.sleep(1)
        if STOP:
            self.state['status'] = 'STOPPED'
            self.save('EXIT')

    def run(self, once=False):
        py = sys.executable
        archive = '/tmp/ga9_nasdaq_archive'
        self.step('archive_audit', [py, '-m', 'ga9.nasdaq_archive', '--archive', archive, '--output', str(self.directory/'archive_audit')], 300)
        # Diagnostic acquisition only. Never accepts data, touches protected partitions or certifies PIT.
        self.step('alpaca_remediation', [py, '-m', 'ga9.alpaca_repair', '--archive', archive,
            '--gaps', str(ROOT/'ga9/artifacts/nasdaq_archive_audit_final_20261029/missing_projected_bars.csv'),
            '--output', str(self.directory/'alpaca_remediation'), '--max-requests', '2', '--max-symbols', '1', '--max-dates', '3'], 90)
        self.step('engineering_regression_v2', [py, '-m', 'unittest', 'ga9.test_supervisor', 'ga9.test_alpaca_repair', 'ga9.test_nasdaq_archive', 'ga9.test_ticker_lineage'], 180)
        self.state.update(status='STOPPED' if STOP else 'BLOCKED', blockers=[
            'PIT membership known_at, stable identities and delisting outcomes not certified',
            'Corporate actions, executable marks, independent sessions and SPY/QQQ net comparison not certified',
            'No genuinely untouched final holdout custody/protocol certification; exposed forward forbidden',
            'No certified development-only experiment adapter or enforceable autonomous Codex dollar budget'],
            next_action='Resolve provenance and holdout custody; implement reviewed development adapter. No automatic promotion from a manifest flag.')
        self.save('RESEARCH_HALTED')
        while not once and not STOP:
            # Blocked means no repeated experiments, downloads, repair loops or model calls.
            # Watchdog pings do not append logs or create disk churn.
            time.sleep(1)
        self.state['status'] = 'BLOCKED' if once and not STOP else 'STOPPED'
        self.save('EXIT')


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--state-dir', type=Path, default=DEFAULT)
    p.add_argument('--once', action='store_true')
    p.add_argument('--mode', choices=['audit', 'exploratory'], default='audit')
    a = p.parse_args()
    directory = a.state_dir.resolve()
    if not directory.is_relative_to(ROOT/'ga9/artifacts'):
        p.error('State must be inside ga9/artifacts')
    signal.signal(signal.SIGTERM, terminate); signal.signal(signal.SIGINT, terminate)
    try:
        supervisor = Supervisor(directory)
    except BlockingIOError:
        return 73
    try:
        if a.mode == 'exploratory': supervisor.exploratory(a.once)
        else: supervisor.run(a.once)
    except Exception as exc:
        supervisor.state.update(status='ERROR', error_type=type(exc).__name__)
        supervisor.save('FAIL_CLOSED', error_type=type(exc).__name__)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

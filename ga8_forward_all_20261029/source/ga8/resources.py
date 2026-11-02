"""Linux process-tree telemetry and a conservative available-RAM stop gate."""
import os
import threading
import time
from pathlib import Path

class Monitor:
    def __init__(self):
        self.limit = self.available() * .75
        self.peak_rss = self.peak_pss = 0
        self.exceeded = False
        self.closed = False
        self.peak_processes=0
        self.cpu_start = self.cpu()
    @staticmethod
    def cpu():
        return {line.split()[0]:list(map(int,line.split()[1:9])) for line in Path('/proc/stat').read_text().splitlines() if line.startswith('cpu')}
    def cpu_usage(self):
        current=self.cpu(); result={}
        for key,values in current.items():
            delta=[x-y for x,y in zip(values,self.cpu_start[key])]
            total=sum(delta)
            result[key]=100*(1-(delta[3]+delta[4])/total) if total else 0.
        return result
    @staticmethod
    def available():
        return int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))) * 1024
    def snapshot(self):
        pending=[os.getpid()]; rss=pss=0; count=0
        while pending:
            pid=pending.pop()
            try:
                count+=1
                pending.extend(map(int,Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                fields=dict((line.split(':')[0],int(line.split()[1])*1024) for line in Path(f'/proc/{pid}/smaps_rollup').read_text().splitlines() if line.startswith(('Rss:','Pss:')))
                rss+=fields['Rss']; pss+=fields['Pss']
            except (OSError,KeyError):
                pass
        self.peak_processes=max(self.peak_processes,count)
        self.peak_rss=max(self.peak_rss,rss); self.peak_pss=max(self.peak_pss,pss)
        self.exceeded |= pss > self.limit or self.available() < self.limit/3
        return dict(peak_processes=self.peak_processes,peak_rss_bytes=self.peak_rss,peak_pss_bytes=self.peak_pss,limit_bytes=self.limit,memory_limit_exceeded=self.exceeded,cpu_utilization_percent=self.cpu_usage())
    def start(self):
        def loop():
            while not self.closed:
                self.snapshot(); time.sleep(.5)
        threading.Thread(target=loop,daemon=True).start()

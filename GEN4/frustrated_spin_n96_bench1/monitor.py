"""Read-only 100ms cgroup/process telemetry, accumulated in RAM."""
import os,time,threading,json
from pathlib import Path
class Monitor:
 def __init__(self):self.rows=[];self.stop_event=threading.Event();self.thread=threading.Thread(target=self.run,daemon=True)
 def start(self):self.thread.start();return self
 def snapshot(self):
  row={'time':time.time(),'monotonic':time.monotonic()}
  for name in ['cpu.stat','memory.current','memory.peak','memory.events','io.stat','cpu.pressure','memory.pressure','io.pressure']:
   try:row[name]=Path('/sys/fs/cgroup',name).read_text().strip()
   except OSError:pass
  procs=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    stat=(p/'stat').read_text();rest=stat.rsplit(')',1)[1].split();comm=stat.split('(',1)[1].rsplit(')',1)[0]
    if comm not in ['python','python3','python3.12']:continue
    procs.append({'pid':int(p.name),'ppid':int(rest[1]),'user_ticks':int(rest[11]),'system_ticks':int(rest[12]),'rss_bytes':int(rest[21])*os.sysconf('SC_PAGE_SIZE')})
   except (OSError,ValueError,IndexError):pass
  row['processes']=procs;return row
 def run(self):
  while not self.stop_event.is_set():self.rows.append(self.snapshot());self.stop_event.wait(.1)
 def stop(self,path):self.stop_event.set();self.thread.join();self.rows.append(self.snapshot());path.write_text(json.dumps(self.rows)+'\n')

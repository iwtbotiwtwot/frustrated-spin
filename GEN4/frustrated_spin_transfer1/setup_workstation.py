"""After T500 transfer verification, stage and qualify an isolated local restart."""
from pathlib import Path
import json,time,hashlib,shutil,tarfile,os,subprocess,sys,traceback
P=Path(__file__).resolve().parent
REPO=P.parents[1]
TARGET=REPO/'GEN4/frustrated_spin_workstation1'
MOUNT=Path('/home/sam/mnt/lilhelper-t500')
BACKUP=MOUNT/'SAM_POD_BACKUPS/frustrated-spin-20260926'
PYTHON=REPO/'.venv-r3/bin/python'
RUNTIME_ARCHIVE=Path('/tmp/spin-publication-20260926/RUNTIME.public.tar.gz')
RUNTIME_SHA='79f4d7afe7b357fe988dfc737c7a223017b68518aa362c4c0fc2e2f440e462cc'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(v):
    q=P/'WORKSTATION_STATUS.json.part';q.write_text(json.dumps(v,indent=2)+'\n');q.replace(P/'WORKSTATION_STATUS.json')
def main():
    state=dict(status='WAITING_FOR_VERIFIED_TRANSFER',pid=os.getpid(),target=str(TARGET),started=time.time());save(state)
    deadline=time.time()+3*3600
    while time.time()<deadline:
        transfer=json.loads((P/'STATUS.json').read_text())
        if transfer['status']=='COMPLETE':break
        if transfer['status'] in ['FAILED','STOPPED']:raise RuntimeError('Transfer '+transfer['status'])
        if (P/'STOP').exists():raise InterruptedError('OWNER_STOP')
        time.sleep(10)
    else:raise TimeoutError('Workstation staging deadline')
    assert os.path.ismount(MOUNT),'T500 must be mounted; refuse local fallback directory'
    done=json.loads((BACKUP/'COMPLETE.json').read_text());assert done['status']=='TRANSFER_VERIFIED'
    restored=BACKUP/'restored';cut=done['final_N'];TARGET.mkdir(parents=True,exist_ok=True)
    assert not (TARGET/'packet').exists(),'Do not overwrite an existing workstation restart'
    state.update(status='STAGING_RESTART',cut_N=cut);save(state)
    assert sha(RUNTIME_ARCHIVE)==RUNTIME_SHA
    with tarfile.open(RUNTIME_ARCHIVE) as t:t.extractall(TARGET,filter='data')
    packet=TARGET/'packet';packet.mkdir()
    source=restored/'packet'
    for p in source.iterdir():
        if p.is_file() and p.name not in ['STOP','controller.lock']:shutil.copyfile(p,packet/p.name)
    for folder in ['inputs','vendor','identities','setup_history']:shutil.copytree(source/folder,packet/folder)
    checkpoint=json.loads((packet/'CHECKPOINT.json').read_text());assert checkpoint['last_completed_N']==cut
    (packet/'results').mkdir();(packet/'sources').mkdir()
    for row in checkpoint['latest_artifacts']:
        src=source/row['artifact'];dst=packet/row['artifact'];shutil.copyfile(src,dst);assert sha(dst)==row['sha256']
        name=Path(row['artifact']).name.replace('.json.gz','.json');shutil.copyfile(source/'sources'/name,packet/'sources'/name)
    os.symlink('../runtime',packet/'runtime')
    # Copy immutable source, then change only this successor's storage paths.
    old_manifest=json.loads((packet/'CODE_MANIFEST.json').read_text())
    for name,h in old_manifest.items():assert sha(packet/name)==h,name
    (packet/'UPSTREAM_POD_CODE_MANIFEST.json').write_text(json.dumps(old_manifest,indent=2)+'\n')
    code=(packet/'campaign.py').read_text().replace("persistent_root='/workspace/gen4'","persistent_root=str(P/'persistent')")
    code=code.replace("mirror='/workspace/gen4/runs/frustrated-spin-packet-continuation1'","mirror=str(P/'persistent/run')")
    code=code.replace('disk_reserve_bytes=200*1024**3','disk_reserve_bytes=20*1024**3')
    (packet/'campaign.py').write_text(code)
    (packet/'CODE_MANIFEST.json').write_text(json.dumps({name:sha(packet/name) for name in old_manifest},indent=2)+'\n')
    for name in ['memory_policy.py','profile_hooks.py','fast_io.py']:
        shutil.copyfile(REPO/'GEN4/frustrated_spin_resume1'/name,TARGET/name)
    shutil.copyfile(P/'workstation_launch.py',TARGET/'workstation_launch.py')
    (TARGET/'ORIGIN.json').write_text(json.dumps(dict(source=str(BACKUP),cut_N=cut,full_historical_results=str(source/'results'),
        runtime_sha256=RUNTIME_SHA,canonical_answers_unchanged=True,imported_cost_model=False),indent=2)+'\n')
    # Qualify in a separate directory, preserving inherited source/result ledgers.
    qualification=TARGET/'qualification';qualification.mkdir()
    for name in [*old_manifest,'CODE_MANIFEST.json']:
        dest=qualification/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(packet/name,dest)
    os.symlink('../runtime',qualification/'runtime')
    (qualification/'identities').mkdir()
    state.update(status='QUALIFYING_WORKSTATION');save(state)
    with (TARGET/'QUALIFY.log').open('w') as log:
        result=subprocess.run([str(PYTHON),str(TARGET/'workstation_launch.py'),'--qualify'],cwd=TARGET,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    assert result.returncode==0,(TARGET/'QUALIFY.log').read_text()[-3000:]
    assert json.loads((qualification/'QUALIFICATION.json').read_text())['status']=='PASS'
    shutil.copyfile(qualification/'QUALIFICATION.json',TARGET/'WORKSTATION_QUALIFICATION.json')
    # Owner requested continuation beyond N1350 after the full verified download.
    command=f'{PYTHON} {TARGET}/workstation_launch.py --steps 1 --hours 1'
    (TARGET/'README.md').write_text('# Workstation frustrated-spin restart\n\nOwner: Sean Brady.\n\nVerified inherited packet checkpoint through N'+str(cut)+'. Full older answers remain on T500 at '+str(source/'results')+'. Local working results start with the final checkpoint; sources, methods and full verification are preserved. CPU local hardware qualification passed against retained N120 authority in a separate directory.\n\nNext exact N: '+str(cut+1)+'.\n\nRun one next N (all three packet families):\n\n    '+command+'\n\nUse --steps and --hours to bound continuation. Exact source answers are always independently recomputed and compared. Native runtime is isolated; no global selectors changed. CPU cost observations carry this workstation runtime identity. This launcher continues packet exact results; completed dense magnetization GPU work and dense graph sources are retained on T500.\n\nStop safely with packet/STOP or SIGTERM. Remove that STOP file only when intentionally resuming.\n')
    with (TARGET/'RUN.log').open('w') as log:
        child=subprocess.Popen([str(PYTHON),str(TARGET/'workstation_launch.py'),'--steps','50','--hours','2'],cwd=TARGET,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    time.sleep(2)
    assert child.poll() is None,(TARGET/'RUN.log').read_text()[-3000:]
    state.update(status='WORKSTATION_CONTINUATION_LAUNCHED',cut_N=cut,next_N=cut+1,target_N=cut+50,qualification='PASS',controller_pid=child.pid,restart_command=command,finished=time.time());save(state)

if __name__=='__main__':
    try:main()
    except Exception:
        save(dict(status='FAILED',pid=os.getpid(),error=traceback.format_exc(),time=time.time()));raise

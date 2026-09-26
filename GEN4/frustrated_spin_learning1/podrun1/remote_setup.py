from pathlib import Path
import tarfile,shutil,subprocess,json,time,os
base=Path('/opt/gen4-learning');root=base/'GEN4/frustrated_spin_learning1'
with tarfile.open(base/'small.tar.gz') as t:t.extractall(root,filter='data')
shutil.copytree(root/'podrun1/spin_vendor',root/'vendor/spin_vendor',dirs_exist_ok=True)
# Restore runtime code and parent-plan resources only. Unused mathematical library objects,
# ATOM3D packet data, and unrelated packet corpus were omitted from transfer.
(root/'podrun1/TRANSFER_SCOPE.json').write_text(json.dumps(dict(omitted=['mathematical_library/objects','PACKET_NATIVE_THETA18_PACKETS.jsonl','GRAMMAR_RESPONSE.i64le','DEFAULT_PACKET.json'],reason='unreferenced by this source-bound frustrated-spin adapter'),indent=2))
subprocess.run([str(base/'venv/bin/python'),str(root/'podrun1/controller.py'),'--test','3'],check=True)

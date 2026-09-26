#!/bin/bash
set -euo pipefail
cd /opt/gen4/restore14/packages
python3 - <<'PY'
import json,hashlib
from pathlib import Path
m=json.loads(Path('MANIFEST.json').read_text())
for n in ['runtime-predecessor.tar.gz','exact-source.tar.gz','catalog-code.tar.gz','training-code.tar.gz','focused-code.tar.gz','n120-code.tar.gz','activity.so']:
 assert hashlib.file_digest(open(n,'rb'),'sha256').hexdigest()==m[n]['sha256'],n
print('ARCHIVES VERIFIED',flush=True)
PY
extract() { mkdir -p "$2"; tar -xzf "$1" --strip-components=1 -C "$2"; }
extract runtime-predecessor.tar.gz /opt/gen4/current
extract exact-source.tar.gz /opt/gen4/n96-benchmark1/source
extract catalog-code.tar.gz /opt/gen4/spin-catalog1
extract training-code.tar.gz /opt/gen4/spin-training1
extract focused-code.tar.gz /opt/gen4/spin-focused1
extract n120-code.tar.gz /opt/gen4/spin-n120-frontier1
extract installation.tar.gz /opt/gen4/spin-focused-install1
mkdir -p /opt/gen4/n72-benchmark1
cp activity.so /opt/gen4/n72-benchmark1/activity.so
python3 -m venv /opt/gen4/venv
/opt/gen4/venv/bin/pip install -r ENVIRONMENT.txt
export PYTHONPATH=/opt/gen4/current PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0
/opt/gen4/venv/bin/python /opt/gen4/spin-focused-install1/install.py --root /opt/gen4/current --evidence /opt/gen4/restore14/install-evidence
/opt/gen4/venv/bin/python /opt/gen4/spin-focused-install1/adopt.py --root /opt/gen4/current --out /opt/gen4/restore14/adoption
printf 'RESTORE_AND_ADOPTION_COMPLETE\n'

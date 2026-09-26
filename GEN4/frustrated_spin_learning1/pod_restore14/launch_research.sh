#!/bin/bash
set -euo pipefail
source /opt/gen4/restore14/activate.sh
cd /opt/gen4-learning/GEN4/frustrated_spin_learning1/podrun3
python - <<'PY'
import json,time
from pathlib import Path
assert json.loads(Path('/opt/gen4/restore14/QUALIFICATION.json').read_text())['status']=='PASS'
r=json.loads(Path('qualification/RESULT.json').read_text())['value']
assert r['status']=='EXACT' and r['restored_backend'] and r['full_density_equal']
assert json.loads(Path('STATE.json').read_text())['deadline']>time.time()
PY
exec python -u controller.py

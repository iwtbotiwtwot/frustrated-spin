#!/bin/bash
set -eu
cd /opt/gen4-learning/GEN4/frustrated_spin_pod14_learning1
. /opt/gen4/restore14/activate.sh
export PYTHONDONTWRITEBYTECODE=1
nohup /opt/gen4/venv/bin/python -u controller.py --hours 8 > RUN.log 2>&1 < /dev/null &
echo $!

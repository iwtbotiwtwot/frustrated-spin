#!/bin/bash
set -euo pipefail
source /opt/gen4/restore14/activate.sh
cd /opt/gen4-learning/GEN4/frustrated_spin_learning1/blind_restart1
exec /opt/gen4/venv/bin/python -u controller.py --hours 8

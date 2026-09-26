#!/bin/bash
set -eu
cd /home/sam/PycharmProjects/SAM_Research_Project
exec .venv-r3/bin/python -u GEN4/frustrated_spin_learning1/controller.py --hours 8

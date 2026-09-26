---
entry_id: H001732
entry_date: 2026-09-25
entry_type: RESULT
status: IMMUTABLE_HISTORY
supersedes: H001730
prior_entries: [H001730, H001729, H001726]
affects_live:
  - SAM_LIVE/00_CURRENT.md
  - SAM_LIVE/01_SLC_CURRENT.md
  - SAM_LIVE/10_PODS_CURRENT.md
---

# Four-A100 spin comparison and owner pause

Prior live state:H001730retains local wider N144 plans,no fresh frontier spectrum.
New state:owner-provided four-A100 pod inspected and GEN4/spin tools restored;
12N144width/batch configurations completed;fresh exact N120 started,then owner
paused all frustrated-spin work. Remote stop cannot be confirmed after bothSSH
routes failed. No further work or automatic resumption is authorized now.

[N144 result](../../GEN4/spin_n144_a1001/RESULT.md):same frozen connected signed
source,widths18–27,12configurations,240sampled modular tasks+48warmups. All actual
widths measured. Lowest observed compute projection:width24/root32,6.71h;
width25/root16close at6.76h. These are bounded partial-work extrapolations,not
complete N144 solve times. No fresh full N144 answer.96CPUworkers searched72044
lower-width candidates;16thread map preparation and demand-built exact branch
templates are scoped successors.2048reference branch templates match exactly.
Native empirical selector recovered after reopening;source/hardware-specific,
not a universal N-only model. Policy ref:
c1b23c98463f9a83babeedfa91486923369aae095c485cf253e9d2df8b0580f9.
All results/source/telemetry/native checkpoints are local and persistent;archive
71483193bytes/SHA25666deb533c76c313d6bca0db23102d01bbff2592caceffd39bcb8646060fb6705.

[N120 pause](../../GEN4/spin_n120_a1001/RESULT.md):fresh retained connected source,
width21/2048branches. Batch256short calibration13%faster than16;full4worker run
started. Last observed109/2560tasks,all4GPUs100%utilization;30second checkpoint
policy to/workspace/gen4/runs/spin-n120-a1001/exact. Latest checkpoint not retrieved.
No new exact N120 answer returned. CPU graph-refinement upload/launch failed;
local script remains unexecuted. ExistingSSHsessions then closed,direct connection
refused,gatewaypublickey rejected. Worker termination unconfirmed;owner pause
blocks all new spin work until explicit resumption. No lifecycle action taken.

Pod4uxlvzwbn7v1fo,direct204.12.201.57:5345,4fullA100-SXM4-80GB/NVLink,
128advertisedvCPU/108.8cgroupCPUequivalents,1006999998464host-memorybytes.
GEN4P1/CE-P1 native spin arithmetic passes exact CPU/GPU adoption. Other archived
GPU capabilities were not requalified for A100. Scoped installations do not
change workstation defaults. N144 source is the prior agent computational
extension;fields/couplings unchanged. Unrelated paused work and Chalkboard remain
unchanged. No new physical-concept classification is assigned.

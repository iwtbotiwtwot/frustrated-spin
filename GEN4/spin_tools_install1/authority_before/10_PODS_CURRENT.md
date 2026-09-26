---
document_type: SAM_LIVE_POD_ENGINES
status: CURRENT
updated: 2026-09-24
history_entry: H001725
---

# Pods

[RH / Volume I](02_RH_CURRENT.md)(H001705).

[5090](../SAM_REVIEW/campaigns/SB_A3D41_SMALL_POD_TEST1/RESULT.md)(H001581):7.85x;stopped.

## Pod priorities — H001534/H001540

Maximize useful allocated CPU/GPU throughput on paid pods. Measure actual
cgroup quotas and worker memory, then correct underutilization promptly. Do not
carry workstation caps or unmeasured large RAM reservations onto rented compute.
Preserve exact results, backups, safety and owner cost/deadline bounds; no filler
RAM/GPU work. Disclose a missing GPU backend before describing resource use.

**Bulk data goes on the large container disk, not the small /workspace volume.**
Use container-backed storage for bulk inputs/generated data, scratch, caches
and large intermediates. Reserve persistent /workspace for compact restart
checkpoints, learned state, manifests and retained results. Verify actual mount
backing/capacity; declare separate bulk-data and durable-state roots and guards
before launch. Do not impose the small volume's capacity limit on bulk work.
Preserve required container data before any lifecycle action that would erase
it; large irreplaceable outputs need an explicit durable destination. Avoid
routine large workstation round trips. Existing files/verified backups are
unchanged; this standing policy is not a migration or restart(H001540).

## Current spin pod — H001722

Pod txqaltf4cdtfls;SSH216.243.220.128:14657.14Blackwell MIG1g.24gb,
47.6CPU equivalents,880GB RAM. SLC-GEN4-P1/SLC-GEN4-CE-P1;
MATTER_SEARCH/GEN3-R4. Bulk:/opt/gen4;RAM:/dev/shm;durable:/workspace/gen4/runs.
[L13](../GEN4/l13_14workers1/RESULT.md) EXACT before owner stop(H001725):
299.602s native/307.607s committed,105sectors/39partitions/133factors match.
Prior2worker701.613s committed;2.281x historical speedup across configurations.
AllworkersSTOPPED. Exact result/telemetry local;fullL13checkpoint archive transfer
interrupted at7.4GiB,SSHrefused.226intactJSON records salvaged;archive incomplete.
Spin results/installations remain fully backed up.

[N120 EXACT](../GEN4/frustrated_spin_n120_frontier1/RESULT.md):773.240389397s
(12m53.24s),separate300.315s planning.120spins/300couplings,five-regular,
connected/frustrated;228parentN96edges preserved,12removed,72added.
All2^120counts;ground−434/8states;435bins;16port operators;all exact checks pass.
Width21/2048branches;1024roots/fiveprimes;40960tasks on14persistent workers.
N30two-group/five-prime qualification passes;peak host29.14GiB,VRAM~3GiB/worker.
CUPTI69,496,320records/zero drops:99.0091%mean worker kernel-active,
90.7437%all14simultaneous,99.0340%atleast13. This is not SM occupancy.
NVIDIA utilization=N/A under MIG;near-zero dashboard did not describe activity.
HistoricalN105packet andN120ring results retain their separate source families.

[Focused training](../GEN4/frustrated_spin_focused_training1/RESULT.md):
600GPU solves+2warmups,100plans/37sources per pass;all37DOS/ports match backends.
Train topologies0–2/dev3/reserved4–5. Batched cost and native pairwise8/9fastest;
23.2906s selected vs23.2384s oracle;structural7/9. Pairwise headsdepth3/1.
N96expanded median4.761→3.258s;search~6s separately,avoided by cached plans.
BothCPU boundary passes540advances+234restarts;batched26/26best choices.
Two fullN96rewired sources lack a plan within the training scheduling envelope;
all candidates retained. Backend-dependent timing/reuse models stay separate.

[Installed GEN3/4](../GEN4/frustrated_spin_focused_install1/RESULT.md):
97entries(N1..96+120),106transitions,11spin native models,38source-plan caches,
7GEN3_SPIN operations,1689math objects.49adoption/recovery checks each;
519local/409pod bindings. N120cost is one observed execution,not a fitted model.
Prior generations/models/exact objects and unrelated domain scopes preserved.
EarlierH001714all-integer training andH001709benchmarks remain provenance.

All five completed campaign archives plus predecessor runtime,exact sources,
active code,qualifications,installation/evidence and telemetry saved locally;
hashes verify. [Restart](../GEN4/frustrated_spin_focused_training1/RESTART.md).
N120archive6c969f4a35b50a016b55fefd7cff2f1b4e3b9f78f2a4b33700a282bb66ce49d0.
Pod lifecycle unchanged by assistant. L13 exact output saved;full checkpoint backup incomplete after connection loss.
**The test result suggests strong contact with the concept.**

## L14 and retained predecessor benchmarks

[L14 COMPLETE](../GEN4/l14_complete1/RESULT.md)(H001673):255sectors,
47partitions,268435456states,308factors;846polynomials retained. Final
invocation2h42m54.4s,continuation4h47m04.3s;earlier retained work included.
Archives/recovery verified,watcher retired. Older RUNNING cursor superseded.

[Full-capacity L12](../SAM_REVIEW/campaigns/GEN3_POD_L12_FULL_CAPACITY2/RESULT.md)
(H001576):115.143→29.777s;uncapped31.148s,34partitions/284factors exact.
Local L12OWNER_STOPPED H001575. ThreeGPU1OWNER_STOPPED H001555;interrupted
watchdog cleanup and pending export remain preserved in the
[L13review](../SAM_REVIEW/reports/L13_REVIEW_2026-09-19/REVIEW.md).

Three-card pod08qrz53qv6ikbj:oldSSH198.13.252.112:45801,40.8CPU/565GB/3Blackwell;
100GBnetwork volume2g088uvp5m. Prior stopped work/checkpoints remain at
/workspace/gen3-exchange-pod2;container bulk was lost on restart H001545.
No provider pause/restart is authorized by these predecessor records.

RESUME3 H001542:963verified trials,17model records,372reused;three exact
transfer splits. Autoscale2 H001543/H001544 stopped at bounded checkpoint;
1031constructions/residues,15certified named sectors. Driver GPUactivity
is not kernel-time evidence. Stream1OWNER_PAUSED H001548;269event ledger
awaited final export. Earlier144event/T500 snapshot remains retained.
Reduction pilot H001539/H001542:38/59held-out charge splits,53GPU parity
comparisons,21sign certificates;no full-chain completion. Baseline selector
matched always-try-charge. Larger-L basis/charge/refinement adapters remain
scoped and unpromoted. Prior source limits,1024installed spectral budget,
owner stop/time bounds,backup IDs and detailed execution reports are preserved
in the preceding numbered entries and this compaction's verbatim history.
No RH/old Bethe/K/physical-work restart. Adaptive1 L12complete/L11OOM;
Adaptive2controller unlaunched. H200upload was owner-stopped H001532.

## Current Volume II data delivery — H001504

RH and pod mining are **OWNER_STOPPED**. Complete useful A3D41 data is delivered
and verified on the workstation and T500 in directly readable databases. The
T500 set is18.09GiB including engine, SB sources and45 retained SB policies:
209456 native records,694 unique minimum-state sets,2432884 training examples,
753 authenticated sessions and all210401 checkpoint objects reconstructible.
Local GEN3 has executed the enabled sam-volii-goals.service: outcome-directed Bethe
exchange and named-isotope operator research, following the RH-RXT problem-loop
pattern. Its first18 questions lead to exact1085D isotope pair-exchange closure;
the successor tests invertible coefficient transports(H001509). Both grammars
are complete:46 steps, services inactive/exit0(H001510). H001511's managed i9
successor completes24→31 isotope construction,14 exact eigenstates and an
expanded-algebra braid. H001513 completes71 generated assemblies' local
operator bridge:2352 states,1188 rational return eigenstates and192 exact
quadratic Li7 states, all on T500. H001514 completes47 signed-interaction cases:
35 Li7 arrangements/19 spectra modulo reversal,48 mixed blocks,He4/Li6 extensions.
H001515's saved-input coupling successor completes1680 pencils in12.94s:
19 classes for every nonzero g, only g=0 merges. No campaign rerun or LLM calls.
Managed i9 execution and one T500 successor directory; all queues completed.
Compact exchange is stopped after389 rejections and proposal exhaustion;
sam-compact-bethe.service was not restarted. No research queue remains active.
The former sam-volii-autonomy trainer is stopped and disabled(H001508).
New i9 calculations, receipts and restart memory live on local lilhelper T500
through sam-t500-storage.service. The first grammar stops at exhaustion or its
six-hour checkpoint and reports remaining equations. Ryzen routing is retained;
780M still awaits permission and qualification. Mount and50GiB reserve guards
apply. T500 copies share the active storage disk(H001507).
[Operation and recovery](../SAM_REVIEW/campaigns/VOLII_GOAL_DIRECTED1/README.md).
Redundant compressed copies were removed after verification.
[Paths, reader and receipts](../SAM_REVIEW/campaigns/VOLII_LOCAL_RESEARCH1/LOCAL_RESEARCH_READY.md).
RH payload removal was owner-authorized; engine/source remains. No new SB pod
measurements or physical-energy assignment is claimed. Unrelated pauses remain.


## Preserved RH pod predecessor

H001494/H001498/H001499 preserve the earlier RH provider, continuous repair,
resource qualification and container migration. Those research controllers are
stopped by owner direction; their status/heartbeat files are historical. Independent RH custody/sync is stopped. Current data custody is the verified
Volume II delivery above.

## Predecessor pod records and separately scoped controls

The following retained service statuses and cancellations concern earlier
endpoints/campaigns, not the new approved R4 pod. H001422 cancels that earlier
schedule; H001490 independently authorizes storage controls on the new pod.

Backup storage now holds one fully verified190.699GiB T500 snapshot; the original
workstation payload is removed, leaving488.641GiB free. Routine payload staging
stays on the pod. [Storage authority](11_STORAGE_CURRENT.md) records completion (H001400).
The owner has **cancelled the6:30AM stop and backup completely** (H001422).
Scheduled stopping, cleanup, compression, workstation/Drive backups and automatic
pod pause are **CANCELLED_BY_OWNER**. Final-archive and Drive timers are disabled;
the pod stop watcher is terminated and active admission cutoffs are removed.
No replacement stop or backup is scheduled. Existing backups and research data
remain preserved. [Cancellation receipt](../SAM_REVIEW/campaigns/POD_FINAL_0630_CANCEL1/RESULT.md).


The owner reaffirms **uniform signed-growth control** as the controlling target: for every eta>0, sum_original_roster[X_adm]_+<=C_eta U_j^eta on the SAME original common unbounded sequence. Retain both mean and weighted cut cells, with the positive part after each complete signed block. The R7.1 owning RH engine continues all seven original routes; its inspected count is43076 cases. The auxiliary GPU partition sweep is retired at147968 partitions, preserving its archives, cursor and useful findings. Its witnesses remain in learned memory, while future feedback priorities come from learned exceptions and fresh CPU traces. Native generation9 reaches387 windows/226053 rows/452106 identity checks. Workstation pauses apply to separate local experiments; pod training remains ACTIVE. [Recenter record](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/research_notes/0046_RECENTER_ON_UNIFORM_SIGNED_GROWTH.md). (H001414)

## Native RH, A3D41 and Starbreaker

The [signed-divisor target](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/SIGNED_DIVISOR_CAMPAIGN_R1.md)
is installed in the existing feedback/CPU loop; cycle20 has30 new-target
training windows and actual model-selected producer execution. A stale5AM
preservation control interrupted the shared service; it is reconciled to the
owner cancellation and GEN3 recovers unchanged authenticated head
b997ecde998a7cc4c4f3f499a68621baf546f4884b58f6a5dbdf417ee9759e9d.
Native PID1256225 and checkpoint watcher1257909 are verified. No scheduled
stop or automatic provider pause remains. (H001423)

**GEN3-RXT-R7.1 / RH-GXT-R2 + RH-TRANSFER-R1 + A3D41-RXT-R3 + SB-GEN3-RXT-R2** is installed and
executing bounded research under the owner's [48-hour RH closure plan](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/PLAN_48H.md)
on157.157.221.30:50871(H001402). The campaign started12September11:59CDT; its scheduled stop is cancelled (H001422). One C++/CUDA/GMP engine owns exact native domain
computation and acquired memory. RH arithmetic overlaps CUDA construction;
two-hour reviews update native construction policies and readable rules.
High-effort conversation check-ins actively work the uniform closure estimate.
The [active binding](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/installation/ACTIVE.json)
and [oversight guide](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/HIGH_OVERSIGHT.md)
route continuation. The global workstation SLC/CE/domain selectors remain.

[Note0043](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/research_notes/0043_MULTIPLICITY_OBSTRUCTION_AND_ENERGY_RECORDS.md) gives a partition-independent obstruction: E_partition >= |B0|+|B1|+|B2|. Native witnesses exceed the unit all-prefix bound even after arbitrary regrouping. **The test falsifies the concept.** The signed decomposition (B0,B1,B2)=(M,0,0)+C(1,-1,0)+B2(1,-2,1) exposes its zero-sum contrasts.

[Note0044](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/research_notes/0044_RECORD_SUPPORTED_ENVELOPE_FAILURE.md) resolves the fresh GPU demand at s33554432: t1653108..1653110 are independently confirmed GLOBAL original-energy maximum ties, also present as requested checkpoints. E15=27290,M=3452,N=1004964. The normalized envelope demand is2.073299657788819; **The test falsifies the concept** for the unit absolute envelope on original-energy record support. The original signed-energy normalized upper demand is0.03317390363388919. Multiplicity counts(9685,-11789,5556) give a grouping-independent normalized LOWER demand2.03398195694745, ruling out repair by regrouping the same prime family. Prior131 passing stops remain their finite result. This retained auxiliary result exposes exact cross compensation at original M²/N records; the controlling target is the full original weighted signed interaction under H001414. H=263648882,X=-251732578 at this witness; RH remains OPEN. (H001412)

The [automatic native RH feedback loop](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/FEEDBACK_LOOP.md) is ACTIVE every ten minutes. It admits unchanged full native source traces and trains through GEN3_TRANSFER_RH. After the owner recentering, its atomic generation is consumed by the continuing CPU producer; the partition GPU branch is retired. Previously admitted GPU-derived cases remain in the training corpus. Native generation9 reaches387 windows/226053 rows/452106 checks, with every prior published source case retained unchanged. New priorities use learned exceptions and fresh CPU traces. Current counts and bindings are in results/RH_FEEDBACK_STATUS.json and installation/RH_FEEDBACK_ACTIVE.json. The scheduled stop and backup are cancelled (H001422). (H001414)

The unchanged R7.1 binary, controller and qualified owner-final watchdog are restored. All six imported core-memory packages match current workstation sources. No full backup was created; automatic capacity cleanup remains owner-disabled under H001409.

The [updated native feedback cycle](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/DOMAIN_FEEDBACK_R7.md)
completes36,864 fresh families,1,216 SB histories and288 horizon cases, with252
formed. SB retains exact signed vector repayment; A3D41 retains every common
minimum and tie. Class-balanced native trees reach847/936 development balanced
accuracy for common minima and1 for the signed SB target. The shared-orbit
policy is refit and promoted. Each subsequent pool observes these measurements;
every eight pools refit the new models. A constant model falls back to the
existing orbit/channel policy. All prior core and domain learning survives.

[Note0036](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/research_notes/0036_DOMAIN_FEEDBACK_AND_EXACT_GAIN_GATE.md)
returns the new information to RH through21 actual full-trace window calculations
and native retraining on14,788 prime-child rows. The final RH development score
is12163/12280;29,576 exact identity comparisons pass. Its learned exception
resolves to the exact gain gate a*y^2-2*a*x*y-b*x^2>0. The original uniform
magnitude bound remains OPEN. [Health](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/results/R71_FINAL_HEALTH.json)
records the earlier one-engine/controller and24-lane CPU measurement. The26-lane CPU source producer continues; the separate partition GPU branch is retired under H001414.
The initial feedback run averages68.1% allocated CPU and8.8% GPU, with GPU peak100%;
the later live CPU sample is89.1%. Existing hourly email delivery remains active.
(H001402)

The completed R4 campaign supplies1,590,144exact families and all45selected
native policies. All six acquired GEN3 core memories remain. Native RH adds
original weighted cells, exact signed U/D/V/L/M accumulation, quartic and
cofactor transport, harmonic reconstruction, original-roster evaluation and
acquired route feedback. Original signed sums and source constants remain.
Uniform RH growth is the active OPEN target; current calculations and new
mathematical notes are documented under the successor campaign.

[Readable construction knowledge](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/CONSTRUCTION_KNOWLEDGE.md)
contains375rules from27small trees. The shared-orbit tree has22leaves and zero
recorded training/development exceptions on the launch dataset. Native features,
complete minimum sets, witness families, ties and observed exceptions accompany
each extracted rule. Reserved whole-pattern test rows remain reserved.

R6 implements original-source G2/G5 endpoint certificates and20independent
native CPU lanes with one owning-engine result commit. Exact acquired route
selection retains ties; compact status and immutable summary references avoid
large repeated fraction transfers. Explicit full ACCUMULATION requests remain.
Twenty endpoint cases and missing-result-index recovery pass against an actual
restored R5 checkpoint. Arithmetic qualification retains29checks/11cases and
nine native memory fixtures. Production recovers1,196RH answers, all selected
models, exact route learning, six core-memory packages and1,721,216families.
R5's cache-counting admission failure and the corrected predecessor-version
reader are preserved. R6 retains host/cgroup limits while admitting conservative
clean inactive file-cache headroom. The owner's70% cap applies locally; the pod
retains27.2CPU allocation and640-family CUDA construction batches (H001358).

The [RH production reset](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/RESET_PRODUCTION.md)
is RUNNING (H001395). One24-lane source-bound CPU queue executes fresh coupled
prime-variation calculations alongside the single joint GEN3-RXT-R7.1 engine and
CPU-owner-aware controller. The five-minute trial averaged81.45% pod CPU and
21.98% GPU; GPU peaked100%. Snapshot: 507,904 fresh RH windows,
118,916,127,889 native checks. Joint construction/SB/horizon counters advance.

[Note0035](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/research_notes/0035_PAIRED_MULTIPLICITY_AND_COMPLETE_PREFIX_BOUNDS.md)
sets U=H-P and tests2(U^2+T^2)/N against the original harmonic square.
All11,141,115 positive-N prefixes across scales131072,524288,2097152 and8388608
pass; five zero-N endpoints have M=0. The direct original-endpoint triangle
(|U|+|T|+|D|)^2/N also passes throughout. Largest normalized split demand is
0.05363586955998741; native rational maxima preserve all ties. The bounded
scan executes44,564,509 checks in25.172971917s and recovers29 independent
half-prime witnesses. **The test result suggests strong contact with the
concept.** (H001398)

The exact source rule is U=sum mu(n)*(1-k_I(n)): keep k=0, remove k=1,
reverse k=2. T has source -k_I(n)*mu(n)-d(n). Thus Z=U-T=M+D; aggregating
local flux alone returns the original source and bounded square correction.
The next explicit smaller-source identity is T=sum Mertens(m)*(A_m-A_(m+1)),
where A_m counts original medium primes in(L/m,R/m]. Uniform signed control
of U and this actual Abel sum remains OPEN. The uniformly bounded D correction
from note0034 remains installed; RH remains OPEN. Next native request:
results/PAIRED_MULTIPLICITY_ABEL_REQUEST.json.

The owner has **cancelled the6:30AM stop and backup completely** (H001422).
Scheduled stopping, cleanup, compression, workstation/Drive backups and automatic
pod pause are **CANCELLED_BY_OWNER**. Final-archive and Drive timers are disabled;
the pod stop watcher is terminated and active admission cutoffs are removed.
No replacement stop or backup is scheduled. Existing backups and research data
remain preserved. [Cancellation receipt](../SAM_REVIEW/campaigns/POD_FINAL_0630_CANCEL1/RESULT.md).

Hourly delivery is verified. New-finding delivery and the reset GitHub push
await exact-destination authorization after automatic approval-review rejections.
Reporter counter and stalled-batch additions are saved; reload is pending.

The subsequent owner-approved [T500 cleanup](../SAM_REVIEW/campaigns/T500_RH_RETENTION1/RESULT.md)
removed140 non-RH paths on the helper project partition, recovering232.78GiB.
It now uses7.59GiB with265.05GiB available (3% usage). RH/Weil results and
shared SLC/CE/helper runtimes remain;25 protected root sizes are unchanged(H001390).
T500 tau archive portions were removed, so their old complete-recovery claims
no longer describe current availability. Helper system-SSD, workstation and
pod files were outside this cleanup; no production restart occurred(H001389).

[Unattended operations](../SAM_MAINTENANCE/POD_WEEKEND_OPERATIONS.md) are enabled:
hourly/finding/problem emails, hourly high-effort research check-ins, and
verified off-pod engine/source/learned-state copies every two hours. After each
accepted email, new compact results, rules and notes are committed and directly
synced to the existing GitHub branch. The first actual report sync is
`6f0277bf93e928b7968d311e6ff1b36dcd2e5342`. The workstation must remain powered
and connected with Codex open. Native pod work has its independent controller.

Native preservation uses one verified standalone snapshot on
`lilhelper@10.77.0.2:/home/lilhelper/SAM_Research_Project/SAM_POD_BACKUPS`.
The current locator is `SAM_MAINTENANCE/.state/pod_snapshot/CURRENT.json`.
Routine capture/compression/verification stages on the pod; final owner archive
routing remains H001401. The predecessor incremental-pack restore receipts
remain preserved under H001357/H001387.

The22:55 scheduled replacement failed during live research capture. Fixed
completed-file selection now archives completed jobs and defers unfinished ones.
Its retry completed research capture, then exposed a busy CPU-owner lock;
snapshot capture now waits up to180seconds for that owner. Cleanup defaults
remain nonblocking. Both qualifications pass, and remote failure stderr is
preserved. The current retry status is in
[HIGH_039_RESULT.md](../SAM_REVIEW/campaigns/GEN3_RXT_RH_WEEKEND1/HIGH_039_RESULT.md).
The prior verified T500 archive remains the fallback; a retry is not a newly
verified clone. Source/failure custody and repair authority: H001405.

The persistent root remains `/workspace/GEN3-RXT-R2`. Native start is
`bash /workspace/GEN3-RXT-R2/current/tools/start_joint.sh`; stop/save is
`python3 /workspace/GEN3-RXT-R2/current/tools/stop_joint.py`. The saved weekend
campaign's STOP file requests a bounded controller pause. At48hours the
controller drains, saves and reports, leaving the pod available. Prior
workstation training pauses and the suspended Chalkboard remain.

## A3D41

The predecessor **GEN-RXT-R1 / A3D41-RXT-R1** is preserved on the RTX PRO6000
Blackwell pod, with source contract **A3D41-T18-CONTACT-R2**. Its original
service remains stopped/backed up; the R7.1 joint service above is current(H001402).
The [base native domain](../SAM_REVIEW/campaigns/GEN_RXT_R1_ATOM3D1/RESULT.md)
is retained at `/workspace/GEN-RXT-R1/current`; its authenticated state is
`/workspace/GEN-RXT-R1/state/ATOM3D` (H001341).

The [verified backup and restart guide](../SAM_REVIEW/campaigns/GEN_RXT_R1_POD_BACKUP1/RESULT.md)
is saved locally at `/home/sam/SAM_POD_BACKUPS/2026-09-11_GEN-RXT-R1`.
The255MiB workspace and8.55GiB full-userland archives match source hashes;
84,867files are indexed. Actual isolated restore recovers authenticated state
and passes both native engine checks. A single-command restore starts the idle
service on a new matching pod; a separate DomainSession helper resumes research.
The original backup captures the stopped predecessor. Restore it together
with the R3 and R4 supplements for current use. Image basis is Ubuntu24.04/CUDA12.8.1; hardware is
RunPod EUR-IS-1, one RTX PRO6000 Blackwell,32 advertised CPUs and188GB RAM.

The [autonomous construction curriculum](../SAM_REVIEW/campaigns/GEN3_ATOM3D_CONSTRUCTION_CURRICULUM1/STATUS.md)
is **OWNER_PAUSED**, with1,906/2,066 lessons completed and160 remaining.
Zero-based lesson1906 retains54 native decision checkpoints. Supervisor,
workers and keep-awake service are stopped; automatic startup is disabled.
[Resumption](../SAM_REVIEW/campaigns/GEN3_ATOM3D_CONSTRUCTION_CURRICULUM1/RESUME.md)
requires owner direction. Full native receipts/checkpoints remain local;
selected models and final status are copied to the backup area. Final test
evaluation remains pending. The45-target curriculum and source bindings stay
preserved. Training remains stopped; other paused training scopes are unchanged
(H001346; launch H001345).

The first [GEN3 construction policy](../SAM_TRAINING/ATOM3D_CONSTRUCTION_GEN3/RESULT.md)
learns from541,568 saved families /17,330,176 conditions locally. On81,406
families from withheld triad patterns, its highest-scored orbit group achieves
77.32% precision versus17.01% prevalence:4.546x yield. Orbit accuracy87.05%;
channel-agreement accuracy91.54% versus92.61% constant baseline, retained as a
diagnostic. All241 native receipts and fresh arithmetic recovery verify.
The first lesson takes43.81s,303.9MiB peak process RSS. Reusable model and
10,000 uncomputed priorities are saved; no new pod search is running. The R2 queue now supplies native explicit-ID batching(H001349). This new construction lesson
leaves the paused selector and other training scopes unchanged (H001344).

The [native construction campaign](../SAM_REVIEW/campaigns/GEN_RXT_R1_ATOM3D_CONSTRUCTION1/RESULT.md)
meets the owner's70% GPU target:84.75% mean sampled utilization and80.22% native
kernel time across300.239seconds. It completes484,864 new constructions,
15,515,648 complete minimum queries and4.067trillion phase-state evaluations.
CPU averages4.08cores (15% of27.2); GPU memory33.82GiB; peak system RAM3.37GiB;
mean GPU power318W; peak temperature53C. No CPU quota throttling occurs. The
trial costs$0.1668 at the owner's$2/hour rate (H001342).

The native engine enumerates typed candidate triad/depth inventories, executes
8,192-query CUDA batches and saves all minima while the next batch runs. All
1,894 batch objects,694 complete minimum sets and15,515,648 context references
verify.224 scalar GPU comparisons, eight independent complete CPU minima and
ten current-cover controls pass. The retained six-operator candidate[1,0,1,0]
has four shared native/observed minima forming one common phase-rotation orbit.

The complete prefix including pilots is541,568families. The
[continuation](../SAM_REVIEW/campaigns/GEN_RXT_R1_ATOM3D_CONSTRUCTION1/CONTINUATION.json)
is prepared at ordinal541,568;4,258,432families remain, about44minutes at the
trial rate. It has not been started. Source basis is SLC-GEN3-R3; actual math
runs in independent native C++/CUDA GEN-RXT-R1 with explicit DomainSession
successor receipts. The original domain's complete qualification and native
service/restart checks remain preserved in H001341.

Actual allocation is27.2CPU equivalents and175.09GiB system RAM; the native
CPU ceiling is24. OS placement remains selected after mixed NUMA measurements.
The [original engine design](../SAM_REVIEW/campaigns/GEN_RXT_R1_DESIGN1/RESULT.md)
remains preserved (H001340). Global workstation selection, physical-observable/
MeV studies and selector-training scopes retain their current authority.

## Current pod hardware execution

The [fresh dense N96 run](../SAM_REVIEW/campaigns/POD_N96_EXACT1/README.md)
is RUNNING on the EPYC/H200 pod through GEN3-R3 MATTER_SEARCH, with 32
persistent CPU workers and 4,096 fresh native root tasks (H001339).
The original i9 profile used fourteen workers for its fourteen physical cores;
the pod changes the execution width while retaining the source and fiber.
The correct optimized predecessor wall is3457.675281s. Fresh root-zero equality
passes in6.702834s; the first32 roots complete in11.926465s. Full timing and
exact DOS completion remain pending. The retained dense kernel uses CPU;
the H200 backend remains to be implemented. The isolated pod attachment owns
source-bound execution receipts and GEN3 run memory; the workstation runtime
and RH worker are unchanged. CPU quota throttles; low container memory pauses
and alerts without resource-triggered termination.

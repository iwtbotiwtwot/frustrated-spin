---
entry_id: H001722
entry_date: 2026-09-24
entry_type: RESULT_INSTALLATION
status: IMMUTABLE_HISTORY
prior_entries: [H001714, H001717, H001718, H001720]
affects_live:
  - SAM_LIVE/00_CURRENT.md
  - SAM_LIVE/01_SLC_CURRENT.md
  - SAM_LIVE/10_PODS_CURRENT.md
---

# Exact N120 and focused training installed on GEN3/GEN4

[Exact N120](../../GEN4/frustrated_spin_n120_frontier1/RESULT.md) completes in
773.240389397seconds (12minutes53.24seconds),includingGPU preparation,modular
work/checkpoint handling and exact reconstruction. Separate CPU structural search
300.315419136seconds;RAM setup0.992seconds;N30qualification8.484501620seconds.

Source120spins/300couplings is connected,five-regular and frustrated. Agent
degree-preserving extension retains228parentN96couplings/alloldfields, removes
12disjoint edges and adds24crosslinks plus48new internal couplings. The frozen
source SHA256 isbed8dbc542412f88a76795573e157e369710a0bcf8d2b7358e10a159d98df1f4.
EarlierN105packet andN120ring families retain their own results. This is not a
claim about every graph atN120 or minimal treewidth.

Exact count1329227995784915872903807060280344576=2^120;ground−434/degeneracy8;
435occupied bins;16open/closed port operators. Count,first/second moments,port
counts and polynomial support pass. Spectrum04088a31a81a8424ec44bd8a582dffabd795ec2ba3bd127a9826e46aa228f254.
Planwidth21 after11conditioned spins;2048branches,1024roots,fiveprimes.
Fourteen persistent CUDAworkers complete40960tasks,16roots×16branches each,
with exact coverage and no restart. Fifthprime1224736769/root3 has source-bound
capacity/root/integer proofs;large-coefficient CRT and two-group N30GPU
qualification pass. Native sessionMATTER_SEARCH_38ef4f61dc5441f4980fbd0e55bad5bf
onSLC-GEN4-P1/SLC-GEN4-CE-P1/GEN3-R4. Resultref
c666aea038e62765896f9ae62a2a6be446e2df4c6cdd83f9f5f1790b47688ee4.

CUPTI69496320records,zero drops. Over the full772.666548321second modular phase,
mean worker kernel-active99.0091%;all14simultaneous90.7437%;atleast13active
99.0340%. These are actual kernel-time fractions,not SM occupancy. The user
reported near-zero live telemetry;NVIDIA directly returnsN/A utilization for
all6physical GPUs with MIG enabled. Dashboard N/A conversion is uninspected.
Initial analysis's serial-interval assumption was replaced by interval unions;
original diagnostic retained. Mathematical work was unaffected.

[Focused training](../../GEN4/frustrated_spin_focused_training1/RESULT.md):
600GPU solves plus2warmups across the same100plans/37sources;all37fullspectra
and port operators match across retained/batched backends. Whole-topology
train0–2/development3/reserved4–5 splits stay fixed. Two fullN96rewired sources
remain documented outside the campaign scheduling envelope;no scientific
exclusion. Retained cost8/9fastest;native pairwise6/9. Batched cost/pairwise8/9,
23.290642924s selected vs23.238427899s oracle;structural7/9. Native focused
headsdepth3/depth1. Both selected cost models are ridgealpha0.1;NumPy CPU
regression is distinct from nativeC++/GMP CART. OriginalN96expanded median
4.761149127s→3.257604178s with the qualified readout;one-time expanded search
~6seconds is separate. Both boundary campaigns complete540advances+234restarts;
retained20/26bestchoices,batched26/26 (24restart/2reuse). Both calibrations
retained;backend changes method preference.

[Additive installation](../../GEN4/frustrated_spin_focused_install1/RESULT.md)
now supplies97entries(N1..96 plusN120),106transitions,11spin native learnedheads,
38cached source plans,7GEN3_SPIN operations and1689totalmath objects. Native
FOCUSED/COST APIs retain explicit hardware/backend scope;N120single timing is
reported as observed,not an extrapolated fit. The real96→120transition preserves
72added/12removed edges and24touched old boundary vertices. CachedN120plan
uses RETAINED_EXACT_PLAN_FOR_IDENTICAL_SOURCE;generic planning gets the fifth
prime capacity. BothGEN3/4pass49adoption/recovery checks;519/409bindings verify.
Current generations/native binaries and prior objects/models remain;Chalkboard
OFF and unrelated paused scopes unchanged.

All calculation workers stopped. Owner was explicitly told pod is safe to stop
after local verification. N120archive723534861bytes,sha
6c969f4a35b50a016b55fefd7cff2f1b4e3b9f78f2a4b33700a282bb66ce49d0.
BothGPU training archives,bothCPU boundary archives,full predecessor runtime,
exact sources,active code,qualifications and final installation/evidence are
saved locally.13manifest-covered restart/installation files verify in addition
to the completed campaign archives. Final installationevidence
6336529e643d1ed72fc1a8e8ec5c690f495a762e849630016045e2ac1380f36e;
portable installer4501f2f51fe88a5b3900e7cdf83aa73e6d2806147de959b662c335d4f5c2583b.
[Restart](../../GEN4/frustrated_spin_focused_training1/RESTART.md). Pod lifecycle
was not changed by the assistant.

**The test result suggests strong contact with the concept.**

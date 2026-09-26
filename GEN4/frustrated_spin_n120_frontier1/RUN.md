# N120 frustrated-spin frontier

Status: COMPLETE, exact in773.240389397seconds; installed GEN3/GEN4.
All results and restart files are verified locally; pod is safe to stop.
See [final result](RESULT.md). The following is the retained execution design.

Owner directive: take a crack at N120 tonight. Agent construction extends the current N96 five-regular graph to120vertices/300couplings, preserving228oldcouplings/all96fields and replacing12disjoint edges with24crosslinks to a fresh four-regular24vertex block. Source frozen before plan or energy calculations. Source is connected and has frustrated signed cycles. This is a new graph, distinct from the previously solved structured N120 ring.

CPU searches cutsets/elimination orders;14Blackwell MIG workers will share exact modular work in16branch groups, with CPU double-buffer preparation and fast exact inverseNTT/CRT. Five primes, including1224736769/root3, have sufficient capacity for2^120. RAM holds intermediates; compact residue/coverage checkpoints flush about every30seconds, full evidence at completion. Source-bound MATTER_SEARCH operations on SLC-GEN4-P1/SLC-GEN4-CE-P1/GEN3-R4.

Training remains authorized and runs first. N120 starts automatically after the faster300solve campaign releases the GPUs. Agent cutoff04:15UTC Sep25 retains about23minutes before the owner's approximate two-hour pod limit. Unfinished N120 work saves complete-task coverage for continuation.

Source SHA256: `bed8dbc542412f88a76795573e157e369710a0bcf8d2b7358e10a159d98df1f4`.
Pod code/log:/opt/gen4/spin-n120-frontier1;RAM:/dev/shm/gen4-spin-n120-frontier1;durable:/workspace/gen4/runs/spin-n120-frontier1.

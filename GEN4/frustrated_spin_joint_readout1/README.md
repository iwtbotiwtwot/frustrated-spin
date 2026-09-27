# Retained joint energy–magnetization–boundary readout

Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are AI research collaborators.

Owner request: complete the fully connected sources through N1408, then develop the joint readout. Graph construction is in the separate dense_extension1 project. This project adds an explicit lossless g(E,M,b) to the qualified dense magnetization solver, without changing historical campaigns.

Each fixed ordered-boundary state has a compressed JSON-lines shard. Every row is `[energy, magnetization, configuration_count_decimal_string]`. Counts are arbitrary-precision integers. The manifest binds source/graph identity, plan, ordered ports, spin conventions, shard hashes and verification. Boundary bit i is spin +1 when set and -1 otherwise. The energy includes all original fields and complete-graph couplings. No partial-boundary averages replace these rows.

The existing GPU/CPU local checks and independent global polynomial encodings remain. Exported rows are read back independently: summing over M reconstructs every original boundary DOS; summing over E reconstructs the exact conditional binomial distribution; their canonical correction-energy digest equals both independent solver digests. N12 qualification additionally compares complete joint tables with direct dense Gray-code enumeration. All existing full/conditional density, count and moment checks remain.

`readout.py` supplies the native `GEN4_JOINT_FIELD_BOUNDARY_READOUT` operation in this project. An exact rational uniform field h gives E_h=E-hM, retaining the original couplings and fields. Queries accept partial boundaries, return exact ground energies, degeneracies, magnetization counts, first/second energy sums and exact finite-system crossing fields. This performs table readout, not a new spin solve. Counts are exact; no temperature evaluation or nuclear-unit assignment is introduced.

    python readout.py joint/production_packet_N000120_+1/MANIFEST.json --field 1/2 --boundary '[1,null,null,null]' --output response.json

The boundary list must match the manifest's ordered-port length. `check_readout.py` tests 36 field/boundary queries against direct enumeration of six dense N12 sources, checks every returned ground-state crossing and rejects a corrupted shard. Qualification also covers N18 and the inherited nonzero-field/wrong controls.

Production uses a fresh additive pod project `/opt/gen4-spin-joint-readout1/project`, after the prior magnetization3 controller stops at its requested case boundary. One GPU owner and one CPU experiment; 8 GiB RSS and 15 minutes per case; 200 GiB free container disk; 2-hour window; maximum N1050 and polynomial degree 6.5 million. Start with all six N120 and N300 readouts, then N750, N900 and N1050. Existing answers are comparison targets when available; fresh full joint data require recomposition because the predecessor retained only the joint hash. Bulk data remain on container storage; compact metadata are mirrored under `/workspace/gen4/runs/frustrated-spin-joint-readout1`.

Safe stop: `touch /opt/gen4-spin-joint-readout1/project/STOP`. Current admitted work finishes before the next case is declined. No hardware change, L-series work or global selector change is part of this project.

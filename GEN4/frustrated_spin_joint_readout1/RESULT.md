# Joint readout implemented and qualified

Sean Brady is originator and conceptual director; OpenAI ChatGPT and Codex are AI research collaborators.

The complete signed graph catalog now reaches N1408: 8,448 graph sources, including 348 newly generated variants. [Graph custody and range locations](../frustrated_spin_dense_extension1/README.md) distinguish graph construction from exact dense solution coverage.

This project now retains exact **g(E,M,b)**, where b specifies the ordered retained boundary spins. Each boundary has a compressed table of energy, total magnetization and arbitrary-precision state counts. Full scalar and conditional spectra are recoverable by summation. The original independent CPU/GPU local calculation, dual global encodings, moments and density closure remain in force. Reading the saved joint tables reproduces their exact solver digest, original DOS and conditional binomial magnetization distributions.

Qualification passes on all 12 N12/N18 dense cases, including the nonzero-field and inherited wrong controls. Direct N12 full-joint enumeration agrees. The native readout passes **36 exact rational-field/partial-boundary queries**, checked against all 4,096 direct configurations of each of six N12 sources. Every returned ground-state crossing matches direct enumeration. Corrupted shard data are rejected.

The readout provides:

- Exact uniform-field response E_h=E-hM for rational h, with original couplings fixed.
- Conditional ground energy, total degeneracy and magnetization-resolved ground counts.
- Exact configuration count and first/second energy sums.
- Exact finite-system crossing fields, including all coexisting magnetization sectors.
- Reusable full joint tables for further observables; no fresh spin enumeration for these queries.

All six N120 and all six N300 production tables have completed and passed readback. The N120 portable archive is **11,815,582 bytes**, SHA-256 `595dbad013a160d96641d61ee8f84d1f912e85ad08c1e03a046d8d431d9450b7`. Local examples retain all six N120 tables, original receipts and two native field/boundary readouts; the archive is also hash-verified on T500. The archive size includes receipts and manifests, not just table payloads. N300 tables remain on the pod. At handoff, the N750 packet positive-fill table has also completed, and the negative-fill case is running.

In the dense N120 signed-packet-chain, fill -1 source, field **h=1/2** and boundary **[+1, free, -1, free]** give ground energy **-639**, ground magnetization **2**, and degeneracy **15**, among exactly **2^118** allowed configurations. This result is a table query with source-defined dimensionless couplings; no new spin solve was executed. The ordered vertex labels are in that table's manifest.

Native operation: `GEN4_JOINT_FIELD_BOUNDARY_READOUT`, supplied by the project adapter in `readout.py`. It executes through MATTER_SEARCH on isolated SLC-GEN4-P1 / CE SLC-GEN4-CE-P1. The global selector is unchanged. For a local query, set `GEN4_DENSE_RUNTIME` to the absolute `../frustrated_spin_workstation1/runtime` path and use the repository `.venv-r3/bin/python`:

    python readout.py examples/joint/production_signed_packet_chain_N000120_-1/MANIFEST.json --field 1/2 --boundary '[1,null,-1,null]' --output response.json

Production controller **61857** runs independently on the existing pod, starting 2026-09-27 00:02:01 UTC and bounded by deadline **02:02:01 UTC**. After N120 it processes N300, then N750/N900/N1050 while resource and exactness gates admit them. The previous magnetization controller stopped at an exact case boundary. No extra GPU hardware was provisioned and L-series work remains paused.

Monitor `/opt/gen4-spin-joint-readout1/project/STATUS.json`. Safe stop:

    touch /opt/gen4-spin-joint-readout1/project/STOP

The current admitted case finishes before new admission stops. Complete larger-N joint coverage is determined by that status and the per-case receipts, not by the graph-catalog upper N.

The test result suggests strong contact with the concept for the executed exact joint readout and response interface.

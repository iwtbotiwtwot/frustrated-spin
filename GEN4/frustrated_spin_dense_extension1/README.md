# Complete signed graph catalog through N1408

Sean Brady is originator and conceptual director; OpenAI ChatGPT and Codex are AI research collaborators.

The owner requested fully constructed graphs through N1408. The existing catalog contains six variants for every N1..1350. This additive extension supplies six variants for every N1351..1408: packet, signed packet and signed packet chain, each completed with uniform +1 and -1 couplings on previously absent pairs.

All **348 new graphs** passed generation and independent readback checks, producing a combined **8,448-graph** catalog. Each N1408 graph contains **990,528 explicit unordered-pair coupling bits**. Every original parent coupling, field, vertex label and ordered port is preserved. New-N parent source and exact-result hashes are checked against the workstation's exact append-only catalog. These are graph sources; this extension does not claim new dense DOS/magnetization solves.

Native generation took 11.964 seconds. The project retains per-N completions, source provenance, append-only index, native sessions and a full 928-file graph manifest.

Locations:

| Range | Workstation / T500 | Pod |
|---|---|---|
| N1..1350 | `/home/sam/mnt/lilhelper-t500/SAM_POD_BACKUPS/frustrated-spin-20260926/restored/follower/graphs` | `/opt/gen4-spin-dense-follower1/project/graphs` |
| N1351..1408 | This project's `graphs/`; mirrored at T500 `.../extensions/N1351_1408/graphs` | `/opt/gen4-spin-dense-extension1/project/graphs` |

T500 readback verifies all 928 files against their local hashes; see `T500_VERIFICATION.json`. Historical catalog files and producer answers are unchanged. `CATALOG_LOCATIONS.json` records the combined ranges. A new native joint-readout successor is under `../frustrated_spin_joint_readout1/`.

The same `dense_format.py` reader expands a bit-packed source into explicit edge JSON when needed. Bit packing is lossless storage of every pair coupling, not a rule omitting the new edges.

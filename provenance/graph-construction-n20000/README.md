# Fully constructed graphs through N20000

Graph construction is complete at **every integer N from1 through20,000**,
with six source/fill variants at each size: **120,000 graph sources**.
The variants are packet, signed_packet and signed_packet_chain, each completed
with +1 or -1 couplings on previously absent pairs. Existing source couplings
and fields are preserved.

Each N20000 graph explicitly encodes **199,990,000 pair interactions**:
N(N-1)/2. Coupling signs use a packed bit representation (24,998,750 raw bytes
per graph before gzip compression). The endpoint receipt lists all six graph
hashes and stored sizes: [N20000_COMPLETE.json](N20000_COMPLETE.json).

The N2001–20000 extension constructed108,000graphs across18,000sizes and retained
35,109,722,649bytes of graph/parent/receipt files after size/SHA-256 verification.
Combined with the completed N1–2000 predecessor, coverage has no gaps. The
recomputed N3000/N4000/N5000 anchors are overlaps, not additional unique sources.
These counts describe labeled source/fill variants, not graph isomorphism classes.

[Completion status](STATUS.json) and [original construction report](ORIGINAL_RESULT.md)
retain the research provenance. The original report's operational hold/pod notes
are historical; current joint-density results are linked below. This publication
includes compact endpoint evidence; the full construction archive remains in
research custody and is separate from the public N1–1800 compact-density release.

| Coverage | Completed range |
|---|---|
| Fully constructed complete signed graphs | Every N1–20000; six variants per N |
| Exact g(E,M,b), continuous | [Every N1–1800](../../reproduce/continuous-n1800/README.md) |
| Exact g(E,M,b), larger isolated milestones | N2000, N3000, N4000 and [N5000](../../reproduce/n5000/README.md) |

Construction and exact joint-density computation are separate completed tasks.
The N20000 graph campaign generated and verified sources; it did not calculate
N20000 joint densities.

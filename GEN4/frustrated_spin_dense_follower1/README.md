# Dense graph follower1

Sean Brady is originator and conceptual director. OpenAI ChatGPT and Codex are AI research collaborators.

This additive, CPU-only follower backfills the completed packet catalog N1–120, then follows every fully completed N of the active packet continuation. For each N, three verified parent families each produce +1 and -1 completions. Every parent interaction, field, vertex label, and ordered port is retained. Every previously missing pair is assigned the explicit fill coupling.

These are complete graph SOURCE definitions, with N(N-1)/2 nonzero couplings each. The follower does not compute a dense density of states. The ongoing exact packet solver is not modified or restarted.

## Complete coupling storage

Each graph stores one explicit sign bit for EVERY unordered vertex pair, ordered lexicographically by (u,v), u<v. Bit order within bytes is least-significant first; 1 means J=+1, 0 means J=-1. Unused end padding is zero. The resulting byte sequence is gzip-compressed and accompanied by a JSON manifest, SHA-256 hashes, a compressed exact parent record, and its verification provenance. This is a complete dense coupling array, not a missing-edge reconstruction rule. Some construction variants coincide at the smallest N; source identities remain explicit.

The reader expands it into an ordinary explicit-edge graph JSON:

    python dense_format.py graphs/N000300/packet_N000300_fill_plus.json expanded_N300.json.gz

This produces a graph source, not a density-of-states answer. Fields and original parent vertex labels are preserved.

Generation uses direct bit offsets. Readback independently checks gzip integrity, uncompressed content hash, dimensions, padding, each original coupling, and total positive/negative counts. Since all absent pairs have the same declared fill sign, the preserved-parent checks and the exact extremal sign count together verify every newly added pair. Qualification additionally decodes every pair sequentially at N1,2,12,120,121,300 and compares all six N300 coupling arrays with the previously generated explicit 44,850-edge source files. Three wrong controls test changed inherited coupling, changed new coupling, and invalid padding.

## Running and recovery

Pod project: /opt/gen4-spin-dense-follower1/project

Producer: /opt/gen4-spin-continuation1/project

Compact mirror: /workspace/gen4/runs/frustrated-spin-dense-follower1

The follower admits only N at or below the producer's last fully completed and verified N. New-N parent source hashes and compressed exact-result hashes are checked against the producer's append-only catalog. The N1–120 seed records are recovered from the completed retained catalog. PRECOMMIT events bind the producer checkpoint and code identity before generation.

Two low-priority CPU workers are used when the existing GEN4 resource manager confirms spare CPU allocation beyond the producer. Each worker has an allocation-derived memory cap no larger than 4 GiB and a 180-second task limit. The producer retains priority. No GPUs are used. Preserve at least 200 GiB free container disk. Full graphs and native receipts stay on container storage; the network volume receives compact status and catalog metadata.

N completion records and append-only indexing support restart without regenerating completed graphs. Atomic files and hashes retain partial progress. SIGTERM or a STOP file stops new admission and finishes the current bounded tasks. The follower exits once the producer finishes and all its completed Ns are covered. A hard deadline five minutes after the producer's recorded deadline bounds final catch-up; any remaining backlog remains resumable. The pod is not stopped automatically.

Monitor:

    cat /opt/gen4-spin-dense-follower1/project/STATUS.json
    tail -f /opt/gen4-spin-dense-follower1/project/RUN.log

Stop only this follower:

    touch /opt/gen4-spin-dense-follower1/project/STOP

The compact mirror is not a complete graph-data backup. Export container results before stopping or deleting the pod.

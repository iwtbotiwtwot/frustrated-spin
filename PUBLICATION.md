# Publication record and reproduction

Publication requested by Sean Brady on September 26, 2026, as a new addition
to `SAMresearchproject/SLC-GEN3-R3`. Source material comes from the retained
`SAM_Research_Project/GEN4/` frustrated-spin projects and the final paused
cooperative-14 pod campaign. The original working-research records are unchanged.

## Export boundary

The addition includes research source code, canonical sources and exact answers,
plans, reports, precommits, controls, timings, ledgers, models, certificates,
native execution records, and installation/qualification evidence. The original
N300 precommit archive and all 20 files in its frozen manifest are byte-preserved.

Runtime authentication keys are private and are excluded. Generated Python/CUDA
caches, solver working pickles, lock files, and bulk per-kernel trace CSVs are
excluded. Aggregate timing, telemetry, and exact research outputs are retained.
Original bundles that duplicate expanded campaign files remain in owner storage;
their hashes and public evidence locations are recorded in
[EXPORT_DISPOSITIONS.json](provenance/EXPORT_DISPOSITIONS.json).

Other retained tar bundles are recursively sanitized and published with the
suffix `.public.tar.gz` appended to their original filename. This includes the
N120 completion and gap-completion bundles. Sanitized archive hashes differ
from their private originals; the disposition record binds both hashes and
lists omitted members. Nested bundles are sanitized too. Historical manifests
and reports still describe their original records and are not rewritten.

The public [PUBLIC_MANIFEST.json](provenance/PUBLIC_MANIFEST.json) identifies the
exact files delivered here. It is the transport manifest for this addition;
the old campaign manifests remain scientific provenance for their own snapshots.
Original absolute paths and pod process identifiers in historical records are
retained as provenance, not current commands for a reader's machine.

The pod snapshot was retrieved read-only after its status was STOPPED. No
training was resumed, no new mathematical test was run, and no remote hardware
was changed during publication. The source workstation's earlier pod snapshot
is also retained separately, so publication does not erase its chronology.

## Reading exact outputs

Canonical source/result objects are ordinary JSON under
`GEN4/frustrated_spin_learning1/canonical/`. Packet source objects are under
`GEN4/frustrated_spin_packet_catalog1/sources/`; gzip-compressed exact results
are under its `results/` directory. The N300 full answers, independently
computed references, open operators, and wrong-control artifacts are under
`GEN4/frustrated_spin_n300_courtroom1/artifacts/`.

`python3 verify_publication.py` uses only the Python standard library and
checks the published files without changing them. This is a retained-record
verification, with no new timing samples or primality/RH work.

## Solver and runtime reproduction

The campaign source scripts retain their original executable definitions and
paths. The packet solver uses `python-flint` and vendored `spin_exact.py`.
Native session execution additionally uses the archived GEN4 runtime and its
recorded dependency versions. GPU campaign reproduction requires the specific
qualified CUDA, package, plan and cooperative-14 topology in
`GEN4/frustrated_spin_pod14_learning1/POD_QUALIFICATION.json`.

One shared, sanitized runtime snapshot is supplied as a
[release asset](https://github.com/SAMresearchproject/SLC-GEN3-R3/releases/download/frustrated-spin-2026-09-26/RUNTIME.public.tar.gz).
Its SHA-256 is recorded in
[RELEASE_ASSETS.json](provenance/RELEASE_ASSETS.json).
Download it to `GEN4/frustrated_spin_learning1/RUNTIME.public.tar.gz` and check
that checksum before restoring it in a separate working copy:

```sh
tar -xzf GEN4/frustrated_spin_learning1/RUNTIME.public.tar.gz \
    -C GEN4/frustrated_spin_learning1
ln -s ../frustrated_spin_learning1/runtime GEN4/frustrated_spin_packet_catalog1/runtime
ln -s ../frustrated_spin_learning1/runtime GEN4/frustrated_spin_n300_courtroom1/runtime
```

New native executions must create fresh session directories and new custody
keys. Private original session roots cannot be resumed using this public
export. The original N300 run refuses to overwrite its completed event ledger;
any subsequent execution is a separate experiment, not a replacement for the
sealed prospective result. Machine allocation and shell launch files describe
their recorded environments and require deliberate adaptation on another host.

## Continuation and dense-completion supplement

The September 26 supplement adds `frustrated_spin_packet_continuation1` and
`frustrated_spin_dense_completion1`. Its separate
[sync receipt](provenance/SYNC_CONTINUATION_DENSE_20260926.json) records the
scope and export exclusions. The running continuation was not paused for this
publication; `pod_launch/` retains its launch-time snapshot and first new
source outputs. It does not contain all subsequent pod results.

The dense-completion project includes all six N300 graph definitions,
generation code, input identities, precommits, native receipts, and identity
checks. Its `SOURCE_GENERATED_NOT_DOS_SOLVED` status is preserved.

The continuation controller's isolated runtime link can be recreated after
restoring the shared runtime archive:

```sh
ln -s ../frustrated_spin_learning1/runtime GEN4/frustrated_spin_packet_continuation1/runtime
```

Do not treat retained launch commands or process IDs as commands for another
machine. Reproduction uses a fresh output directory and explicit resource
configuration; the source records in this publication remain unchanged.

Existing repository license, notice, and stewardship terms apply. Originating
third-party notices retained in runtime and source bundles remain applicable.

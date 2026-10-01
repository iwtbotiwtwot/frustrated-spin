# Current completion and byte-accounting clarification — October 1, 2026

N3000, N4000 and N5000 are completed exact joint-spectrum calculations, superseding
the partial/checkpoint and graph-only states in the earlier N2000-era report.
Their two-encoding logical raw output totals **3.055 TiB**, representing completed
output. Their lossless compressed archives total **1.053 TiB**. The logical total
includes encoding/boundary duplication and is not unique disk usage or download size.
[Exact byte table and sources](README.md#completed-spectra-and-storage-accounting).
The continuous campaign's hypothetical expanded-output byte figures are storage
projections; its separately public compact release is 8.34 GB.

# Continuous N1–1800 publication — October 1, 2026

The [continuous package](reproduce/continuous-n1800/README.md) adds original
compact scientific records for every N1–1800, 10,800 case summaries, explicit
methodology and equations, batch results, source/build bindings and independently
checked release assets. Expanded full tables are separate milestone data.
[Literature context](reproduce/continuous-n1800/LITERATURE.md) identifies the
N1296 sampling comparison and the scope of exact joint-density claims.

# N2000–N5000 reproduction packages — September 29, 2026

The [N5000 reproduction package](reproduce/n5000/README.md) and [N4000 reproduction package](reproduce/n4000/README.md) each preserve 192 completed rows, 96 matching encoding pairs, frozen inputs, exact CPU recomputation, and verified lossless shard inventories. Their packet/+1 CPU reproductions match all 32 rows in 37.769 and 16.473 seconds, respectively. N5000 has six transfer batches and N4000 has three, each capped at 100 GiB.

The [N3000 package](reproduce/n3000/README.md) adds all six completed exact joint cases, 192 GPU production receipts, frozen sources and tested CPU recomputation. All 32 packet/+1 replay rows match production canonical and raw-record hashes in 10.486 seconds. The 422.457 GB raw dataset is losslessly compressed into 236.964 GB of independently verified shards, grouped into three batches capped at 100 GiB. All three workstation downloads are complete; batches 001 and 002 have been uploaded to Drive, and batch 003 is ready for upload. Original production records and GPU source hashes are preserved; private session keys are excluded.

# Open licensing supplement — September 27, 2026

Owner-authorized scoped spin release: MIT software and CC BY 4.0 data, reports and figures. [LICENSING.md](LICENSING.md) explicitly covers the public dataset, manuscript foundation and identical materials in earlier spin releases. [RUNTIME_LICENSE.md](RUNTIME_LICENSE.md) identifies frozen runtime copies and grants additional open permissions without changing archive/scientific bytes. Third-party rights remain separate. The inherited research-only records below and in historical archives describe prior terms; current recipients may elect the new grant. Preferred citation: [CITATION.cff](CITATION.cff), DOI https://doi.org/10.5281/zenodo.22989862.

# N2000 reproducibility supplement — September 27, 2026

The [portable N2000 package](reproduce/n2000/README.md) adds the completed six-case exact g(E,M,b) result, all 16 boundary states per case, both independent encodings' scientific receipts, frozen complete-graph sources, original code, and a separate portable native runner. Full primary data are 63.223 GB uncompressed or 37.398 GB losslessly compressed. The [Google Drive folder](https://drive.google.com/drive/folders/1F8wvIRqL3pdB34db-llz0YjnIbFbRg9Y) hosts the public data; DATA_MANIFEST.json records confirmed availability and per-file SHA256. Bulk data are kept out of Git history.

Public-runtime qualification uses fresh sessions and pinned numpy 2.1.2 / python-flint 0.8.0. It reproduces all 32 files of the complete N2000 packet/+1 case byte-for-byte and checks N12/N30 independently. The other five large cases retain their original completed receipts; this publication did not rerun the full expensive campaign. The old runtime export omitted its 143,710-byte sealed foundation source ZIP; the exact original, already bound by the runtime's hash, is supplied in runtime_supplement. No runtime validation is bypassed.

Private original sessions and custody keys are excluded. The original scientific receipts and older records retain their original bytes. The new publication manifests describe only the additive public files. That earlier N3000 stopped-checkpoint boundary is superseded by the completed September 29 result above. Existing licensing, attribution and stewardship apply.

# Standalone repository copy

The published frustrated-spin directory was copied from SLC-GEN3-R3 commit
74dbef016c96a58593fed362713c111a55f85071 into iwtbotiwtwot/frustrated-spin.
Its three directory-specific commits are preserved, with source/extracted IDs
in [STANDALONE_COPY.json](provenance/STANDALONE_COPY.json). Scientific evidence
and the N300 frozen record retain their original bytes. The entry-point
README and current runtime download descriptors now refer to this repository.
Both runtime assets are copied byte-for-byte from the parent publication.
The inherited parent legal documents are preserved in `legal/historical/2026-09-07/`; the open licensing supplement above governs the current scoped spin grant.

The bulk-data boundary is unchanged: verified local/T500 custody and published
manifests, rather than all raw multi-gigabyte production data on GitHub.
The original publication record follows.

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
[release asset](https://github.com/iwtbotiwtwot/frustrated-spin/releases/download/frustrated-spin-2026-09-26/RUNTIME.public.tar.gz).
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

## Joint capability and response supplement

The latest sync adds the completed N1408 workstation extension, dense-source
extension, magnetization/joint methods, installed shared capability and two
bounded Volume II response experiments. It preserves existing scientific source
records and the original N300 precommit. See
[SYNC_JOINT_20260926.json](provenance/SYNC_JOINT_20260926.json) for every new
export exclusion and large-file identity.

Complete N1408 packet answers and compact source-bound production receipts are
included. Bulk joint shards, older full packet outputs, private session state,
and duplicate staging runtimes remain in verified owner custody. Publication of
their manifests records availability and provenance; it does not place those
bulk bytes on GitHub. Local custody paths in historical records require the
corresponding archive; large streamed queries cannot run from metadata alone.

The upgraded scoped runtime is available through
[RELEASE_JOINT_20260926.json](provenance/RELEASE_JOINT_20260926.json). Check its
SHA-256 before extracting into a fresh working directory. Its original package
manifests describe the private snapshot; public export omits authentication
keys and execution caches. Initialize new sessions and keys for new executions.
The parent repository's portable R3 runtime is not duplicated in this copy.

To reproduce the new small phase experiments in a compatible isolated runtime,
place the selected run.py/analyze.py in a fresh GEN4 project directory there,
and copy PHASE_ADOPTION_INPUTS.json into GEN4/spin_joint_install1/. Follow its
REPRODUCE.md using that runtime's Python and resource configuration. Keep all
published execution directories immutable. The known source-data dependencies
are included, and these small experiments do not require the large joint shards.

Run `python3 verify_publication.py` for published-byte and retained N300 checks,
and `python3 verify_latest.py` for the retained new response results. Neither
command performs a fresh production solve or timing trial. The latest transport
manifest includes both original and new Git files; historical campaign hashes
retain their original scope and may include deliberately unexported private or
bulk files.

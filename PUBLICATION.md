# Publication, data access and reproduction — current guide

Current coverage is recorded in [CURRENT_STATUS.md](CURRENT_STATUS.md) and
[CURRENT_STATUS.json](CURRENT_STATUS.json): graphs at every N1–20000, exact joint
densities at every N1–1800, and isolated exact milestones N2000–N5000.

**Due to their size, large expanded datasets are held on Google Drive rather
than in this Git repository.** See the [data-folder links](README.md#exact-milestone-packages).
The compact N1–1800 dataset is a separate GitHub release; source code, reports,
checksums and selected examples remain in Git.

## Current packages

- [Continuous N1–1800](reproduce/continuous-n1800/README.md): original compact
  records at all 1800 sizes, six cases each;18 range archives and bound solver/source
  archive; public 8.34 GBrelease with verified SHA-256. Expanded full tables are
  separate selected-milestone data.
- [N2000](reproduce/n2000/README.md), [N3000](reproduce/n3000/README.md),
  [N4000](reproduce/n4000/README.md), [N5000](reproduce/n5000/README.md): completed
  exact joint spectra,192 encoding rows per size, frozen sources and tested
  packet/+1 CPU replay. N2000 supplies the common public-runtime installation.
- [Graph construction](provenance/graph-construction-n20000/README.md):120,000
  labeled sources through N20000; compact endpoint evidence in Git; full corpus
  remains separate in research custody.

[Current data-access table](CURRENT_STATUS.md#storage-and-access) records public
links and the scope of custody checks. Completion, physical custody and anonymous
access are separate fields. An older pending/hold field preserved in provenance
is not a current instruction to withhold completed data.

## Completed versus hypothetical storage

N3000–N5000 completed logical raw output across both encodings totals 3.055 TiB;
archived raw shards total 1.823 TiB and compressed archives total 1.053 TiB.
These are completed-output/archive counts. The continuous campaign's 42.031 TB
hypothetical headerless expanded output is a storage projection, not retained
or published data. [Exact byte accounting](provenance/SPECTRA_STORAGE_ACCOUNTING.json).

## Verification and actual recomputation

Each package's `verify-record` (or continuous `verify.py`) checks retained results
without new production. The individual milestone README explains actual native
CPU smoke recomputation, fresh output directories, dependencies and memory/disk
requirements. Follow those instructions, rather than historical pod launch commands.
The tested public milestone runtime is a pinned reproduction environment; older
campaign runtime versions remain provenance for their original executions.

For historical evidence:

```sh
python3 verify_current.py
python3 verify_latest.py
```

`verify_current.py` verifies the preserved original document bytes and explicitly
listed current documentation/hosting overrides, then invokes the unchanged
`verify_publication.py` scientific checks: original public transport files, N300 frozen
precommit/witness/event chain and retained exact comparisons. `verify_latest.py`
is the inherited filename for the September 26 phase-response verifier; it does
not establish the latest catalog range. Newer package checks are linked above.
Original campaign files and the hashes that identify them remain unchanged.
Running the old verifier directly against updated documentation reports the old
document-hash mismatch; use the current wrapper for this checkout.

## Historical reports and superseded operational states

The [historical campaign index](GEN4/README.md) and additive CURRENT_CONTEXT.md
files map frozen campaign READMEs to current coverage. The original N2000-era
partial N3000 and graph-only N4000/N5000 states were superseded by completed
spectra. The earlier N1408 source extension was superseded by continuous graph
construction through N20000. Original runtime/process/custody instructions apply
to their dated campaign, not a new installation.

The preceding publication guide and README are preserved under
[the reconciliation record](provenance/status-review-20261001/REPORT.md).
Original transport lineage: [standalone extraction](provenance/STANDALONE_COPY.json),
[September 26 source export](provenance/SYNC_JOINT_20260926.json), and
[runtime asset](provenance/RELEASE_JOINT_20260926.json). Their dates and scopes
remain valid; they are not today's latest data inventories.

## Licensing and attribution

Project-owned software is MIT; research data, reports and figures are CC BY 4.0.
[LICENSING.md](LICENSING.md) and [RUNTIME_LICENSE.md](RUNTIME_LICENSE.md) govern
scope and frozen-runtime grants; third-party rights remain separate. Historical
research-only terms describe earlier distribution, as explained in those grants.
See [CITATION.cff](CITATION.cff) for citation and the concept DOI.
Sean Brady is originator/conceptual director; OpenAI ChatGPT and Codex are AI
research collaborators and co-authors. Private session credentials are excluded.

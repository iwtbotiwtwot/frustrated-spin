# Shared exact packet and joint spin capabilities

This extends the installed GEN3_SPIN operations used by SLC, CE, GEN3/GEN4,
ATOM3D/A3D41, Starbreaker and MATTER_SEARCH. No separate domain solver is selected.
Existing payloads retain their behavior. Sean Brady is originator and conceptual
director; OpenAI ChatGPT and Codex are research collaborators.

`GEN3_SPIN_SOURCES {}` now reports the full canonical N1..120 registry (123 source
records) and separately typed packet/complete-graph extensions through N1408.
N-only defaults preserve the packet N100/N105 and frustrated-source N120.
The connected-prefix N100/N105 require their family/hash selector.

`GEN3_SPIN_SOURCE {"source_recipe":{"family":"signed_packet_chain","N":300}}`
reconstructs the exact completed packet source and its certified edge partition.
It returns the source, ordered ports and decomposition. It does not return a
newly executed result. Families are packet, signed_packet, signed_packet_chain.

`GEN3_SPIN_SOLVE {"source_recipe":{"family":"packet","N":300}}` executes
exact packet polynomial compilation in the shared CPU backend. Identical local
operators are reused within the warm consumer. A chain shortcut is admitted only
when its complete conditional energy polynomials are equal; otherwise full
signed two-state messages remain. Scalar equality is not applied to joint data.

Add `"joint":true` to retain g(E,M,b). Add `"dense_fill":-1` (or any integer)
to preserve parent interactions and fill every absent pair with that coupling.
The solver uses E=Ecorr-J0*(M^2-N)/2, local exact operators, repeated component
powers, balanced products and signed boundary messages. Full scalar DOS and all
ordered port rows remain in the ordinary answer. Joint rows are compressed native
mathematical objects in the same Store and checkpoint dependency closure.

Explicit graphs use the existing `source`/`ports` fields. Optional `decomposition`
is {"blocks":[...],"bridges":[[u,v,J],...]}; every vertex/interaction must be
accounted for, retained ports must belong to the first block, and bridges follow
the declared single-gateway chain. Generic integer graphs without an admitted
component decomposition use joint polynomial variable elimination. The method
is chosen from source structure, never from N alone. `GEN3_SPIN_SELECT` with the
same payload returns the bound plan/estimates without solving.

Backend `cpu` is the default; `gpu` uses CUDA integer local enumeration followed
by FLINT composition and independent CPU checks. GPU joint VE is not implemented.
Existing modular GPU DOS and focused production methods remain available through
the original payload. Auto keeps small local operators on CPU. Default joint
admission: 2M unique local assignments, 6.5M polynomial degree, 2GiB estimated
polynomial workspace, 4M output records and120seconds. These are adjustable
`options`, not a promise that arbitrary dense graphs have a packet decomposition.
Use the existing SLC/GEN4 resource launcher for substantial workloads.

Read a retained dataset:

```json
{"joint_key":"signed_packet_chain_N120_fill_-1"}
```

Pass this to `GEN3_SPIN_SOURCE`; use its result_ref in `GEN3_SPIN_READOUT`:

```json
{"result_ref":"<returned SHA256>","uniform_field":"1/2",
 "boundary":[1,null,-1,null],"collective_coupling":"0",
 "boundary_fields":["0","0","0","0"],"include_spectrum":false}
```

The exact transformation is E'=E-hM-g*(M^2-N)/2-sum(b_i*s_port_i).
Thus one table supports changing the uniform field, adding uniform pair coupling,
changing retained-port fields and closing any subset of ordered boundaries.
Optional integer `magnetization` conditions M. Returned values include exact
counts, ground energies/degeneracies, all coexisting magnetizations at exact
rational crossing fields, E/M/mixed moments, variance and covariance. Set
include_spectrum=true for the complete transformed energy DOS. No spin
re-enumeration occurs. Integer/rational inputs only; counts never use floating
point. M denotes sum of binary source coordinates; physical units come from the
calling source map.

`GEN3_RESULT_APPLY {"operation":"GEN3_SPIN_READOUT","payload":{...}}`
adds exact request/implementation-keyed reuse. Repeating the same request,
including after checkpoint recovery, returns arithmetic_calls=0. A changed field,
ordered boundary or implementation does not reuse the old response.
`GEN3_RESULT_EXPORT`/`IMPORT` carries the complete chunk dependency closure.
No absolute pod data path is required for installed datasets or exported results.

Use existing `./spin-tools call OPERATION PAYLOAD` or DomainSession.execute.
All historical operations, learned cost scopes and canonical answers remain.
The N1408 complete-graph source catalog is distinct from dense DOS coverage;
only explicitly imported or executed joint results are labeled solved.

Large completed joint datasets are indexed under `external_joint_results`.
On a host holding those files, `GEN3_SPIN_SOURCE {"joint_key":"packet_N900_fill_+1"}`
retains a manifest/source-bound native reference; READOUT streams each selected
shard after hash verification. It checks row counts and conditional count closure.
The installed catalog pins manifests and all shard hashes; it does not trust an
unbound path or the filename's N. On hosts without the archive, selection reports
the required custody location. Small installed datasets are self-contained.

Native export explicitly reports `SELF_CONTAINED` versus
`REQUIRES_HASH_BOUND_EXTERNAL_DATA`, carrying external manifest/hash requirements.
Import and checkpoint recovery preserve this distinction. Reused calculated
responses remain available without rescanning bulk data. A fresh response from
an external table requires its retained shards. Active campaigns may finish more
datasets after this installation's pinned inventory snapshot.

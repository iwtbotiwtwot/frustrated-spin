# Extending the fast N100/N105 packet family across N1–120

**Originator and conceptual director: Sean Brady.**

Sean's research direction is to extend the graph structure responsible for the exceptionally cheap N100/N105 exact calculations across the catalog, and use that structure as a reusable computational capability. Codex supplied the explicit graph grammar, exact implementation, signed and connected comparison families, and execution documented here.

## The idea

N100 and N105 show that nominal spin count does not determine exact computational difficulty. Their sources decompose into repeated small packets. Instead of treating them as isolated fast examples, build a complete family at every N that preserves this useful structure, then introduce frustration and connections while keeping the boundary information small enough for exact calculation.

The resulting program is:

> explicit graph structure → reusable packet spectra → exact boundary messages → complete global spectrum.

A connected graph can remain cheap when its packets communicate through small exact interfaces. The computational opportunity is therefore broader than disconnected components alone.

## Completed result

Every integer **N=1,2,3,…,120** was executed in each of three separately identified families: **360 exact source cases**.

For every source, the **median of three warm packet-cache solves was below 10 milliseconds**. Each timed call rebuilt the complete global density and ordered retained-port spectra from local packet tables. It did not retrieve a previously computed complete answer.

| Family | Completed sizes | Largest three-run warm median |
|---|---|---:|
| Original packet extension | All N1–120 | 8.476 ms |
| Signed packet extension | All N1–120 | 7.239 ms |
| Connected signed packet extension | All N1–120 | 6.848 ms |

These are pod CPU measurements. The under-10-ms statement refers to each source's three-run warm median, not every individual repetition or a cold process launch. Empty-cache solves and independently executed full-graph variable elimination were measured separately. All 360 sources passed full exact coefficient comparison.

A further exact boundary-equality refinement was executed for all 120 connected-family sources. Its largest three-run median was **6.556 ms**. That refinement has its own measurements and certificate rather than replacing the original comparison records.

## Recovered source grammar

The original N100 graph is exactly the induced first 100 vertices of N105: all inherited fields and interactions match. Both original anchors have zero fields and positive unit couplings.

Each complete layer is a five-spin clique, K5. Consecutive layers within a packet are joined by five matching edges. A one-layer packet has 5 spins and 10 edges; two layers have 10 spins and 25 edges; three layers have 15 spins and 40 edges.

| Anchor or extension | Packet sizes | Edges |
|---|---|---:|
| N100 | 15,15,15,15,15,10,10,5 | 260 |
| N105 | 15,15,15,15,15,10,10,10 | 275 |
| N110 | 15,15,15,15,15,15,10,10 | 290 |
| N115 | 15,15,15,15,15,15,15,10 | 305 |
| N120 | 15,15,15,15,15,15,15,15 | 320 |

The extension adds a third five-spin layer to each remaining two-layer packet. It preserves the N100/N105 anchors exactly. Explicit induced prefixes supply every intermediate integer and every smaller N. Small prefixes can contain incomplete layers; their complete graphs are retained individually.

Original ordered port identities [0,1,60,61] are preserved. At sizes where a port vertex does not yet exist, only the existing members of that ordered list are requested.

## Signed and connected extensions

The signed family changes one edge per complete K5 layer to negative coupling. Complete layers then contain explicit negative-product triangles, recorded as frustration witnesses. Small prefixes without a completed witness remain explicitly identified by their actual witness count.

The connected signed family adds a chain of signed bridges between one gateway spin in each packet. At N120 it has 120 vertices, 327 interactions, one connected component, and 24 retained frustrated-triangle witnesses. Every coupling is included in its exact calculation.

These comparison families were designed for this experiment. They are separate source identities at each N. The existing canonical frustrated graphs and their answers have not been replaced, and N121–144 remains untouched.

## Exact computational method

For packet i, retain the full integer polynomial for every requested local port or gateway assignment:

\[
A_i(q\mid \sigma)=\sum_{s_i:\,s_{\partial i}=\sigma}
q^{(E_i(s_i)+B_i)/2},
\qquad B_i=\sum |J|+\sum |h|.
\]

Integer Ising energies have the required parity, so every exponent is an integer. Exact FLINT polynomial arithmetic preserves all configuration counts.

The compiler first checks the vertex partition and accounts for every edge. Local tables are keyed by their complete fields, couplings, and ordered ports. Repeated identical scalar packets are combined with polynomial powers; a balanced product combines the remaining factors. The campaign required only **102 distinct local tables** for its three full catalogs.

For a bridge of strength J between boundary spins s and t, the exact bridge factor is

\[
q^{(|J|-Jst)/2}.
\]

Summing over both values of t propagates a two-state boundary message. The complete global density is reconstructed from these messages, including every retained-port conditioning and every interaction.

For the measured zero-field packets, spin reversal pairs the two gateway-conditioned energy distributions. The refinement checks the full polynomial equality directly. When \(A_-=A_+=A\),

\[
\sum_{t=\pm1} A(q)q^{(|J|-Jst)/2}
=A(q)(1+q^{|J|}),
\]

independently of s. The connected chain then contracts through ordinary polynomial products. A nonzero-field control breaks that equality: the implementation rejects the shortcut and uses the complete two-state calculation. An undeclared extra cross-packet edge is rejected by the partition check.

## Verification and timing

Each of the 360 sources received three full-graph variable-elimination calculations, three packet calculations starting with an empty cache, and three packet calculations using the persistent local cache: **3,240 timed exact calculations**. The 120 boundary-refinement cases add **360 timed calculations**. The separate 18-source smoke regression is retained as qualification evidence.

Comparisons retain every scalar DOS coefficient, every ordered-port conditional row, exact configuration counts, first and second moments, and source/plan/output identities. The original N100/N105 outputs additionally match the retained canonical answers. Open operators use an explicitly recorded zero-glue convention.

Solve timings include global spectrum reconstruction and native count/moment checks. Structural planning, external equality verification, receipt writing, and file persistence are separately scoped. Warm local-table reuse is distinct from empty-cache work and complete-result lookup.

Selected warm results before boundary refinement:

| N | Original packet (ms) | Signed packet (ms) | Connected signed packet (ms) |
|---|---:|---:|---:|
| 100 | 4.678 | 4.897 | 5.055 |
| 105 | 5.040 | 5.264 | 5.563 |
| 110 | 5.853 | 5.581 | 5.915 |
| 115 | 5.920 | 6.123 | 6.430 |
| 120 | 6.222 | 6.393 | 6.848 |

## What this gives GEN4

The completed artifact is a source-bound exact computation tool and a controlled structural catalog. It separates spin count, packet structure, frustration, connectivity, cache reuse, and boundary information in executable examples.

The next useful extensions are two-spin packet interfaces, loops in the packet-connection graph, and fields that remove gateway symmetry. Those tests can determine how exact cost changes with retained boundary size. The same compiler principle can also be investigated on the existing canonical graphs by identifying their actual separators and preserving every interaction.

Training remains paused. This project does not restart its old queue or install a global selector.

**The test result suggests strong contact with the concept.**

## Evidence and use

- [Measured catalog](CATALOG.csv): all 360 source cases and route timings.
- [Execution report](REPORT.md): construction, exactness contract, and representative comparisons.
- [Graph grammar](GRAMMAR.json) and [source manifest](SOURCE_MANIFEST.json): anchors, extensions, and all explicit source identities.
- [Boundary certificate](BOUNDARY_CERTIFICATE.json) and [refinement timings](BRIDGE_REFINEMENT.csv).
- `sources/`, `results/`, `refinement/`, and native `sessions/`: explicit inputs, full spectra, precommits, controls, and calculation receipts.
- [Usage](README.md): retained lookup and fresh exact execution commands.

For the measured size dependence and stage breakdown, see [Runtime scaling](RUNTIME_SCALING.md).

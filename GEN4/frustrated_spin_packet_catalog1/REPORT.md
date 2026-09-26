# Packet-family extension across N1–120

Owner: Sean Brady, originator and conceptual director.

Status: COMPLETE. Training remains paused. All timings below were measured on the pod CPU in this campaign.

## Construction and computation

The N100 graph is exactly the induced first 100 vertices of N105. Both use zero fields and positive unit couplings. Their components are chains of K5 layers with perfect-matching interfaces. The N105 extension completes its three two-layer packets to three layers each, giving eight 15-spin packets at N120. The full N1–120 ladder is formed by explicit induced prefixes, preserving both anchors exactly.

Two additional agent-designed families retain the packet vertices and internal topology: one negative edge per complete five-spin clique creates explicit frustrated triangles; a connected version links the packets through one gateway spin per packet, with signed bridges. These are separately named new sources. Existing canonical connected graphs and answers are unchanged.

The compiler verifies every vertex and edge against its packet partition. It computes exact local port-conditioned polynomial spectra, caches them by full local source and ordered ports, and combines repeated scalar packets with polynomial powers and a balanced product. Connected cases use exact two-state boundary messages, summing both assignments at each bridge. No full-result lookup supplies a timed answer.

Every row compares three fresh full-graph variable-elimination solves, three solves with an empty packet cache, and three solves with a persistent packet cache. All scalar coefficients, ordered retained-port spectra, configuration counts and first/second moments agree. Open operators use the explicitly declared zero-glue convention. Timings include source-bound solve and native readout/checks; planning, external equality verification, native receipt and file writing are outside the timed solve.

## Anchor and extension measurements

| Family | N | Components | Fresh VE (ms) | Empty packet cache (ms) | Warm packet cache (ms) |
|---|---:|---:|---:|---:|---:|
| packet | 96 | 8 | 23.933 | 14.063 | 4.307 |
| packet | 100 | 8 | 25.570 | 12.555 | 4.678 |
| packet | 105 | 8 | 27.641 | 12.480 | 5.040 |
| packet | 110 | 8 | 29.808 | 13.103 | 5.853 |
| packet | 115 | 8 | 32.161 | 13.486 | 5.920 |
| packet | 120 | 8 | 34.269 | 12.453 | 6.222 |
| signed_packet | 96 | 8 | 23.784 | 14.258 | 4.427 |
| signed_packet | 100 | 8 | 26.454 | 12.941 | 4.897 |
| signed_packet | 105 | 8 | 28.397 | 12.709 | 5.264 |
| signed_packet | 110 | 8 | 30.552 | 13.185 | 5.581 |
| signed_packet | 115 | 8 | 32.812 | 13.681 | 6.123 |
| signed_packet | 120 | 8 | 35.079 | 12.620 | 6.393 |
| signed_packet_chain | 96 | 1 | 23.480 | 14.810 | 4.785 |
| signed_packet_chain | 100 | 1 | 25.796 | 13.283 | 5.055 |
| signed_packet_chain | 105 | 1 | 28.031 | 13.289 | 5.563 |
| signed_packet_chain | 110 | 1 | 30.051 | 13.692 | 5.915 |
| signed_packet_chain | 115 | 1 | 32.196 | 14.654 | 6.430 |
| signed_packet_chain | 120 | 1 | 34.417 | 12.944 | 6.848 |

## Coverage

{
  "packet": {
    "completed": 120,
    "warm_median_ms": 0.9870149951893836,
    "warm_max_ms": 8.475720533169806,
    "warm_under_100ms": 120,
    "connected": 3
  },
  "signed_packet": {
    "completed": 120,
    "warm_median_ms": 0.8116382523439825,
    "warm_max_ms": 7.238766935188323,
    "warm_under_100ms": 120,
    "connected": 3
  },
  "signed_packet_chain": {
    "completed": 120,
    "warm_median_ms": 0.8921412809286267,
    "warm_max_ms": 6.848055985756218,
    "warm_under_100ms": 120,
    "connected": 120
  }
}

## Reusable result

Packet size and retained boundary size govern this route. The connected signed family makes the distinction executable: a graph can be connected and frustrated while retaining small exact packet interfaces. Larger connected components alone do not determine high cost.

The unchanged historical frustrated graphs have different interactions; this catalog supplies an additional family at each N. Applying packet messages to those existing graphs requires their actual source-bound separators. No coupling was removed from an existing canonical calculation.

The test result suggests strong contact with the concept.

## Reproduce

Use `run.py --smoke` for the bounded regression, then `run.py` for all 360 source records. Existing completed result files are not silently overwritten. `query.py FAMILY N` retrieves a source-bound result or executes a fresh packet solve. No global selector or training queue is changed.

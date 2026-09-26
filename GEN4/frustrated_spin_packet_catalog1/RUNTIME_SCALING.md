# Measured runtime scaling

The runtime is not uniform. The measured warm-cache curve has structural steps followed by broadly rising cost as the full exact output grows. These are pod CPU three-repetition medians.

| N | Packet (ms) | Signed packet (ms) | Connected signed packet (ms) |
|---:|---:|---:|---:|
| 10 | 0.172 | 0.163 | 0.267 |
| 20 | 0.321 | 0.319 | 0.460 |
| 40 | 0.522 | 0.525 | 0.655 |
| 60 | 0.531 | 0.527 | 0.601 |
| 61 | 0.891 | 0.883 | 1.000 |
| 62 | 1.558 | 1.692 | 1.718 |
| 80 | 2.993 | 2.994 | 3.258 |
| 100 | 4.678 | 4.897 | 5.055 |
| 110 | 5.853 | 5.581 | 5.915 |
| 120 | 6.222 | 6.393 | 6.848 |

The retained ports are the existing vertices in ordered list [0,1,60,61]. N60 therefore has two ports (four conditional spectra); N61 has three (eight spectra); N62 has four (sixteen spectra). The jump here includes a change in output size. It is not a comparison with a fixed number of requested observables.

From N62 through N120 the four-port output contract is fixed. Increasing graph/energy size raises the size and arithmetic cost of the exact spectra. Timing variation remains visible; the curve is not strictly monotonic.

## Where the time goes

| Packet source | Local cache access (ms) | Polynomial combination (ms) | Full readout and checks (ms) |
|---:|---:|---:|---:|
| 40 | 0.0016 | 0.0158 | 0.4395 |
| 60 | 0.0014 | 0.0116 | 0.4560 |
| 62 | 0.0016 | 0.0219 | 1.4727 |
| 100 | 0.0024 | 0.2330 | 4.2896 |
| 120 | 0.0019 | 0.3837 | 5.6632 |

At N120, full readout and native checks take about 91% of the total warm packet solve. The timed total also includes source-record binding checks and orchestration, so the listed stage medians need not sum exactly to its median.

The observed N62–120 curve is compatible with a roughly linear increase over this finite measured range. A single smooth curve across N1–120 would conceal the retained-port transitions. These data do not measure larger-N runtime.

The clearest next optimization target is complete exact readout/serialization and its repeated checks, while preserving all required spectra and verification. The packet polynomial combination itself is already below 0.4 ms at N120.

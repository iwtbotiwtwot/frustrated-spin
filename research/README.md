# Thermal, selected-coefficient and ratio results — October 2, 2026

These results extend what can be calculated from the structured graph families.
They do not change the published full-density coverage: continuous N1–1800,
isolated full spectra through N5000, explicitly constructed graphs through N20000.

| Result | Completed scope | Record |
|---|---|---|
| Direct thermal-boundary integrals | Every tenfold step 10³⁴+10 through 10⁵⁷+10; three families, five temperatures, 360 cases, 2189 independent checks | [Report](spin_thermal_octo1/REPORT.md), [data](spin_thermal_octo1/RESULTS.json) |
| Exact selected coefficients | 17,424-count N10010 batch; 1,296-count N20000 batch; CPU/GPU agreement | [Report and hardware](spin_gpu_batch1/REPORT.md) |
| Physical normalization | 54 finite thermal comparisons, 378 direct finite-sum checks | [Report](spin_normalization1/REPORT.md) |
| Global continuous transition | Retained 60%-free constructions; 158 finite thermal cases; 275,104 selected exact counts in occupied windows | [Report](spin_transition1/REPORT.md), [derivation](spin_transition1/PROOF.md) |
| Variable free/core ratio | Two exact tricritical points, global inequalities and first-order witnesses | [Report](spin_ratio1/REPORT.md), [standalone reproduction](../reproduce/ratio-transitions/README.md) |

The large-N calculations use compact repeated-component factors and exact
integer multiplicities. They do not expand 10⁵⁷ spins or the corresponding
g(E,M,b) table. Their temperature scaling is stated in the linked report.

For the newer transition/ratio studies the model is
H=−(M²−N)/(2N)+κC_N, with fixed κ and C_N=2Σ_negative s_i s_j.
Whole-Hamiltonian scaling instead has κ=1/N. The normalization comparison
shows that these choices can yield substantially different physical responses.

At fixed κ=3log3/20 the pair family has a tricritical point at 20% free spins;
at κ=261log3/1844 the chain construction has one at 77/461≈16.7028%.
These are coupling-specific results. “Free” means no sparse negative edge;
all spins still participate in the dense mean field. Near these points ratio
variation changes the first ordering onset between continuous and discontinuous.

The preserved reports are dated campaign records. The global-transition study
resolves the normalization report's formerly open remote-maximum question for
the retained families. The ratio study extends those families. Source hashes
are in SOURCE_MANIFEST.json. Some original report links refer to internal
campaign files not distributed here; public reproduction entrypoints are above.
Selected-count bulk streams remain in research custody; their publication
reports and compact result records are included. Existing Drive links cover
the earlier expanded milestone datasets, not these new streams.

No draft manuscript is published by this update. Sean Brady is originator and
conceptual director; OpenAI ChatGPT and Codex are AI research collaborators.

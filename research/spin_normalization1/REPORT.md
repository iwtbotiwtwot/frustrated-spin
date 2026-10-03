# Normalization changes the retained source response

**The explicit fixed-strength-frustration extension gives a substantially
different thermal and boundary response.** The companion
[GPU campaign](../spin_gpu_batch1/REPORT.md) completes independently checked
N20000selected counts and demonstrates efficient coefficient batching.

For the chain at N20000,beta1.4,mean squared magnetization changes from
0.6633215405 under whole scaling to0.0001928565 at fixed frustration strength.
The preparation contribution changes sign. Between-readings and within-interval
contributions remain positive in every tested case. These are complete
thermal integrals, with infinite tails included, not truncated coefficient sums.

## Explicit model

H=-(M^2-N)/(2N)+kappa*C_N, with the original correction C_N.
kappa=1/N is exactly the archived whole-Hamiltonian scaling. kappa=1 is a new
model retaining order-one sparse corrections. It is not automatically the
model obtained by rescaling only missing-edge fill and preserving every original
bond. Existing archived results and the unpublished manuscript remain unchanged.

[PROOF.md](PROOF.md) derives exact coefficient reweighting, normalized Gaussian
integrals, explicit tail bounds, the magnetization-moment identity, and the
limiting zero-field local susceptibility. The fixed-kappa1 local instability
occurs at beta=1.663814710634 for signed packets
and beta=1.663815941534 for chains. The whole-scaled
sequence has limiting local threshold1. Exact source polynomial differentiation
verifies all susceptibility and fourth-cumulant identities. A negative quartic
coefficient fixes the continuous local bifurcation direction; classification of
all distant competing maxima is a separate remaining global question.

## Complete finite comparison

54cases: N200,5000,20000; packet,signed_packet,signed_packet_chain;
beta1,1.4,1.8; kappa1/N and1.128-bit Arb, relative tolerance1e-22,
absolute tolerance1e-24, explicit tails beyond auxiliary field4.
Every exact input, rational interval endpoint, boundary weight and budget is
retained in RESULTS.json. The packet has C_N=0 and is the normalization control.
The original three-part readout and its declared one-third clock are unchanged.

Chain N20000 (rounded display of certified intervals):

| beta | Normalization | <(M/N)^2> | Preparation | Between readings | Within interval |
|---:|---|---:|---:|---:|---:|
| 1.0 | whole_scaled | 0.008227817735 | 0.004712775828 | 6.554914491e-06 | 8.628078246e-06 |
| 1.0 | fixed_frustration | 7.961144462e-05 | -0.406512831 | 0.002423634708 | 0.004300513301 |
| 1.4 | whole_scaled | 0.6633215405 | 0.06100365716 | 0.01063589674 | 0.01433944616 |
| 1.4 | fixed_frustration | 0.0001928565097 | -0.4269585101 | 0.0005376701437 | 0.0009715863729 |
| 1.8 | whole_scaled | 0.8699110198 | 0.02289208915 | 0.00600530866 | 0.008311212487 |
| 1.8 | fixed_frustration | 0.07623162881 | -0.4304894818 | 0.0001693792819 | 0.0003070874842 |

Preparation is the signed difference p_full-p_equilibrated. Its negative value
means that the declared prepared start has lower accepted probability than the
equilibrated comparison. No absolute value or positivity assumption is applied.

The12-worker pod study, including the finite-sum gate and all18N200checks,
took6.909238s of worker wall time. The independent check expands the
full N200integer polynomial, then performs direct192-bit finite Gibbs sums;
378comparisons agree. This uses no Gaussian integration. No expanded large-N
spectrum was needed. Source tables retain their original SHA-256 identities.

## What the old coefficient window actually covers

The N20000GPU benchmark queried k9996..10004,d2329..2337,all16boundary states.
Summing all1296counts with the new weights and dividing by complete certified Z
gives the following log10 probability; the omitted probability is also stored.

| beta | Normalization | log10(window probability) |
|---:|---|---:|
| 1.0 | whole_scaled | -3.477273 |
| 1.0 | fixed_frustration | -2681.489280 |
| 1.4 | whole_scaled | -698.217535 |
| 1.4 | fixed_frustration | -4270.747305 |
| 1.8 | whole_scaled | -2060.859739 |
| 1.8 | fixed_frustration | -5906.949698 |

At beta1 under whole scaling the probability is about0.0003332. Under fixed
frustration it is about10^-2681.489. The old zero-coupling central window is
therefore an implementation benchmark, not the thermally important region of
the new model. This accounting identifies exactly why increasing that same
window's N would provide little additional physical information.

**Highest-value next step:** use the complete finite-factor thermal law to
choose magnetization/defect windows with a declared and measured Gibbs mass,
then extract those counts in GPU batches. Low-field fixed-frustration sources
favor d near L/(1+exp(-4*beta*kappa)); the finite root and mean-field response
must be retained when selecting actual windows. The global competing-maxima
question can be attacked analytically alongside that readout.

## Execution, provenance and custody

STARBREAKER/SB-GEN3-ACCUMULATION-R1 with SLC-GEN3-R4/SLC-GEN3-CEV1-R4.
The source-bound normalization adapter supplies the missing independent sparse
coupling; SPIN_WINDOW_THERMAL_MASS records complete-partition window accounting.
Native exports and checkpoints are retained. Local controllers shared the
existing managed sam-r3.slice allocation; pod thermal workers used CPU4–15,
alongside the coefficient verifier on CPU2. No helper computation, prime-event
change, generic installation, Chalkboard activation or public publication.

All61remote thermal output/log hashes match T500. Coefficient source is bound
by SHA in READOUT_BINDING.json and independently checked by spin_gpu_batch1.
Bulk: /home/sam/mnt/lilhelper-t500/GEN4/spin_normalization1. CUSTODY.json records full archive readback. Pod originals and T500
copies remain; the T500archive shares its disk. Workers finished; pod remains
rented. The existing paper is an immutable earlier draft; these results are
new material for its next explicitly versioned revision.

# Exact spin catalog and transition training

Installed source family: every integer N1..96, induced prefixes of the retained
N96 graph. The original eleven entries and ten skip transitions are preserved.
There are 96 entries, 95 adjacent transitions plus ten original skip transitions.

Native operations through DomainSession.execute:

- GEN3_SPIN_CATALOG {} lists explicit sources and references.
- GEN3_SPIN_ENTRY {"N":96} retrieves exact DOS and retained port operators.
- GEN3_SPIN_TRANSITION {"from_N":95,"to_N":96} retrieves measured transition work.
- GEN3_SPIN_LEARNING {} lists nine new models and three training experience roots.
- GEN3_SPIN_PLAN {"source":explicit_graph,"previous_N":96} compares fresh min-fill,
  transition priority, parent plan, adjacent-order repair and six-seed tie portfolio.

The planner uses native C++/GMP CART predictions from the ladder depth-one combined
head, with exact structural work as tie-break. All candidates and scores remain
visible. Its Python combinatorial planner executes inside the native runtime;
it computes a plan, not a new spin spectrum. Width22 and four qualified NTT primes
are current execution admission limits, not scientific restrictions on source N.

Three completed pod training campaigns are retained: 165 exact ladder solves;
450 CPU restarts plus 90 incremental steps across N1..30; 238 training solves and
one separate GPU warmup across every N1..96. Repeats and aliases are grouped.
All-integer policy heads are depth zero: their 16/16 reserved choices came from
structural tie-break, not learned discrimination. Earlier ladder heads are depth
one and selected the N96 portfolio before its new timings were measured.

N1..30 transfer is exact boundary arithmetic over a declared N30 future horizon.
Its preserved runner is GEN4/frustrated_spin_n1_30_training1/train_small.py;
GEN4_SPIN_INCREMENTAL_STEP is a campaign adapter, not a globally installed op.
Previous scalar spectra alone cannot reconstruct an unretained future boundary.
All models, source definitions, full results and training examples are reusable;
this is native policy/experience learning, not retraining a language model.

Timings cover exact DOS and retained port operators, excluding historical T18
attachments. See GEN4/frustrated_spin_training_install1/RESULT.md and ANALYSIS.json.

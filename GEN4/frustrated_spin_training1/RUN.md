# Transition training successor

Owner explicitly requests training: run N2–96 multiple ways and learn the best
transition method before advancing to N108. Prior catalog/result is immutable.

Agent design: five planning strategies, three rotated-order fresh repetitions
per source. Compare fresh min-fill, previous-order priority, parent plan,
adjacent-swap repair, and a deterministic tie-order portfolio. Each fresh solve
must reproduce its exact catalog spectrum and all retained port rows. Timing
records separate preparation, GPU arithmetic and CPU reconstruction.

Identical mathematical plans are grouped for learning; repetitions are timing
samples, not independent training sources. Compare exact structural-cost choice,
nearest prior experience, and native CART heads using structural, transition,
and combined features. Fit on N2–72, select depth on N84, freeze predictions
before new N96 method measurements. N96 is held out from these fits; its graph
and original catalog baseline are previously known. Source roster stays explicit.

14 persistent GPU workers, CPU planner/exact reconstruction, RAM/VRAM reuse,
compact durable checkpoints. No N108 source or solve is part of this batch.

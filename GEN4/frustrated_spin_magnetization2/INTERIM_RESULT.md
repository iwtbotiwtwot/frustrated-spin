# Exact magnetization composition improvement

2026-09-26 interim result. Sean Brady is originator and conceptual director; OpenAI ChatGPT and Codex are AI research collaborators.

All six dense N300 cases and all six dense N450 cases completed with exact verification. Small-source qualification, field and wrong controls are retained in `pod_evidence/QUALIFICATION.json`; individual receipts and runtime identity are alongside it. The one-hour pod controller PID 42525 remains active, with deadline 2026-09-27 00:09:04 UTC and a planned next level N600.

The matched N300 signed-packet-chain, fill -1 comparison took **16.4956964 seconds optimized versus 116.5862062 seconds with the previous implementation**, a **7.07-fold improvement**. Both timing scopes include solving and verification, excluding cold CUDA initialization and persistence. Complete spectra and joint distributions agree. This is one matched timing observation, not a repeated timing distribution.

The correction graph has nine zero-coupling bridges. Removing their identically zero terms splits the calculation into ten 30-vertex components with five distinct component tables. Repeated exact polynomials are reused by integer powers; balanced products and one retained-port polynomial at a time reduce composition work. Primary composition/readout took 7.577 seconds and independent reference composition/readout 6.702 seconds, versus 11.571 + 2.727 and 97.211 + 2.875 seconds in the old route. Final checks took 2.056 seconds.

The matched receipt's peak RSS includes both implementations in one process and must not be presented as optimized-only memory usage. The N450 hardest signed-chain negative-fill case finished in 58.845 seconds with peak RSS 810352 KiB. These source-specific gains arise from exact structure and arithmetic organization. GPU local enumeration is already a small portion of the total.

For L>15 exchange research, the transferable idea is to identify exact reusable operator blocks and compose their boundary action. The spin magnetization histogram itself is not sufficient to reconstruct a quantum exchange operator. A useful proposed next experiment is an expensive retained L14 sector: find a finer invariant decomposition or repeated restricted operator, verify reconstruction against the retained exact sector, and measure total savings. No new L14/L15 run was launched by this discussion.

Monitor or stop on the pod:

    cat /opt/gen4-spin-magnetization2/project/STATUS.json
    touch /opt/gen4-spin-magnetization2/project/STOP

Full current results remain on the pod; the local evidence directory is an interim receipt snapshot. The earlier completed T500 transfer predates this campaign's completion.

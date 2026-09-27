# Installed shared packet and joint spin upgrade

**Status: PROMOTED, INSTALLED, AND ADOPTED.**
Sean Brady is originator and conceptual director; OpenAI ChatGPT and Codex are research collaborators.

The existing shared SLC/CE spin tools now include exact packet compilation,
joint energy–magnetization–boundary solving and readout, uniform field/pair and
ordered-boundary response, and native retained-result reuse. This extends the
existing GEN3_SPIN and GEN3_RESULT interfaces used by GEN3, GEN4, SB and A3D41.

- [Analysis and contribution map](ANALYSIS.md)
- [Installed interface guide](GUIDE.md)
- [Installation report](RESULT.md)
- [Data coverage](DATA_COVERAGE.json)
- [Reproduction and recovery](REPRODUCE.md)
- [Local qualification](installed_qualification/QUALIFICATION.json)
- [GEN4 GPU qualification](pod_upgrade/qualification2/QUALIFICATION.json)
- [Local domain adoption](installed_adoption/ADOPTION.json)
- [GEN4 domain adoption](pod_upgrade/adoption_final/ADOPTION.json)
- [GEN4 workstation adoption/recovery](gen4_math_adoption/ADOPTION.json)

Global workstation: SLC-GEN3-R4 / SLC-GEN3-CEV1-R4, generation unchanged.
Scoped GEN4: SLC-GEN4-P1 / SLC-GEN4-CE-P1, selected at `/opt/gen4/current` before
pod shutdown. The complete upgraded capsule is preserved locally and on T500.
No unattended training or L-series campaign is started by this installation.

The pod is safe to stop. Research files and promoted runtime total13,069,700,160bytes,
with complete SHA-256 agreement on both the workstation and T500. The joint
campaign stopped safely after all six N900 cases completed.

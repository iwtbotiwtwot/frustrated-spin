# Packet-family catalog extension

Owner: Sean Brady, originator and conceptual director.

Owner task: pause training and extend the N100/N105 packet-family graph across the rest of the N1–120 catalog using the best available method. The training controller was stopped safely; it is not restarted by this project.

This additive project creates three explicitly named catalogs, each N1–120:

- `packet`: induced-prefix ladder that preserves canonical N100 and N105 exactly, then extends the remaining three two-layer packets to three K5 layers each.
- `signed_packet`: same packet topology with one negative edge in each five-spin layer; complete layers contain explicit frustrated triangles.
- `signed_packet_chain`: the signed packets joined through one gateway spin per packet, with alternating signed bridges; every resulting graph is connected.

The last two families are agent-designed comparisons supporting the owner's extension objective. N is a size, not a unique graph identity. These sources have separate hashes, family names and full outputs. Existing canonical graphs/results and N121–144 holdouts are unchanged.

The source-bound compiler preserves every interaction. Independent packets combine through polynomial powers and balanced multiplication; connected packets use exact two-state boundary messages. Identical local spectra are cached by their complete fields, couplings and ordered retained ports. A fresh timed call always reconstructs the complete global spectrum. Full-graph variable elimination supplies a separately executed comparison for every source.

Artifacts: REPORT.md; CATALOG.csv; GRAMMAR.json; SOURCE_MANIFEST.json; sources/; results/ (full exact answers and precommits); PACKET_TABLES.json.gz; native sessions/; verification evidence; resource/runtime identity; hashes.

Pod working location: `/opt/gen4-learning/GEN4/frustrated_spin_packet_catalog1`.
Durable mirror: `/workspace/gen4/runs/frustrated-spin-packet-catalog1`.
Local repository location: `GEN4/frustrated_spin_packet_catalog1`.

On the pod, activate `/opt/gen4/restore14/activate.sh` and use:

```sh
python query.py packet 110
python query.py signed_packet_chain 120 --solve
python query.py packet 110 --solve --empty-cache
```

The first command is explicitly a retained-result lookup. The latter two execute fresh full-spectrum calculations through MATTER_SEARCH and retain receipts. Full catalog reproduction is `python run.py`; a completed catalog is not overwritten. Use a separate output copy for a new timing campaign. No global selector or previous training queue is modified.

# Spin tools command line

The installed `./spin-tools` calls the current MATTER_SEARCH DomainSession and
prints its verified engine announcement/session path to stderr. Each operation
retains its full native receipt and an additional full JSON result file; terminal
output is compact unless `--full` is selected. `--output FILE` chooses the full
result file and refuses to overwrite an existing file. `--session DIRECTORY`
reopens an explicit compatible session; work commands checkpoint their results.

```sh
./spin-tools sources
./spin-tools source --N 100
./spin-tools source --N 105 --full
./spin-tools source --N 120 --family SLCX028_N120_REPEATED_MOTIF_RING_V1
./spin-tools select --N 105 --policy structural
./spin-tools solve graph.json --payload solve-options.json
./spin-tools solve --N 105 --payload solve-options.json
./spin-tools contract contraction-payload.json
./spin-tools readout readout-payload.json
./spin-tools call GEN3_SPIN_SOURCE '{"N":100}'
```

Graph and payload arguments accept a JSON filename, an inline object, or `-`
for stdin. Select/solve accept an explicit graph or the catalog selectors `--N`,
`--family`, `--hash`; their optional `--payload` contributes operation-specific
fields unchanged. The generic `call OP PAYLOAD` passes its entire JSON object
unchanged, allowing all installed options without extending the CLI. Global
`--root`, `--session`, `--output`, and `--full` work before or after a command.
For example, a solve payload can contain `{"backend":"cpu","mode":"fresh",
"options":{"method":"components"}}`. Fresh solve computes the supplied graph;
source retrieval reuses a completed result. Recovery mode accepts the explicit
retained result reference defined by the solve operation.

On the workstation, calculation commands run through the installed resource
controller and `.venv-r3`. GEN4 uses `/opt/gen4/venv` under pod resource management.
No launcher starts workers, restores old campaigns, or changes source selection
implicitly. N-only 120 selects the current frontier; request the historical ring
by its family or canonical source hash. N100/N105 retained component metadata is
not a precomputed CUDA cutset plan; select/solve use their declared operation
policy and backend.

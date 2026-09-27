# Reproduce

Run from the repository using `.venv-r3/bin/python` and the installed resource launcher. `run.py` opens a current ATOM3D DomainSession and creates `execution/` only when absent. Preserve this completed directory; copy the scripts to a fresh sibling project directory under GEN4 for a rerun. Use a fresh resource run name.

```sh
.venv-r3/bin/python CURRENT_REVISION/engines/SLC/gen3/resources.py run --name NEW-LOWERCASE-NAME --seconds 600 -- .venv-r3/bin/python GEN4/NEW-PROJECT/run.py
.venv-r3/bin/python GEN4/NEW-PROJECT/analyze.py
```

`analyze.py` derives the report from saved results without scientific execution. Source input hash is in execution/DESIGN.json. Native payloads and receipts, exact source identities and checkpoint are retained in execution/sessions/.

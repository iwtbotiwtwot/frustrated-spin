# Reproduce

From the repository root, use `.venv-r3/bin/python`. Preserve this completed
directory: copy run.py and analyze.py to a fresh sibling directory under GEN4
and use a fresh lowercase resource-run name. run.py refuses to overwrite an
existing execution directory.

```
.venv-r3/bin/python CURRENT_REVISION/engines/SLC/gen3/resources.py run --name FRESH-NAME --seconds 600 -- .venv-r3/bin/python GEN4/FRESH-DIRECTORY/run.py
.venv-r3/bin/python GEN4/FRESH-DIRECTORY/analyze.py
```

The first script executes the installed domain. The second derives the report
and checks the source polynomial identity from saved native results; it does
not launch another domain experiment. Input hash and source are in DESIGN.json,
while execution/sessions contains native receipts and the final checkpoint.

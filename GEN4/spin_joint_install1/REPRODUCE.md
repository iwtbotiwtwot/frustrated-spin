# Reproduction, use, and recovery

Use the current shared workstation runtime:

```bash
./spin-tools call GEN3_SPIN_SOURCES '{}'
./spin-tools call GEN3_SPIN_SOLVE '{"source_recipe":{"family":"packet","N":300}}'
./spin-tools call GEN3_SPIN_SOURCE '{"joint_key":"packet_N900_fill_+1"}'
```

Use the returned result_ref with GEN3_SPIN_READOUT and an exact uniform_field
string. Use the existing DomainSession or GEN4 ResearchMathematics interfaces to
keep a consumer warm and retain request reuse. See GUIDE.md for all payloads.
No research worker runs automatically.

Installed source files: CURRENT_REVISION/engines/SLC/gen3/spin_joint.py,
spin_packet.py and spin_joint_core; shared dispatch remains spin_tools.py.
Existing spin_exact, source catalog, selection, GPU solver and CE domains remain.

Re-run implementation qualification only when a relevant change warrants it:

```bash
.venv-r3/bin/python GEN4/spin_joint_install1/qualify.py --root . --out /tmp/spin-joint-new-qualification
```

For a new deployment, use the retained installer only after inspecting its
candidate/root and existing resource state. It authenticates the predecessor,
stages immutable objects, takes the existing runtime activation lock, preserves
changed files, refreshes all registry bindings, and rolls back on verification
failure. The installed directories contain STAGED.json and predecessor/ backups.
Do not copy loose source files over authenticated binding paths.

The complete scoped GEN4 successor is in pod_upgrade/runtime. Its RELEASE.json
and requirements.lock authenticate the captured package and qualified dependency
environment. All package files are covered by
pod_upgrade/FINAL_DOWNLOAD_MANIFEST.json; the backup includes failed and successful
qualification/install records. A future pod can restore this capsule and use a
compatible CUDA/FLINT environment; package/solver qualification should identify
that new hardware. Old timings retain their original backend/topology identity.

The research archive is custody/pod/opt/. Restore complete joint directories with
MANIFEST.json and every referenced boundary shard. For this workstation, the
installed catalog already lists their preserved local locations; the T500 copy
has its own registered host path. Native exported references mark when these
external artifacts are required. Exact cached response results can be reused
without scanning the table again.

The packet continuation predecessor and its source checkpoints are preserved in
custody/pod/opt/gen4-spin-continuation1/runtime and the earlier T500 continuation
backup. Current workstation packet results reach N1408. The final joint campaign
STATUS.json records a safe stop after N900, and its code, receipts, inputs and
native sessions are preserved. No N1050 joint solve was executed in that final
window. Resume only as a separately authorized campaign.

All hashes for bulk preservation are in custody/FINAL_INVENTORY.json and
pod_upgrade/FINAL_DOWNLOAD_MANIFEST.json. Verification receipts cover both local
copies and T500. A replica on T500 is a second machine/disk; directories on that
same disk are not counted as additional independent copies.

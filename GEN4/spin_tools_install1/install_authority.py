"""Publish the completed additive capability after immutable history creation."""
import hashlib,json,re,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
assert not (P/'AUTHORITY.json').exists()
assert json.loads((P/'VERIFICATION.json').read_text())['status']=='PASS'
entries=R/'SAM_HISTORY/entries';n=max(int(f.name[1:7]) for f in entries.glob('H[0-9][0-9][0-9][0-9][0-9][0-9]_*.md'))+1
entry=f'H{n:06d}';name=f'{entry}_2026-09-24_GEN3_GEN4_COMPLETE_SPIN_TOOLS.md'
files=['00_CURRENT.md','01_SLC_CURRENT.md','10_PODS_CURRENT.md','13_GEN4_RESEARCH_WEB_CURRENT.md','04_PRIME_GRAMMAR_CURRENT.md']
for d in ['authority_before','authority_after']:(P/d).mkdir(exist_ok=True)
for f in files:shutil.copy2(R/'SAM_LIVE'/f,P/'authority_before'/f)
statement=f'''The complete spin tool collection is installed and executed on local
SLC-GEN3-R4 / SLC-GEN3-CEV1-R4 and the research pod's scoped
SLC-GEN4-P1 / SLC-GEN4-CE-P1, preserving their current generation identities.
Every integer N1–N96, N100, N105 and current N120 is a default source:99sizes.
A separate historical N120ring gives100source-family records. All97preceding
references remain unchanged;1692mathematical objects,106transitions,
11spin models and38cached plans are retained. The native interface now has
14GEN3_SPIN operations, including source selection, fresh CPU/GPU solving,
signed finite-factor contraction, conditioning/readout and explicit recovery.

Local qualification passes139checks;research-pod qualification passes143.
Fresh N100/N105 agree on the complete scalar spectrum and all16conditional
rows. Actual one-device CUDA output agrees with CPU for a changed source;
80tasks/fiveprimes/two branch groups complete. Completed-checkpoint recovery
reuses all80tasks and performs zero fresh arithmetic. Native focused inference
is exercised separately, with hardware transfer identified. The 14-MIG timing
calibration remains scoped; no new N120 timing is claimed.

MATTER_SEARCH,ATOM3D,STARBREAKER andRH execute the shared signed-factor tool.
The web adds five native adoption calls/five checkpoints/53custody files,
447native results, and searchable capability documentation/findings.
Use `./spin-tools` or `DomainSession.execute`; source and domain mappings remain
explicit. MP candidate224872321 and the MP research direction are shelved by
owner instruction. The original RH root, previous scientific results,
paused controllers and suspended Chalkboard retain their scope.

**The test result suggests strong contact with the concept.**
'''
(P/'LIVE_STATEMENT.md').write_text(statement)
history=f'''---
entry_id: {entry}
entry_date: 2026-09-24
entry_type: RESULT_INSTALLATION_AND_OWNER_DIRECTION
status: IMMUTABLE_HISTORY
supersedes: H001722 spin installation counts; preserves its exact results and calibration
prior_entries: H001722, H001724, H001725
affects_live:
'''+''.join(f'  - SAM_LIVE/{f}\n' for f in files)+f'''---

# Complete source-aware spin tools in GEN3 and GEN4

Sean explicitly requested every integer N1 through N96, followed by N100,
N105 and N120, installed for broad program use. He also directed that MP and
candidate224872321 be put on the shelf. Source grouping, native exact methods,
qualification inputs and the shared interface are Codex implementation choices.

[Report](../../GEN4/spin_tools_install1/RESULT.md),
[verification](../../GEN4/spin_tools_install1/VERIFICATION.json),
[guide](../../GEN4/spin_tools_install1/GUIDE.md),
[source inventory](../../GEN4/spin_tools_install1/SOURCE_SUMMARY.md),
[findings](../../GEN4/spin_tools_install1/FINDINGS.md).
Native receipts, installation staging/backups and original source custody are
linked from that report. Three existing prerequisite installations on the
research pod pass their28/210/49adoption checks before the final extension.
Runtime authentication passes536local and426research-pod file checks.

## Exact new current statement

{statement}
## Implementation record and boundaries

The first publication rejected untagged archived timing metadata; the corrected
publication uses lossless float64 tags. The first local installation rejected
an out-of-tree CLI binding and rolled back; its staged/failed records remain.
The corrected CLI lives in CURRENT_REVISION and authenticates normally.
Both installed packages match PACKAGE_MANIFEST_FINAL.json; the draft manifest
is preserved. Current generations, prior source references and models remain.
No call was made to the stopped216.243.220.128pod. No MP arithmetic, PrimeNet
submission, new CMB fit, physical source assignment or uniform RH result occurs.
The exact boundary-shift reuse identity is a Codex-proposed next operation,
separate from the operations implemented and tested here.

Previous live text is preserved under the campaign's authority_before;
replacement snapshots are under authority_after. The numbered entry is
created before any live replacement.
'''
with (entries/name).open('x') as f:f.write(history)
for fn in files:
 f=R/'SAM_LIVE'/fn;s=f.read_text()
 if fn=='01_SLC_CURRENT.md':
  start=s.index('[Spin](../GEN4/frustrated_spin_focused_install1/RESULT.md)');end=s.index('\n\nThe [mathematical operations]',start)
  s=s[:start]+f'''[Shared spin tools](../GEN4/spin_tools_install1/RESULT.md)({entry}):
**1692objects**;99default sizes(everyN1..96,100,105,120),100family records,
14GEN3_SPIN operations;106transitions,11models/38cached plans preserved.
Source-aware CPU/GPU solving,signed finite factors,readout and recovery;
139local/143research-pod native checks;536local/426pod bindings.
Four CE domains execute the shared tool;actual GPU/CPU full outputs agree.
Use `./spin-tools`;[guide](../GEN4/spin_tools_install1/GUIDE.md).
Prior H001722 cost/pairwise calibration and exact frontier results remain scoped.'''+s[end:]
 elif fn=='10_PODS_CURRENT.md':
  anchor='## Current spin pod — H001722';assert anchor in s
  s=s.replace(anchor,f'''## Research pod shared spin tools — {entry}

SSH198.13.252.37:32398;runtime `/opt/gen4/current`;one full RTX PRO6000
Blackwell Server Edition. SLC-GEN4-P1/SLC-GEN4-CE-P1;generation unchanged.
[Installed capability](../GEN4/spin_tools_install1/RESULT.md):99default sizes,
100families,1692objects,14spin operations,143native checks and426bindings.
Actual five-prime/two-group GPU execution and complete checkpoint recovery pass.
Research web `/workspace/gen4/rh-voli-unified1` executes five adoption calls.
No unattended worker is started;MP is shelved. The former spin pod below
remains stopped and was not contacted for this installation.

## Stopped historical spin pod — H001722/H001725''',1)
 elif fn=='13_GEN4_RESEARCH_WEB_CURRENT.md':
  anchor='## MP53 prediction and commonality';assert anchor in s
  s=s.replace(anchor,f'''## Installed shared spin capability — {entry}

[Report](../GEN4/spin_tools_install1/RESULT.md),
[findings](../GEN4/spin_tools_install1/FINDINGS.md),
[guide](../GEN4/spin_tools_install1/GUIDE.md).

{statement}
## Shelved MP53 prediction and commonality''',1)
  s=s.replace('The next technical route is optimized arithmetic beneath theorem/support\nplanning, preserving alternative factor branches and charging fresh factor\ndiscovery.', 'The retained next technical route, shelved with MP by the owner, is optimized\narithmetic beneath theorem/support planning, preserving alternative factor\nbranches and charging fresh factor discovery.')
 elif fn=='04_PRIME_GRAMMAR_CURRENT.md':
  anchor='## Current GEN4 MP53 prediction and commonality';assert anchor in s
  s=s.replace(anchor,f'''## Owner-directed research state — {entry}

MP research and candidate **224872321** are **SHELVED_BY_OWNER**.
Retain the forecast, commonality, replay and acceleration findings below for
owner-directed resumption. The current work installs shared spin tools in
GEN3/4; it executes no MP task and starts no MP worker.

## Retained GEN4 MP53 prediction and commonality''',1)
 elif fn=='00_CURRENT.md':
  anchor='## Immediate state\n\n';assert anchor in s
  s=s.replace(anchor,anchor+f'''- [Complete shared spin tools](../GEN4/spin_tools_install1/RESULT.md)({entry}):
  everyN1..96 plus100,105,120;99defaults/100families/1692objects.
  14operations;fresh CPU/GPU solving,signed factors,readout,recovery;
  139local/143research-pod checks pass. Use `./spin-tools`.
  MP research/candidate224872321 shelved by owner;prior records retained.
''',1)
 s=re.sub(r'^history_entry: H\d+',f'history_entry: {entry}',s,count=1,flags=re.M)
 f.write_text(s);shutil.copy2(f,P/'authority_after'/fn)
with (R/'SAM_HISTORY/HISTORY_INDEX.md').open('a') as f:f.write(f'\n| {entry} | 2026-09-24 | RESULT_INSTALLATION_AND_OWNER_DIRECTION | [Complete GEN3/4 spin tools](entries/{name}) | EveryN1..96+100/105/120;99defaults/100families;freshCPU/GPU/sharedfactors;139/143checks;MPshelved |\n')
shutil.copy2(entries/name,P/'authority_after'/name)
a={'entry':entry,'history':str((entries/name).relative_to(R)),'live_files':[{'path':'SAM_LIVE/'+f,'sha256':hashlib.sha256((R/'SAM_LIVE'/f).read_bytes()).hexdigest()} for f in files]}
(P/'AUTHORITY.json').write_text(json.dumps(a,indent=2)+'\n');print(entry)

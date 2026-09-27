from pathlib import Path
import re,shutil,json
R=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
assert json.loads((P/'PROMOTION.json').read_text())['status']=='PROMOTED_INSTALLED_AND_ADOPTED'
files=['00_CURRENT.md','01_SLC_CURRENT.md','03_STARBREAKER_GW_CURRENT.md','05_ATOM3D_CURRENT.md','10_PODS_CURRENT.md','11_VOLII_EXCHANGE_CURRENT.md','13_GEN4_RESEARCH_WEB_CURRENT.md']
entry='H001766';name=entry+'_2026-09-26_SHARED_SPIN_JOINT_INSTALL_AND_CUSTODY.md'
assert max(int(f.name[1:7]) for f in (R/'SAM_HISTORY/entries').glob('H??????_*.md'))==1765
stage={}
link='[Shared packet/joint upgrade](../GEN4/spin_joint_install1/RESULT.md)'
for fn in files:
 text=(R/'SAM_LIVE'/fn).read_text()
 if fn=='00_CURRENT.md':
  text=text.replace('Spin PAUSED(H001732);see Pods.','Shared spin upgrade installed; final joint campaign safely stopped(H001766).')
  a=text.index('- [Complete shared spin tools]');b=text.index('- Sean Brady',a)
  text=text[:a]+f'''- {link}({entry}):120canonical defaults,
  123source records,1840native objects. Packet recipes/complete graphs through
  N1408;54dense magnetization cases;24joint cases atN120/300/750/900.
  Exact field/pair/boundary readout and native reuse installed in existing
  SLC/CE/GEN3/GEN4/SB/A3D41 routes;369local/381GEN4 checks pass.
  Pod data/runtime:13.07GB verified locally and onT500;safe to stop pod.
'''+text[b:]
 elif fn=='01_SLC_CURRENT.md':
  a=text.index('## Spin —');b=text.index('## Installed upgrade',a)
  text=text[:a]+f'''## Spin — {entry}

Shared packet/joint tools installed; final N900 campaign stopped; backups verified.

'''+text[b:]
  a=text.index('[Shared spin tools]');b=text.index('\n\n[Mathematical operations]',a)
  text=text[:a]+f'''[Shared spin](../GEN4/spin_joint_install1/RESULT.md)({entry}):1840objects,
120defaults/123sources;14existing operations extended with packet compilation,
joint E/M/b solving and exact field/pair/boundary readout. Native reuse/recovery;
369local/381GEN4 checks;SB/A3D41 and GEN4 workstation adoption pass.
Graph/packet sources through1408;24joint datasets at120/300/750/900.
Use `./spin-tools`;[guide](../GEN4/spin_joint_install1/GUIDE.md).
Old106transitions,11models/38plans and their hardware scopes remain.'''+text[b:]
 elif fn in ['03_STARBREAKER_GW_CURRENT.md','05_ATOM3D_CURRENT.md']:
  marker='## Completed Starbreaker object' if fn.startswith('03') else '## A3D41'
  if fn.startswith('03'):
   paragraph=f'''## Shared exact source response — {entry}

{link}: installed through existing SB/CE operations.
The inherited N100 source retains its full DOS while gaining exact joint
E/M/ordered-boundary response and opposite-sign endpoint-field readout.
Native reuse/checkpoint recovery and preserved N900 streaming execute.
The SB engine,45policies,ordered histories and matter/carrier types remain.

'''
  else:
   paragraph=f'''## Shared joint phase/source response — {entry}

{link}: existing A3D41/CE route executes both actual
VolumeII C4 six-spin sources with retained joint E/M/b, formal alignment and
collective coupling, boundary response and exact cached reuse.
Original full spectra match;M=2sumRe(z) on the retained phase map.
Physical units remain source-mapped; training and L-series pauses remain.

'''
  text=text.replace(marker,paragraph+marker,1)
 elif fn=='10_PODS_CURRENT.md':
  a=text.index('## N97–119 exact catalogue queue');b=text.index('## Pod priorities',a)
  text=text[:a]+f'''## Spin final custody and installed runtime — {entry}

{link}: joint campaign on69.8.146.173:11136 safely
stopped after all sixN900cases at2026-09-27T01:03:37UTC. N1050not started.
All24joint datasets/54dense production cases and complete runtime are preserved.
Research:4947files/11,987,816,855bytes;upgraded capsule:3931files/1,081,883,305bytes.
Every listed hash matches workstation andT500. **Pod safe to stop**;no hardware
termination performed. [Custody/recovery](../GEN4/spin_joint_install1/REPRODUCE.md).
Scoped GEN4-P1/CE-P1 shared upgrade promoted at`/opt/gen4/current`;
381GPU/CPU checks and12domain-adoption checks pass. Predecessor runtime unchanged.
Completed N97–119 archive now supplies the installed contiguousN1..120 registry;
its packet/connected-prefix distinctions remain. No new unattended campaign.

'''+text[b:]
 elif fn=='11_VOLII_EXCHANGE_CURRENT.md':
  marker='## Constructive GEN4 expansion'
  text=text.replace(marker,f'''## Installed collective and boundary response — {entry}

{link} extends existing SLC/CE/GEN3/GEN4 operations.
Both actual C4 frustrated six-spin source maps execute through A3D41, preserving
full spectra and adding joint E/M/b readout. M=2sumRe(z) supplies an exact formal
phase-alignment coordinate;uniform pair and ordered-boundary fields reuse the
same table. Exact moments,covariance,ground families and crossing fields return
through native references. [Contribution analysis](../GEN4/spin_joint_install1/ANALYSIS.md).
All24completed joint datasets atN120/300/750/900 are installed or indexed for
hashed streaming from verified local/T500 custody. L-series remains paused.

'''+marker,1)
 elif fn=='13_GEN4_RESEARCH_WEB_CURRENT.md':
  a=text.index('## Complete graphs and joint collective readout');b=text.index('[Native ruler, clock and energy report]',a)
  text=text[:a]+f'''## Installed complete-source and joint capability — {entry}

{link};[analysis](../GEN4/spin_joint_install1/ANALYSIS.md).
The existing14spin operations now include exact packet compilation,joint E/M/b
solving,field/pair/boundary response and native result reuse.120canonical defaults,
123source records,1840native objects. Packet and fully constructed graph sources
reachN1408;8,448complete graphs. Exact dense production:54cases;full joint tables:
24cases,six each atN120/300/750/900. These cover different objects explicitly.

369local/381GEN4 checks pass. SB's inheritedN100 and A3D41's actualC4 sources
execute;GEN4 workstation reuses an N900 response after reopening.
The final joint campaign is safely stopped;13.07GB research/runtime is verified
on workstation andT500. Pod can be stopped;no further pod dependency.
L-series remains OWNER_PAUSED(H001764);current global generation is unchanged.

'''+text[b:]
  a=text.index('## Installed shared spin capability');b=text.find('\n## ',a+4)
  text=text[:a]+f'''## Shared spin capability — {entry}

Current installation and domain mappings are linked above. H001726 remains the
original99default/100family installation. Its14operations,106transitions,
11models/38cached plans and typed hardware measurements remain available.
New source records,packet methods,joint responses and authenticated retained
inputs extend that same runtime;no separate domain solver is introduced.
'''+text[b:]
 # Replace superseded opening summaries within the bounded live documents.
 if fn=='03_STARBREAKER_GW_CURRENT.md':
  a=text.index('[Pod pilot]');b=text.index('[CQG revision]',a)
  text=text[:a]+'**SB-GEN3-ACCUMULATION-R1**,45policies; native signed energy/receiver plans remain.\n\n'+text[b:]
 elif fn=='05_ATOM3D_CURRENT.md':
  a=text.index('[5090 pilot]');b=text.index('## A3D41',a)
  text=text[:a]+f"""[Joint phase/source response](../GEN4/spin_joint_install1/RESULT.md)({entry}):
A3D41/CE executes both actualC4 sources;exactE/M/b,field/pair/boundary readout
and cached reuse. M=2sumRe(z);physical units/source typing and pauses remain.

"""+text[b:]
 elif fn=='10_PODS_CURRENT.md':
  a=text.index('## Spin final custody');b=text.index('## Pod priorities',a)
  text=text[:a]+f"""## Spin installation and final custody — {entry}

[Installed upgrade/custody](../GEN4/spin_joint_install1/RESULT.md):joint run
stopped after sixN900cases;N1050not started.54dense cases/24joint datasets;
13.07GB SHA-256 verified on workstation andT500. **Pod safe to stop**;
no hardware termination performed.381GEN4checks pass;successor selected at
`/opt/gen4/current`. N97–119 now included in sharedN1..120registry.

"""+text[b:]
 text=re.sub(r'^history_entry: H\d+',f'history_entry: {entry}',text,count=1,flags=re.M)
 text=re.sub(r'^updated: .*','updated: 2026-09-26',text,count=1,flags=re.M)
 assert len(text.encode())<=32768,(fn,len(text.encode()))
 stage[fn]=text
(P/'authority_before').mkdir(exist_ok=True);(P/'authority_after').mkdir(exist_ok=True)
for fn in files:shutil.copy2(R/'SAM_LIVE'/fn,P/'authority_before'/fn)
history=f'''---
entry_id: {entry}
entry_date: 2026-09-26
entry_type: RESULT_INSTALLATION_AND_CUSTODY
status: IMMUTABLE_HISTORY
supersedes: H001726 installation counts; H001765 active joint campaign state
prior_entries: H001726, H001762, H001763, H001764, H001765
affects_live:
'''+''.join(f'  - SAM_LIVE/{f}\n' for f in files)+f'''---

# Shared packet/joint capabilities installed; final pod custody complete

Sean explicitly directed careful contribution analysis, upgrading and promoting
existing SLC/CE/GEN3/GEN4/SB/A3D41 capabilities, followed by downloading everything
needed before pod shutdown. The source-aware compiler, joint contracts, exact
native persistence and streaming design are Codex implementation contributions.

[Analysis](../../GEN4/spin_joint_install1/ANALYSIS.md),
[installed result](../../GEN4/spin_joint_install1/RESULT.md),
[promotion](../../GEN4/spin_joint_install1/PROMOTION.json),
[interface](../../GEN4/spin_joint_install1/GUIDE.md),
[coverage](../../GEN4/spin_joint_install1/DATA_COVERAGE.json),
[recovery](../../GEN4/spin_joint_install1/REPRODUCE.md).

## Prior state and replacement

The shared installation held99defaults/100source families and1692objects.
The separate exact atlas already completed allN1..120; its retained gap records
had not yet been installed in the general source registry. Packet/complete-graph
sources reached1408. Joint production was running toward750/900/1050.

The existing14spin operations are now extended with exact packet compilation,
joint E/M/ordered-boundary solving,uniform field/pair and boundary response,
fixed-M readout and native cached reuse.120canonical defaults/123source records
and1840native mathematical objects are installed. Prior defaults are unchanged.

369installed workstation checks and381GEN4 GPU/CPU checks pass. Both actual
VolumeII C4 source examples execute through A3D41. SB retains its N100 full DOS
and uses new joint endpoint responses. Both hosts pass12adoption checks.
Existing GEN4 ResearchMathematics consumes local N900 data and reuses its response
after reopening. Registry authentication:548global/419scoped files.
Global SLC-GEN3-R4/CEV1-R4 and scoped GEN4-P1/CE-P1 generations remain unchanged;
shared capability SHARED_SPIN_JOINT_V1 is promoted and adopted.

The corrected scoped capsule includes the shared dispatcher/source normalizer,
five-prime planner and47missing immutable prerequisite objects. Sealing restores
an inherited missing native binary from unchanged authenticated source and the
qualified requirements lock. Failed preparation/format checks and subsequent
successful results remain. No prior campaign runtime or canonical result is edited.

## Final scientific custody

There are8448complete graph sources through1408,54distinct completed dense
magnetization production cases, and24full joint production datasets:all six
family/fill combinations at120,300,750,900. Construction and solve coverage
remain separate. Packet continuations do not replace canonical frustrated sources.
The final joint run stops safely at2026-09-27T01:03:37.550796UTC after the lastN900
case;N1050 is not started.

4947research files/11,987,816,855bytes and3931upgraded-package files/1,081,883,305bytes
are SHA-256 verified on both workstation andT500:13,069,700,160bytes total.
Sean was informed the pod can be stopped;no hardware termination was performed.
All fresh local readouts use preserved data. Existing packet/dense graph custody
through1408 remains separately retained.

## Preserved boundaries

N100/N105 packet cases,connected-prefix alternatives and N96/N120 frustrated
lineage remain distinct. N105 is not relabeled prospective;the cause of the
historical N108 scheduling omission is not invented. Original models/timings keep
their backend scope. Physical units are supplied by source maps;SB history and
matter/carrier types remain. L-series,RH/training and Chalkboard pauses remain.
No autonomous follow-up campaign or MP computation/submission is started.

**The test result suggests strong contact with the concept.**

Prior live snapshots are under authority_before; replacements under authority_after.
'''
with (R/'SAM_HISTORY/entries'/name).open('x') as f:f.write(history)
for fn,text in stage.items():
 (R/'SAM_LIVE'/fn).write_text(text);(P/'authority_after'/fn).write_text(text)
with (R/'SAM_HISTORY/HISTORY_INDEX.md').open('a') as f:f.write(f'\n| {entry} | 2026-09-26 | RESULT_INSTALLATION_AND_CUSTODY | [Shared packet/joint spin upgrade and final pod custody](entries/{name}) | Existing SLC/CE/GEN3/4/SB/A3D41 upgraded;369/381checks;13.07GBtwo-copy custody |\n')
(P/'AUTHORITY.json').write_text(json.dumps(dict(entry=entry,history='SAM_HISTORY/entries/'+name,live_files=files),indent=2)+'\n')
print(entry,{fn:len(text.encode()) for fn,text in stage.items()})

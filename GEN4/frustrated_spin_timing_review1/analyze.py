"""Read-only timing extraction from completed, source-bound GEN4 training."""
from pathlib import Path
import csv,json,statistics
P=Path(__file__).resolve().parent;R=P.parent/'frustrated_spin_full96_training1/results/ram'
g=json.loads((R/'GROUPED_EXPERIENCE.json').read_text());m=json.loads((R/'MEASUREMENTS.json').read_text());spec=json.loads((R/'SPECIFICATIONS.json').read_text());rows=[]
for n in range(1,97):
 groups=[r for r in g if r['N']==n];best=min(groups,key=lambda r:r['median_ns']);fresh=next(r for r in groups if r['method']=='fresh_min_fill');p=spec[best['case']]['plan'];measurements=[r for r in m if r['case']==best['case']]
 assert int(statistics.median(r['total_ns'] for r in measurements))==best['median_ns']
 rows.append(dict(N=n,best_method=best['method'],best_method_median_seconds=best['median_ns']/1e9,best_method_repetitions=best['repetitions'],fresh_method_median_seconds=fresh['median_ns']/1e9,reduction_vs_fresh_percent=100*(1-best['median_ns']/fresh['median_ns']),all_training_solve_seconds=sum(r['total_ns'] for r in m if r['N']==n)/1e9,training_solve_count=sum(r['N']==n for r in m),width=p['selected']['width'],branches=p['selected']['branches'],weighted_entries=p['selected']['weighted_entries'],root_count=p['root_count'],primes=len(p['primes']),source_sha256=p['source_sha256']))
with (P/'TIMINGS.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(P/'TIMINGS.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['| N | Seconds | N | Seconds | N | Seconds | N | Seconds |','|---:|---:|---:|---:|---:|---:|---:|---:|']
for i in range(24):
 cells=[]
 for j in [i,i+24,i+48,i+72]:cells.extend([str(rows[j]['N']),f"{rows[j]['best_method_median_seconds']:.4f}"])
 lines.append('| '+' | '.join(cells)+' |')
table='\n'.join(lines);print(table)
report='''# N1–96 completion times and useful speed reductions

Read-only review of the completed GEN4 all-integer training. No new spin solves.
Numerical sources: ../frustrated_spin_full96_training1/results/ram/
GROUPED_EXPERIENCE.json, MEASUREMENTS.json and SPECIFICATIONS.json.

Times below are seconds for the fastest measured method at each N, using its
median where repeated. They cover a fresh exact spectrum and retained port
operators using warm prepared execution; they exclude initial source/plan
preparation, checkpoint writes, GPU warmup and historical T18 attachments.
N1..30 used CPU and N31..96 used GPU. The separate N1..30 incremental experiment
is not substituted into this table. TIMINGS.csv includes all-method training
solve totals, repeat counts, baseline comparisons, structure and source identity.
Best-method totals do not add up to the 251.115s complete training session.

'''+table+'''

## Comparisons

“Less than expected” is assessed against the measured fresh-min-fill baseline
on the same source, rather than an unfitted prediction from N alone.

| N | Fresh seconds | Best seconds | Reduction | Chosen method |
|---:|---:|---:|---:|---|
'''
for n in [85,86,91,92,93,96]:
 r=rows[n-1];report+=f"| {n} | {r['fresh_method_median_seconds']:.4f} | {r['best_method_median_seconds']:.4f} | {r['reduction_vs_fresh_percent']:.1f}% | {r['best_method']} |\n"
report+='''
N91/N92 transferred ordering gives width18 instead of22; weighted output work
falls from479690496 to63801600 and433732736 to74167936 respectively. This explains
the large arithmetic-time reduction. These full96 comparisons each have one
sample per distinct plan; they identify promising cases for repeat timing.

N96 takes8.4739s compared withN95's9.2403s andN94's9.3844s:8.3% and9.7% lower.
N96's selected plan requires430070400weighted output entries againstN95's
513524864, a16.3% reduction in this structural work measure. The separate
three-repeat ladder campaign also measures anN96portfolio median8.0354s against
11.0346s fresh,27.2% lower.

N41..61 is a broad plateau: selected times stay roughly0.35–0.38s while source
size increases. N62 doubles the transform length256→512 and rises to0.7151s;
N90 doubles512→1024 and the conditioning branches16→32, rising to2.9761s.
The concrete execution changes explain these steps better than N alone.

N18,N34,N40 have downward adjacent-time changes20.1%,17.3%,31.4%. Their selected
widths stay3 and structural work increases. First-run records locate these drops
mainly in reconstruction: N17→18 is98.43→79.73ms;N33→34 is207.79→167.08ms;
N39→40 is261.25→167.11ms. These observations indicate timing overhead variation,
not a detected structural simplification of those particular sources.

Helpful next-target information: N91/N92 provide the largest observed benefit
from transferred ordering; N85/N86 show strong portfolio gains. Components,
elimination width, branches and retained boundary determine reusable work for
these explicit graphs. The measurements do not establish a universal ranking
of the integers independently of their source graph.
'''
(P/'REVIEW.md').write_text(report)

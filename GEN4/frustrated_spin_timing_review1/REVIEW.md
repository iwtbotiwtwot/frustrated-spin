# N1–96 completion times and useful speed reductions

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

| N | Seconds | N | Seconds | N | Seconds | N | Seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.0010 | 25 | 0.1605 | 49 | 0.3675 | 73 | 0.7281 |
| 2 | 0.0017 | 26 | 0.1614 | 50 | 0.3655 | 74 | 0.7385 |
| 3 | 0.0057 | 27 | 0.1614 | 51 | 0.3735 | 75 | 0.7441 |
| 4 | 0.0112 | 28 | 0.1607 | 52 | 0.3696 | 76 | 0.7457 |
| 5 | 0.0113 | 29 | 0.1607 | 53 | 0.3705 | 77 | 0.7758 |
| 6 | 0.0211 | 30 | 0.1664 | 54 | 0.3727 | 78 | 0.7810 |
| 7 | 0.0210 | 31 | 0.1832 | 55 | 0.3662 | 79 | 0.7821 |
| 8 | 0.0414 | 32 | 0.1851 | 56 | 0.3575 | 80 | 0.8088 |
| 9 | 0.0406 | 33 | 0.2346 | 57 | 0.3775 | 81 | 0.8351 |
| 10 | 0.0421 | 34 | 0.1941 | 58 | 0.3730 | 82 | 0.8298 |
| 11 | 0.0411 | 35 | 0.1947 | 59 | 0.3738 | 83 | 0.8661 |
| 12 | 0.0819 | 36 | 0.2010 | 60 | 0.3750 | 84 | 0.9380 |
| 13 | 0.0811 | 37 | 0.1884 | 61 | 0.3766 | 85 | 0.9377 |
| 14 | 0.0800 | 38 | 0.1961 | 62 | 0.7151 | 86 | 0.9177 |
| 15 | 0.0810 | 39 | 0.2923 | 63 | 0.7339 | 87 | 1.0155 |
| 16 | 0.0819 | 40 | 0.2006 | 64 | 0.7466 | 88 | 1.2820 |
| 17 | 0.1010 | 41 | 0.3619 | 65 | 0.7572 | 89 | 1.3552 |
| 18 | 0.0807 | 42 | 0.3592 | 66 | 0.7091 | 90 | 2.9761 |
| 19 | 0.0808 | 43 | 0.3572 | 67 | 0.7467 | 91 | 3.1968 |
| 20 | 0.0828 | 44 | 0.3637 | 68 | 0.7242 | 92 | 3.1562 |
| 21 | 0.0825 | 45 | 0.3690 | 69 | 0.7273 | 93 | 5.5756 |
| 22 | 0.0828 | 46 | 0.3715 | 70 | 0.7281 | 94 | 9.3844 |
| 23 | 0.0826 | 47 | 0.3689 | 71 | 0.7268 | 95 | 9.2403 |
| 24 | 0.0833 | 48 | 0.3743 | 72 | 0.7349 | 96 | 8.4739 |

## Comparisons

“Less than expected” is assessed against the measured fresh-min-fill baseline
on the same source, rather than an unfitted prediction from N alone.

| N | Fresh seconds | Best seconds | Reduction | Chosen method |
|---:|---:|---:|---:|---|
| 85 | 1.6547 | 0.9377 | 43.3% | tie_portfolio |
| 86 | 1.6439 | 0.9177 | 44.2% | tie_portfolio |
| 91 | 8.8003 | 3.1968 | 63.7% | transition_priority |
| 92 | 7.4853 | 3.1562 | 57.8% | transition_priority |
| 93 | 8.4750 | 5.5756 | 34.2% | tie_portfolio |
| 96 | 11.2515 | 8.4739 | 24.7% | tie_portfolio |

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

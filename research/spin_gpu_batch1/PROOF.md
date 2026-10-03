# General selected-window extraction

The retained exact source and modular algorithm are unchanged from
../spin_gpu_coeff1/PROOF.md and ../spin_gpu_coeff2/REPORT.md.
For N=20+30m, the chain polynomial is

    Q_b(X,U)=R_b(X,U) A(X,U)^m B(X,U)^(4m+1)(1+X)^(18m+3).

For every requested k,d, root contraction is

    g_b(k,d)=sum_(a,r,v in R_b) v*[X^(k-a) U^(d-r)] H(X,U),

where H is the product of the non-root factors. Taking the union of these
shifted coordinate requests lets every modular transform serve the whole batch.
Every term has a nonnegative integer coefficient. The total mass of H remains
2^(N-15), independent of how many coefficients are requested. Thus the same
CRT product bound used by the predecessor suffices for every batch member.

The Kronecker stride N-14 exceeds deg_X H=N-15; the padded transform exceeds
the encoded product degree. All modulus arithmetic and reconstruction remain
exact. Batching changes only transferred indices and root contractions; it
does not reduce the modular transform length or number of prime moduli.

For general k, M=2k-N and original energy is

    E=14m+8-4d-((2k-N)^2-N)/2.

Global reversal is g_b(k,d)=g_(b xor15)(N-k,d). Symmetric k windows allow
that identity to be checked on every produced record. The independent CPU
recurrence remains the seven-step polynomial identity documented in
../spin_coeff3/PROOF.md, with all division remainders checked. It evaluates
the same generalized root contraction after constructing coefficients by a
different powering algorithm, without modular GPU arithmetic.

The benchmark d center floor((7m+4)/2) is the zero-coupling defect center.
It is not generally the finite-temperature peak. The companion normalization
study evaluates the probability of this selected window against complete Z.

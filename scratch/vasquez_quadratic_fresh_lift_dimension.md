# Vasquez Bridge — quadratic fresh-variable lift by nonlinear dimension

Status: `QUADRATIC_BRANCH_CLOSED_BY_DIMENSION`

Let

\[
LS(h):=\{u: D_u h\text{ is constant}\}
\]

be the linear-structure subspace of a Boolean function `h` on `n` variables, and define

\[
\dim_{nl}(h):=n-\dim LS(h).
\]

This is the same invariant computed by `dim_invariant` in the existing ZLG verifier code.

## Lemma 1 — k ANDs imply nonlinear dimension at most 2k

Suppose `h` is computed by a triangular XOR/AND circuit with `k` AND gates

\[
a_i=(\ell_i(x)+c_i+\sum_{j<i}\alpha_{ij}a_j)
    (r_i(x)+d_i+\sum_{j<i}\beta_{ij}a_j),
\]

followed by an affine output in `(x,a_1,...,a_k)`, where `ell_i,r_i` are linear forms in the original inputs.

Let

\[
K=\bigcap_{i=1}^k\ker\ell_i\cap\ker r_i.
\]

For `u in K`, induction on the triangular gates shows

\[
a_i(x+u)=a_i(x)
\]

for every `i`: the fresh input-linear parts of both factors are unchanged, and all earlier gate values are unchanged. Therefore the final output changes only by its affine input term, so `D_u h` is constant. Hence

\[
K\subseteq LS(h).
\]

The `2k` linear forms `ell_i,r_i` have rank at most `2k`, so

\[
\dim K\ge n-2k.
\]

Thus

\[
\boxed{\dim_{nl}(h)\le 2k.}
\]

In particular

\[
\boxed{MC(h)\ge \left\lceil\frac{\dim_{nl}(h)}2\right\rceil.}
\]

## Lemma 2 — nonlinear dimension of zf for quadratic f

Let `f(x)` be a nonlinear quadratic Boolean function on `n` variables. Let its quadratic part have associated alternating bilinear form of rank `2r`.

Set

\[
g(z,x)=z f(x),
\]

where `z` is fresh.

For a direction `(a,u) in F_2 x F_2^n`,

\[
D_{(a,u)}g(z,x)
= z\big(f(x)+f(x+u)\big)+a f(x+u).
\]

If this derivative is constant and `a=1`, its coefficient of `z` must vanish, so `D_u f=0`; then the derivative equals `f(x+u)`, which is nonconstant because `f` is nonlinear. Contradiction. Therefore every linear structure has `a=0`.

For `a=0`, constancy forces

\[
zD_u f(x)\equiv0,
\]

so `D_u f=0` identically.

Hence

\[
LS(g)=\{0\}\times Z(f),\qquad Z(f):=\{u:D_u f=0\}.
\]

For quadratic `f`, if `D_u f=0` then the linear part of that derivative vanishes, so `u` lies in the radical of the quadratic alternating form. Since that radical has dimension `n-2r`,

\[
\dim Z(f)\le n-2r.
\]

Therefore

\[
\dim_{nl}(zf)
=(n+1)-\dim Z(f)
\ge 2r+1.
\]

So

\[
MC(zf)\ge
\left\lceil\frac{2r+1}{2}\right\rceil
=r+1.
\]

## Quadratic fresh-variable lift theorem

Mirwald-Schnorr characterize the multiplicative complexity of a quadratic Boolean function as half the rank of its associated alternating matrix, so

\[
MC(f)=r.
\]

Computing `f` with `r` ANDs and then multiplying once by the fresh variable `z` gives

\[
MC(zf)\le r+1.
\]

Together with the dimension lower bound,

\[
\boxed{MC(zf)=MC(f)+1}
\]

for every nonlinear quadratic Boolean function `f`.

This closes the entire quadratic branch, not only `MC(f)=2` or `MC(f)=3`.

## Why the exterior-rank route is no longer needed here

A general three-AND function can have cubic exterior rank three, so the proposed blanket inequality

\[
R_\wedge(T_3(h))\le MC(h)-1
\]

is false at `MC(h)=3`.

The nonlinear-dimension argument avoids that false generalization and uses the special fresh-variable structure directly.

## Boundary

```text
QUADRATIC_F_NONLINEAR := yes
RANK_Q := 2r
MC_F := r
DIM_NL_ZF_LOWER := 2r+1
MC_ZF_LOWER := r+1
MC_ZF_UPPER := r+1
QUADRATIC_FRESH_LIFT := CLOSED
GENERAL_NONQUADRATIC_FRESH_LIFT := not implied
P_NE_NP_PROVED := no
```

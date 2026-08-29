# Vasquez Bridge — first shared-gate incompatibility and accumulation boundary

Status: `LOCAL_INCOMPATIBILITY_VERIFIED_GLOBAL_INVARIANT_RETIRED`

## Exact SAT selector gadget

Use Boolean inputs `(w,s1,s2,s3)` to encode the selector-CNF over existential variable `x`

\[
(\neg s_1\vee x)\wedge
(w\vee\neg s_2\vee\neg x)\wedge
(\neg w\vee\neg s_3\vee\neg x).
\]

Its satisfiability predicate is

\[
F(w,s)=1+s_1\big((1+w)s_2+w s_3\big).
\]

Hence

\[
F(0,s)=1+s_1s_2,\qquad F(1,s)=1+s_1s_3.
\]

Each restriction has multiplicative complexity one.

## Shared one-gate incompatibility

A one-AND circuit over four inputs has the form

\[
A(x)B(x)+C(x)
\]

with affine `A,B,C`. There are exactly

\[
32\cdot32\cdot64=65536
\]

parameter choices if the output coefficient of the gate is included explicitly.

The verifier `scratch/vasquez_bridge_pair_quadratic.py` exhausts all of them and finds zero realizations of `F`.

There is an explicit two-AND realization:

\[
g_1=(1+w)(s_2+s_3),
\]

\[
g_2=(1+s_1)(1+s_3+g_1),
\]

\[
F=s_1+s_3+g_1+g_2.
\]

Therefore

\[
MC(F)=2.
\]

This is the first exact Vasquez-Bridge witness that two individually one-AND SAT residuals can require two ANDs when forced into one shared circuit.

The obstruction is basis-independent at one gate: the two restricted quadratic forms are distinct,

\[
q_0=s_1s_2,\qquad q_1=s_1s_3.
\]

An invertible shared linear change of free variables acts injectively on quadratic forms, so it cannot make `q_0=q_1`. A single shared AND has one homogeneous quadratic product, hence cannot produce both restrictions.

## Why quadratic diversity does not close the P-vs-NP bridge

The local effect is real but does not accumulate fast enough under the naive invariant "dimension of the span of restricted quadratic parts."

If a global function `G(y,w)` has algebraic degree at most `D`, then after restricting `w=rho`, the coefficient of each quadratic monomial `y_i y_j` is a Boolean polynomial in `rho` of degree at most `D-2`. Thus the span of all restricted quadratic forms is controlled by the space of `w`-monomials of degree at most `D-2`.

A `k`-AND circuit has the coarse degree bound

\[
\deg G\le 2^k.
\]

Therefore the restricted-quadratic coefficient patterns can already occupy a space as large as

\[
\sum_{d=0}^{2^k-2}\binom{r}{d}
\]

when `r` variables are restricted. This grows too quickly with `k` for quadratic-span diversity to force a superpolynomial lower bound. In particular, once `2^k` reaches a constant fraction of `r`, the bound can approach the full `2^r` coordinate space while `k=O(\log r)`.

So the exact pair incompatibility is retained, but **quadratic-form diversity is retired as the global bridge invariant**.

## Interpretation

The two-coordinate gadget is another manifestation of the same local phenomenon seen in fresh-variable lift work: changing a control slice can force one additional multiplication. An additive one-gate penalty per control level is structurally meaningful but cannot by itself turn polynomial multiplicative complexity into superpolynomial multiplicative complexity.

A successful Vasquez Bridge invariant must therefore detect incompatibility that accumulates much faster than algebraic degree permits a small number of gates to absorb.

```text
LOCAL_SHARED_INCOMPATIBILITY := verified
RESTRICTED_MC := 1 on each of the two slices
GLOBAL_MC := 2
SHARED_BASIS_ESCAPE := no at k=1
QUADRATIC_DIVERSITY_INVARIANT := retired for asymptotic bridge
P_NE_NP_PROVED := no
```

## Next bounded action

Move one level above homogeneous quadratic diversity. Test whether the **factorization type itself** of several residual slices has a shared-gate compatibility invariant that is stable under higher-degree terms and whose capacity grows only polynomially per AND gate. Retire it immediately if a `k`-gate circuit can realize exponentially many factorization types through restricted higher-degree monomials.

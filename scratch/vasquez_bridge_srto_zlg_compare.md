# Vasquez Bridge — SRTO versus current ZLG sibling algebra

Status: `SHARED_BUNDLE_OBSTRUCTION_IDENTIFIED`

## Child bundle in zero/leak notation

For two child computations of one SAT split, write

\[
F(z,y)=P(y)+z\,p(y),
\]

so

\[
C_0=P,\qquad C_1=P+p.
\]

The SAT parent value is

\[
C_{parent}=C_0\lor C_1=P+p+Pp.
\]

Define

\[
\Omega(P,p):=P+p+Pp.
\]

## What the current level-5 sibling theorem controls

The existing level-5 sibling-exchange audit studies two late gate products

\[
PQ,\qquad UV
\]

with collision condition

\[
PQ+UV\in S_3,
\]

and product leakage

\[
\Theta(P,p;Q,q)=Pq+Qp+pq.
\]

Those verified sectors classify **shared gate-product collisions**. They do not directly classify the output-level SAT relation `Omega(P,p)`.

## Exact OR-Absorption(1) result

For one control bit and three free variables, the exhaustive verifier `vasquez_bridge_or_absorption1.py` enumerates every distinct one-AND shared bundle `F(z,y)`.

It finds

```text
child_bundle_functions = 1152
distinct_parent_or_functions = 128
mc1_parent_universe = 128
failures = 0
```

Hence every shared one-AND bundle satisfies

\[
MC(\Omega(P,p))\le1.
\]

So `OR-Absorption(1)` is completely closed: once the two restrictions really come from one shared one-AND bundle, the sibling OR costs no additional multiplication.

## Correct interpretation of the selector gadget

The selector-CNF in `vasquez_bridge_pair_quadratic.py` has slices

\[
C_0=1+s_1s_2,\qquad C_1=1+s_1s_3.
\]

Each slice separately has multiplicative complexity one, but exhaustive search over all 65,536 one-AND circuits for the four-variable controlled bundle finds no shared one-AND realization. There is an explicit two-AND realization, so the **shared bundle** has exact multiplicative complexity two.

Its sibling OR is

\[
C_0\lor C_1=1+s_1s_2s_3,
\]

which also has multiplicative complexity two.

Therefore this gadget is not a failure of `OR-Absorption(1)`. The obstruction occurs earlier: the two individually simple slices require incompatible factor choices and cannot be packed into one shared one-AND DAG.

## Revised finite bridge object

The first useful local quantity is therefore

> **Shared Restriction Complexity:** the minimum number of AND gates required by one circuit whose control slices realize a prescribed tuple of residual SAT functions.

The existing sibling-exchange work is relevant precisely because it studies when apparently different restricted gate products can be represented, exchanged, or absorbed inside one shared triangular DAG.

The local SAT question is not merely whether `Pp` can be absorbed after the child bundle is built. It is whether the child restrictions themselves can share the same small gate factorization while also satisfying the parent self-reduction identity.

## Asymptotic barrier

A constant penalty for one incompatible sibling pair is not enough for `P != NP`. The needed theorem must show that incompatible shared factorizations accumulate across SAT's self-reduction system faster than any polynomial-width triangular DAG can absorb them.

Fixed-degree slice invariants are especially suspect: higher-degree monomials in restricted variables can collapse to low-degree terms after restriction and generate many apparent quadratic/factorization types from a small circuit.

```text
BACKWARD_FRONTIER := SAT Self-Reduction Triangular Obstruction (SRTO)
CURRENT_ZLG_OBJECT := shared gate-product collision/absorption
OR_ABSORPTION_1 := closed; 1152/1152 shared one-AND bundles remain one-AND after sibling OR
SELECTOR_GADGET := individual slices MC=1; shared bundle MC=2; parent OR MC=2
MISSING_LOCAL_OBJECT := shared-restriction factorization incompatibility at growing k
MISSING_ASYMPTOTIC_OBJECT := accumulation of those incompatibilities across SAT self-reduction
P_NE_NP_PROVED := no
```

## Next bounded action

Do not jump directly to `OR-Absorption(5)`. First classify **Shared-Restriction(1)** symbolically: characterize exactly when two MC<=1 slice functions can be packed into one shared one-AND controlled function. Extract the invariant from the distinct homogeneous quadratic parts, then test whether its natural higher-`k` generalization is immediately defeated by higher-degree restriction collapse. Only a surviving invariant should be lifted to the existing level-5 sibling database.

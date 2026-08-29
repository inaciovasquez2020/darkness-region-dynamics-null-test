# Vasquez Bridge — SRTO versus current ZLG sibling algebra

Status: `MISSING_COUPLING_TERM_IDENTIFIED`

## Child bundle in zero/leak notation

For two child computations of one SAT split, write

\[
F(z,y)=P(y)+z\,p(y),
\]

so

\[
C_0=P,\qquad C_1=P+p.
\]

The SAT parent value is the OR of the children:

\[
C_{parent}=C_0\lor C_1.
\]

Over the Boolean ring,

\[
C_{parent}
=P+(P+p)+P(P+p)
=P+p+Pp.
\]

Define the output-level OR aggregator

\[
\Omega(P,p):=P+p+Pp.
\]

The new nonlinear term demanded by SAT self-reduction is therefore the **output zero/leak product** `Pp`.

## What the current level-5 sibling theorem controls

The existing level-5 sibling-exchange audit starts from two late gate products

\[
PQ,\qquad UV
\]

with collision condition

\[
PQ+UV\in S_3.
\]

For full zero/leak gate factors `(P,p)` and `(Q,q)`, product leakage is

\[
\Theta(P,p;Q,q)=Pq+Qp+pq.
\]

The verified common-factor, zero-fiber, and labelled absorption closures classify sectors of this **gate-product collision** problem.

They do not directly classify the SAT self-reduction condition

\[
C_{parent}=\Omega(P,p)=P+p+Pp,
\]

because `P` and `p` here are the zero and leak components of the **whole child output bundle**, not two affine factors of one late multiplication gate.

Therefore the existing level-5 closures cannot currently be cited as proving even one nontrivial instance of the SAT Self-Reduction Triangular Obstruction.

## Missing finite theorem: OR absorption

Suppose a shared triangular child circuit uses `k` AND gates and has output pair `(P,p)`. Computing `Omega(P,p)` naively requires one additional AND for `Pp`.

A parent circuit of the same width `k` can satisfy SAT self-reduction only if this product is **absorbed** into the existing shared DAG: it must be expressible using the existing gate outputs and affine wiring, or a gate exchange must replace an existing multiplication without increasing width.

Thus the finite local bridge problem is:

> **OR-Absorption(k).** Classify all output pairs `(P,p)` obtainable from a `k`-AND shared triangular circuit for which `Omega(P,p)` also has a realization of width at most `k` compatible with the same restriction structure.

A fail-closed verifier for small `k` can reuse the zero/leak pair multiplication law

\[
(a,b)(c,d)=(ac,ad+bc+bd)
\]

but must track the final output pair, not only late gate factor planes.

## Additive barrier

Even a theorem saying every nondegenerate SAT split forces

\[
MC(C_{parent})\ge MC(child\ bundle)+1
\]

would yield only an additive cost along a root-to-leaf chain. With `n` logical variables this gives at most an `Omega(n)` style lower bound, which is still polynomial.

Therefore SRTO needs two layers:

1. **local OR absorption:** characterize when one split can avoid the extra multiplication;
2. **global incompatibility accumulation:** prove that a polynomial-width shared DAG cannot realize the required absorption choices simultaneously across the exponentially branching SAT self-reduction system.

The second layer is the true asymptotic bridge.

## Exact relation to the verified two-slice gadget

The selector-CNF in `vasquez_bridge_pair_quadratic.py` has child slices

\[
C_0=1+s_1s_2,\qquad C_1=1+s_1s_3.
\]

Their OR is

\[
C_0\lor C_1=1+s_1s_2s_3,
\]

which has multiplicative complexity two. Each child has multiplicative complexity one. This is an exact finite example of a non-absorbed sibling OR costing one additional multiplication.

It validates the local phenomenon but also illustrates the additive barrier.

```text
BACKWARD_FRONTIER := SAT self-reduction triangular obstruction (SRTO)
CURRENT_ZLG_OBJECT := late-gate product collision PQ+UV in S3 with leakage Theta
MISSING_LOCAL_OBJECT := output-level product Pp in Omega(P,p)=P+p+Pp
NEXT_FINITE_THEOREM := OR-Absorption(k)
NEXT_ASYMPTOTIC_THEOREM := incompatible OR absorptions accumulate across the shared SAT split DAG
P_NE_NP_PROVED := no
```

## Next bounded action

Build `OR-Absorption(1)` exactly first. Enumerate all one-AND output pairs under one control restriction, classify which pairs have `MC(Omega(P,p)) <= 1`, and isolate the minimal non-absorbed classes. Compare their invariant with the verified quadratic selector gadget. Only then decide whether extending the classifier to `k=2` or `k=5` is structurally useful.

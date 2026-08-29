# Vasquez Bridge — exact uniform boundary for P vs NP

Status: `BACKWARD_FRONTIER_WEAKENED_EXACTLY`

## Fixed SAT encoding

Let `SAT_N : {0,1}^N -> {0,1}` be a fixed reasonable length-`N` Boolean encoding of SAT instances.

A triangular XOR/AND circuit with `k` AND gates is specified by

\[
a_i=L_i(x,a_{<i})R_i(x,a_{<i}),\qquad i=1,\dots,k,
\]

with affine `L_i,R_i`, followed by an affine output in `(x,a_1,...,a_k)`.

For `k = poly(N)`, the dense coefficient description has length

\[
O(kN+k^2),
\]

so both description size and evaluation time are polynomial.

## Uniform Triangular SAT condition

Define `UTS` to mean:

> There exist a polynomial `p` and a deterministic polynomial-time generator `G` such that, on input `1^N`, `G` outputs a triangular XOR/AND circuit `C_N` with at most `p(N)` AND gates and `C_N = SAT_N` on all `N`-bit inputs.

Then

\[
UTS \Longleftrightarrow SAT\in P.
\]

### `UTS -> SAT in P`

Given an input `x` of length `N`, run `G(1^N)` and evaluate the resulting triangular circuit on `x`. The generator, circuit description, and evaluation are all polynomial in `N`.

### `SAT in P -> UTS`

A deterministic polynomial-time SAT machine can be unrolled uniformly into polynomial-size Boolean circuits. Replace

\[
\neg a = 1+a,
\qquad
 a\lor b = a+b+ab
\]

over `F_2`; AND gates remain AND gates. Topologically order the multiplication gates and absorb all XOR/constant wiring into affine gate inputs and the affine output. This gives a polynomial-time-generated triangular XOR/AND family with polynomially many AND gates.

Since SAT is NP-complete,

\[
P=NP \Longleftrightarrow SAT\in P \Longleftrightarrow UTS.
\]

Therefore the exact backward target for the Vasquez Bridge may be weakened from a nonuniform superpolynomial multiplicative-complexity lower bound to:

> **Uniform Triangular Obstruction (UTO):** no polynomial-time generator produces a polynomial-width triangular XOR/AND family computing all `SAT_N`.

Thus

\[
UTO \Longleftrightarrow P\ne NP.
\]

This is strictly weaker than proving `MC(SAT_N)=N^{omega(1)}`, which would rule out nonuniform polynomial circuits as well.

## Consequence for the forward program

The finite ZLG/lift classifications constrain individual circuit structures. Uniformity alone does **not** imply that `C_N` and `C_{N+1}` have compatible gates, common bases, nested topology, or any other structural coherence: a polynomial-time generator may output a completely different circuit at every length.

So a bridge from finite local ZLG constraints to `UTO` needs a **generator-level** statement, not merely more fixed-`k` exclusions.

A sufficient form would be an extraction theorem:

> From the code of any polynomial-time triangular-circuit generator `G`, compute in polynomial time infinitely many lengths `N` and polynomial-size certificates exposing a verifier-backed forbidden local configuration in `G(1^N)` if those circuits claim to compute `SAT_N`.

No such extraction theorem is proved here. The point is to identify the exact missing scale: the bridge must constrain the uniform generator across unbounded input lengths, or directly diagonalize against it, while keeping the diagonal construction inside SAT/NP.

## Boundary

```text
FIXED_TARGET := P != NP
OLD_BACKWARD_TARGET := MC(SAT_N)=N^{omega(1)}  [sufficient but stronger than needed]
NEW_BACKWARD_TARGET := Uniform Triangular Obstruction (UTO)
UTO_EQUIVALENT_TO_P_NE_NP := yes, for fixed reasonable SAT encoding
FINITE_ZLG_ALONE_IMPLIES_UTO := no known implication
MISSING_OBJECT := generator-level scalable obstruction / NP-safe diagonal extraction
P_NE_NP_PROVED := no
```

## Next bounded action

Work backward one more step from `UTO`: characterize the weakest polynomial-time-checkable failure certificate for a claimed uniform SAT circuit generator. Separate false-negative certificates (satisfiable formula rejected, NP-witnessable) from false-positive certificates (unsatisfiable formula accepted, not known NP-witnessable). Determine whether the asymmetry can be converted into a two-sided generator contradiction using the triangular/ZLG structure without assuming `NP=coNP`.

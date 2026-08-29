# Vasquez Bridge — SAT self-reduction meeting point

Status: `BACKWARD_FORWARD_MEETING_POINT_IDENTIFIED_NOT_CLOSED`

## 1. Uniform failure certificates without NP=coNP

Let `C_N` be a claimed polynomial-time-generated triangular XOR/AND circuit for the length-`N` SAT predicate.

A direct false negative is NP-witnessable: a formula `phi` with `C_N(phi)=0` plus a satisfying assignment.

A direct false positive `C_N(phi)=1` with `phi` unsatisfiable is not known to have an NP witness. This apparent asymmetry can be avoided by using SAT self-reduction rather than semantic unsatisfiability certificates.

## 2. SAT self-reduction identity

For a CNF formula `phi` with a chosen logical variable `x`, let

\[
\phi_0=\operatorname{simp}(\phi|_{x=0}),\qquad
\phi_1=\operatorname{simp}(\phi|_{x=1}).
\]

With canonical padding/encoding maps `R_0,R_1` into the appropriate length classes,

\[
SAT(\phi)=SAT(\phi_0)\lor SAT(\phi_1).
\]

Over `F_2`,

\[
a\lor b=a+b+ab.
\]

Hence every correct SAT circuit family must satisfy

\[
C_N(\phi)
=
C_{N_0}(R_0\phi)
+
C_{N_1}(R_1\phi)
+
C_{N_0}(R_0\phi)C_{N_1}(R_1\phi)
\]

for every valid parent formula and chosen splitting variable.

## 3. Any incorrect family has a local structural witness

Assume the circuit family is correct on the trivial base formulas (empty satisfied formula and explicit contradiction) and satisfies the self-reduction identity at every non-base formula.

Induct on the number of remaining logical variables (with formula-size/encoding padding as a secondary well-founded measure). The base values agree with SAT. At a non-base formula, both children have smaller measure, so by induction their circuit values equal their SAT values. The self-reduction identity then forces the parent circuit value to equal SAT as well.

Therefore:

> If a family differs from SAT anywhere, then either a base case is wrong or there exists a parent formula/splitting variable where the self-reduction identity fails.

Such a failure is polynomial-time checkable from the circuit descriptions and the formula alone. No unsatisfiability certificate is needed.

## 4. Equivalent uniform obstruction target

For polynomial-time-generated polynomial-width triangular circuit families, the following are equivalent:

1. the family computes SAT;
2. it has the correct base values and satisfies every canonical SAT self-reduction identity.

Thus `P != NP` is equivalent to the nonexistence of a polynomial-time-generated polynomial-width triangular family satisfying this entire self-reduction consistency system.

Call this the **SAT Self-Reduction Triangular Obstruction (SRTO)**.

## 5. Connection to the existing sibling machinery

For one fixed parent circuit, composing with `R_0` and `R_1` gives two restricted child computations produced by the **same triangular DAG and the same gate parameters**. This is exactly the shared-restriction setting.

The parent consistency law is

\[
P=C_0+C_1+C_0C_1.
\]

The only nonlinear coupling between the sibling child values is their product `C_0 C_1`.

This is structurally aligned with the existing ZLG/sibling program:

- two slices/restrictions of one shared triangular circuit;
- common-prefix gate parameters;
- collision/absorption questions between sibling products;
- zero/leak pair algebra for tracking how one control restriction changes gate outputs.

The existing finite level-5 sibling results do **not** yet prove SRTO, but SRTO supplies a concrete reason to study sibling incompatibility: not as isolated finite case enumeration, but as the local consistency condition that must be satisfied at every node of the SAT self-reduction tree.

## 6. New exact bridge

```text
FIXED_TARGET := P != NP
BACKWARD_FRONTIER := SRTO
FORWARD_FRONTIER := verified shared-sibling / zero-leak gate algebra
MEETING_OBJECT := parent = child0 OR child1 = child0 + child1 + child0*child1
MISSING_THEOREM := polynomial-width shared triangular DAGs cannot satisfy all SAT self-reduction sibling identities uniformly across all depths
FALSE_POSITIVE_CERTIFICATE_PROBLEM := removed by self-reduction consistency
P_NE_NP_PROVED := no
```

## 7. Next bounded action

Translate one canonical SAT split into the repository's zero/leak pair notation. Treat the split bit as the control variable `z`, write every gate as `A_i + z B_i`, and derive the exact condition imposed by

\[
C_{parent}=C_0+C_1+C_0C_1.
\]

Then compare that condition with the already-certified sibling collision/absorption sectors. The goal is to identify whether the current level-5 local theorem is actually a finite instance of the SRTO consistency law or whether an additional coupling term is missing.

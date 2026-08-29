#!/usr/bin/env python3
from collections import Counter
from itertools import combinations, product

from zlg_mc5_sibling_collision_census import BITS, plane_residual
from zlg_mc5_sibling_kernel import (
    ONE,
    VARS,
    make_reducer,
    subspace2_key,
    topology,
)
from zlg_mc5_sibling_orbit_quotient import orbit, pair_key


def local_eval(f, X, Y):
    c, x, y, a = f
    A = X & Y
    return c ^ (x & X) ^ (y & Y) ^ (a & A)


def local_mul(f, g):
    """Multiply in span{1,X,Y,A} with A=XY over the Boolean ring."""
    c, x, y, a = f
    d, u, v, b = g
    return (
        c & d,
        (c & u) ^ (x & d) ^ (x & u),
        (c & v) ^ (y & d) ^ (y & v),
        (c & b)
        ^ (a & d)
        ^ (x & v)
        ^ (y & u)
        ^ (x & b)
        ^ (a & u)
        ^ (y & b)
        ^ (a & v)
        ^ (a & b),
    )


def verify_local_algebra():
    # This is stronger than checking only the seven factor planes: arbitrary
    # constant sibling labels turn every factor into an arbitrary element of
    # span{1,X,Y,A}.  Closure of this full 4D algebra therefore handles every
    # compatible labelled factor choice in a zero-fiber gate block.
    products = 0
    truth_cases = 0
    for f in product((0, 1), repeat=4):
        for g in product((0, 1), repeat=4):
            h = local_mul(f, g)
            products += 1
            for X, Y in product((0, 1), repeat=2):
                assert local_eval(h, X, Y) == (
                    local_eval(f, X, Y) & local_eval(g, X, Y)
                ), (f, g, h, X, Y)
                truth_cases += 1
    assert products == 256
    assert truth_cases == 1024
    return products, truth_cases


def block_support(key):
    hits = []
    for block in range(3):
        mask = 7 << (3 * block)
        if all((v & ~mask) == 0 for v in key):
            hits.append(block)
    assert len(hits) == 1, (key, hits)
    return hits[0]


def main():
    products, truth_cases = verify_local_algebra()

    gates = topology(BITS)
    S3 = [ONE] + VARS + [g[2] for g in gates]
    reducer = make_reducer(S3)

    block_basis = []
    for X, Y, a in gates:
        block_basis.extend([X, Y, a])
    assert len(block_basis) == 9

    planes = {}
    for p in range(1, 1 << 9):
        for q in range(p + 1, 1 << 9):
            key = subspace2_key(p, q)
            planes.setdefault(key, (p, q))
    assert len(planes) == 43435

    zero = []
    support = {}
    for key in planes:
        if plane_residual(key, block_basis, reducer) != 0:
            continue
        zero.append(key)
        support[key] = block_support(key)

    assert len(zero) == 21
    assert Counter(support.values()) == Counter({0: 7, 1: 7, 2: 7})

    # Two distinct 2-planes in one 3D F2 block always meet in a nonzero
    # direction.  Hence every disjoint zero-fiber pair must use two distinct
    # gate blocks.  Each sibling product is then contained in the local algebra
    # of its own already-computed prefix gate and needs no new AND.
    disjoint = []
    for A, B in combinations(zero, 2):
        if set(A) & set(B):
            continue
        assert support[A] != support[B], (A, B, support[A], support[B])
        disjoint.append(pair_key(A, B))

    assert len(disjoint) == 147
    assert len(set(disjoint)) == 147

    orbit_by_rep = {}
    disjoint_set = set(disjoint)
    for p in disjoint:
        o = orbit(p)
        assert o <= disjoint_set
        rep = min(o)
        orbit_by_rep.setdefault(rep, o)
        assert orbit_by_rep[rep] == o

    assert len(orbit_by_rep) == 75
    orbit_size_dist = Counter(len(o) for o in orbit_by_rep.values())
    assert orbit_size_dist == Counter({1: 27, 2: 36, 4: 12})

    # At slice 1, a factor supported in block i is an element of
    # span{1, X_i~, Y_i~, a_i~}, where a_i~=X_i~Y_i~ is already the ith prefix
    # AND.  verify_local_algebra proves each sibling product stays in that span.
    # The zero-slice correction lies in S3, whose lifted value is affine in the
    # original inputs and the three prefix outputs.  Thus the complete leakage
    # uses the three prefix ANDs and zero additional sibling ANDs.
    print(
        "SIBLING_ZERO_FIBER_CLOSURE "
        f"planes={len(zero)} disjoint_pairs={len(disjoint)} "
        f"orbits={len(orbit_by_rep)} extra_sibling_ands=0"
    )
    print(
        "SIBLING_ZERO_FIBER_BREAKDOWN "
        "block0_planes=7 block1_planes=7 block2_planes=7 "
        "orbit_size1=27 orbit_size2=36 orbit_size4=12"
    )
    print(
        "SIBLING_ZERO_FIBER_LOCAL_ALGEBRA "
        f"products={products} truth_cases={truth_cases} dimension=4"
    )
    print("LEVEL5_SIBLING_ZERO_FIBER_CLOSED")


if __name__ == "__main__":
    main()

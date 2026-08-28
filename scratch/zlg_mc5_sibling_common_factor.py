#!/usr/bin/env python3
from collections import Counter, defaultdict
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


def generic_one_and_identity():
    # After full-factor rebasing, two sibling products with a common factor
    # have the form A*B + (A+e)*C.  Over the Boolean ring this is
    # A*(B+C) + e*C, so only one sibling AND remains.
    checked = 0
    for A, B, C, e in product((0, 1), repeat=4):
        lhs = (A & B) ^ ((A ^ e) & C)
        rhs = (A & (B ^ C)) ^ (C if e else 0)
        assert lhs == rhs, (A, B, C, e, lhs, rhs)
        checked += 1
    assert checked == 16

    # Full-factor elementary rebasing moves change a product only by an
    # already-available factor, never by another AND.
    checked = 0
    for A, B in product((0, 1), repeat=2):
        assert (A & B) == (B & A)
        assert ((A ^ 1) & B) == ((A & B) ^ B)
        assert ((A ^ B) & B) == ((A & B) ^ B)  # B^2=B
        checked += 1
    assert checked == 4
    return 20


def main():
    algebra_cases = generic_one_and_identity()

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

    residual = {
        key: plane_residual(key, block_basis, reducer)
        for key in planes
    }
    fibers = defaultdict(list)
    for key, r in residual.items():
        fibers[r].append(key)

    common_pairs = []
    by_fiber_size = Counter()
    for members in fibers.values():
        if len(members) < 2:
            continue
        for A, B in combinations(members, 2):
            common = set(A) & set(B)
            if not common:
                continue
            # Distinct 2-planes over F2 intersect in exactly one nonzero
            # vector when they have a common factor direction.
            assert len(common) == 1, (A, B, common)
            w = next(iter(common))
            SA = [v for v in A if v != w]
            SB = [v for v in B if v != w]
            assert len(SA) == len(SB) == 2
            # Either complement in each plane is a valid second basis vector.
            assert all(subspace2_key(w, s) == A for s in SA)
            assert all(subspace2_key(w, t) == B for t in SB)
            # This pair really is a direct PQ+UV in S3 collision.
            assert residual[A] == residual[B]
            p = pair_key(A, B)
            common_pairs.append(p)
            by_fiber_size[len(members)] += 1

    assert len(common_pairs) == 8001
    assert len(set(common_pairs)) == 8001
    assert by_fiber_size == Counter({4: 6174, 7: 1764, 21: 63})

    # Quotient only after closure is established pairwise.  Every common-factor
    # orbit must stay entirely in the common-factor sector.
    orbit_by_rep = {}
    common_set = set(common_pairs)
    for p in common_pairs:
        o = orbit(p)
        assert o <= common_set
        rep = min(o)
        orbit_by_rep.setdefault(rep, o)
        assert orbit_by_rep[rep] == o

    assert len(orbit_by_rep) == 2769
    orbit_size_dist = Counter(len(o) for o in orbit_by_rep.values())
    assert orbit_size_dist == Counter({1: 465, 2: 1224, 4: 888, 8: 192})

    print(
        "SIBLING_COMMON_FACTOR_CLOSURE "
        f"pairs=8001 orbits=2769 algebra_cases={algebra_cases} "
        "extra_sibling_ands=1"
    )
    print(
        "SIBLING_COMMON_FACTOR_BREAKDOWN "
        "size4_pairs=6174 size7_pairs=1764 size21_pairs=63 "
        "orbit_size1=465 orbit_size2=1224 orbit_size4=888 orbit_size8=192"
    )
    print("LEVEL5_SIBLING_COMMON_FACTOR_CLOSED")


if __name__ == "__main__":
    main()

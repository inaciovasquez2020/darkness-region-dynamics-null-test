#!/usr/bin/env python3
from collections import Counter, defaultdict
from itertools import combinations

from zlg_mc5_sibling_kernel import (
    ONE,
    VARS,
    cross_class,
    iter_bits,
    make_reducer,
    mul,
    reduce_mod,
    subspace2_key,
    topology,
)

BITS = (0, 0, 0, 0, 0, 0)


def coord_poly(c, block_basis):
    out = 0
    for i in iter_bits(c):
        out ^= block_basis[i]
    return out


def plane_residual(key, block_basis, reducer):
    a, b, c = key
    residuals = []
    for p, q in ((a, b), (a, c), (b, c)):
        P = coord_poly(p, block_basis)
        Q = coord_poly(q, block_basis)
        residuals.append(reduce_mod(mul(P, Q), reducer))
    assert residuals[0] == residuals[1] == residuals[2], (key, residuals)
    return residuals[0]


def main():
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

    direct_fibers = defaultdict(list)
    cross_fibers = defaultdict(list)

    for key, (p, q) in planes.items():
        direct_fibers[plane_residual(key, block_basis, reducer)].append(key)
        cross_fibers[cross_class(p, q)].append(key)

    direct_partition = {frozenset(v) for v in direct_fibers.values()}
    cross_partition = {frozenset(v) for v in cross_fibers.values()}
    assert direct_partition == cross_partition

    size_dist = Counter(len(v) for v in direct_fibers.values())
    assert size_dist == Counter({1: 38269, 4: 1029, 7: 147, 21: 1}), size_dist

    by_fiber_size = Counter()
    by_intersection = Counter()
    by_size_and_intersection = defaultdict(Counter)

    for members in direct_fibers.values():
        if len(members) < 2:
            continue
        for A, B in combinations(members, 2):
            by_fiber_size[len(members)] += 1
            kind = "common_factor" if set(A) & set(B) else "disjoint"
            by_intersection[kind] += 1
            by_size_and_intersection[len(members)][kind] += 1

    assert by_fiber_size == Counter({4: 6174, 7: 3087, 21: 210}), by_fiber_size
    assert by_intersection == Counter({"common_factor": 8001, "disjoint": 1470}), by_intersection
    assert by_size_and_intersection[4] == Counter({"common_factor": 6174})
    assert by_size_and_intersection[7] == Counter({"common_factor": 1764, "disjoint": 1323})
    assert by_size_and_intersection[21] == Counter({"common_factor": 63, "disjoint": 147})

    total = sum(by_fiber_size.values())
    assert total == 9471

    print(
        "SIBLING_COLLISION_CENSUS "
        f"planes={len(planes)} classes={len(direct_fibers)} collisions={total} "
        f"common_factor={by_intersection['common_factor']} disjoint={by_intersection['disjoint']}"
    )
    print(
        "SIBLING_COLLISION_BREAKDOWN "
        "size4=6174 size7=3087 size21=210 "
        "size7_disjoint=1323 zero_fiber_disjoint=147"
    )
    print("CROSS_CLASS_PARTITION_MATCHES_DIRECT_PQ_MOD_S3")
    print("LEVEL5_SIBLING_COLLISION_CENSUS_VERIFIED")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from collections import defaultdict
from itertools import combinations

from zlg_mc5_sibling_collision_census import BITS, coord_poly, plane_residual
from zlg_mc5_sibling_kernel import (
    ONE,
    VARS,
    iter_bits,
    make_reducer,
    reduce_mod,
    subspace2_key,
    topology,
)

GENERATORS = {
    "sigma1": (0, 1, 0),
    "sigma2": (1, 1, 2),
    "sigma3": (2, 1, 4),
}


def swap_coord_bits(v, block):
    i = 3 * block
    b0 = (v >> i) & 1
    b1 = (v >> (i + 1)) & 1
    if b0 != b1:
        v ^= (1 << i) | (1 << (i + 1))
    return v


def transform_plane(key, block):
    return tuple(sorted(swap_coord_bits(v, block) for v in key))


def swap_monomial(mask, i, j):
    bi = (mask >> i) & 1
    bj = (mask >> j) & 1
    if bi != bj:
        mask ^= (1 << i) | (1 << j)
    return mask


def permute_poly(poly, i, j):
    out = 0
    for monomial in iter_bits(poly):
        out ^= 1 << swap_monomial(monomial, i, j)
    return out


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

    residual = {
        key: plane_residual(key, block_basis, reducer)
        for key in planes
    }
    fibers = defaultdict(list)
    for key, r in residual.items():
        fibers[r].append(key)
    assert len(fibers) == 39446

    collision_count = 0
    for members in fibers.values():
        collision_count += len(members) * (len(members) - 1) // 2
    assert collision_count == 9471

    for name, (block, _, var_i) in GENERATORS.items():
        var_j = var_i + 1

        # The 9-coordinate action is exactly the Boolean-input swap on the
        # block basis (X_i,Y_i,a_i), and a_i is fixed by commutativity.
        for c in range(1 << 9):
            lhs = permute_poly(coord_poly(c, block_basis), var_i, var_j)
            rhs = coord_poly(swap_coord_bits(c, block), block_basis)
            assert lhs == rhs, (name, c)

        # S3 is invariant under the generator.
        for s in S3:
            assert reduce_mod(permute_poly(s, var_i, var_j), reducer) == 0, name

        # It is an involutive permutation of all factor 2-planes.
        for key in planes:
            t = transform_plane(key, block)
            assert t in planes, (name, key, t)
            assert transform_plane(t, block) == key, (name, key)

        # Direct covariance modulo S3 and preservation of residual fibers.
        target_by_source_residual = defaultdict(set)
        for key, r in residual.items():
            t = transform_plane(key, block)
            tr = residual[t]
            assert reduce_mod(permute_poly(r, var_i, var_j) ^ tr, reducer) == 0, (
                name,
                key,
            )
            target_by_source_residual[r].add(tr)

        assert all(len(v) == 1 for v in target_by_source_residual.values()), name

        # Every entire direct residual fiber maps bijectively to one direct
        # residual fiber of the same size. Therefore PQ+UV in S3 is preserved.
        for members in fibers.values():
            transformed = {transform_plane(key, block) for key in members}
            assert len(transformed) == len(members), name
            targets = {residual[key] for key in transformed}
            assert len(targets) == 1, (name, members[:2])
            target = next(iter(targets))
            assert len(fibers[target]) == len(members), name
            assert transformed == set(fibers[target]), name

        # Common-factor/disjoint status is also preserved on every collision.
        checked = 0
        for members in fibers.values():
            if len(members) < 2:
                continue
            for A, B in combinations(members, 2):
                TA = transform_plane(A, block)
                TB = transform_plane(B, block)
                assert bool(set(A) & set(B)) == bool(set(TA) & set(TB)), name
                assert residual[TA] == residual[TB], name
                checked += 1
        assert checked == 9471, (name, checked)

        print(
            "SIBLING_SYMMETRY_GENERATOR_VERIFIED "
            f"name={name} planes=43435 fibers=39446 collisions={checked}"
        )

    print("SIBLING_SYMMETRY_GROUP_GENERATORS sigma1 sigma2 sigma3")
    print("SIBLING_SYMMETRY_GENERATORS_COMMUTE_AND_SQUARE_TO_ID")
    print("LEVEL5_SIBLING_SYMMETRY_GENERATORS_VERIFIED")


if __name__ == "__main__":
    main()

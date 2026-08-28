#!/usr/bin/env python3
from collections import Counter, defaultdict
from itertools import combinations

from zlg_mc5_sibling_collision_census import BITS, plane_residual
from zlg_mc5_sibling_kernel import (
    ONE,
    VARS,
    make_reducer,
    subspace2_key,
    topology,
)
from zlg_mc5_sibling_symmetry import transform_plane


def pair_key(A, B):
    return tuple(sorted((A, B)))


def transform_pair(pair, mask):
    A, B = pair
    for block in range(3):
        if (mask >> block) & 1:
            A = transform_plane(A, block)
            B = transform_plane(B, block)
    return pair_key(A, B)


def orbit(pair):
    return frozenset(transform_pair(pair, mask) for mask in range(8))


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

    pairs = []
    sector = {}
    for members in fibers.values():
        n = len(members)
        if n < 2:
            continue
        for A, B in combinations(members, 2):
            p = pair_key(A, B)
            common = bool(set(A) & set(B))
            kind = "common" if common else "disjoint"
            sector[p] = f"size{n}_{kind}"
            pairs.append(p)

    pairset = set(pairs)
    assert len(pairset) == 9471
    assert Counter(sector.values()) == Counter({
        "size4_common": 6174,
        "size7_common": 1764,
        "size7_disjoint": 1323,
        "size21_common": 63,
        "size21_disjoint": 147,
    })

    # Every one of the 8 certified group elements must preserve the full
    # collision set and the structural sector before quotienting.
    for mask in range(8):
        for p in pairs:
            t = transform_pair(p, mask)
            assert t in pairset, (mask, p, t)
            assert sector[t] == sector[p], (mask, sector[p], sector[t])

    # Direct orbit partition.
    orbit_by_rep = {}
    for p in pairs:
        o = orbit(p)
        rep = min(o)
        if rep in orbit_by_rep:
            assert orbit_by_rep[rep] == o
        else:
            orbit_by_rep[rep] = o

    assert len(orbit_by_rep) == 3351
    orbit_size_dist = Counter(len(o) for o in orbit_by_rep.values())
    assert orbit_size_dist == Counter({1: 567, 2: 1500, 4: 1092, 8: 192})
    assert sum(len(o) for o in orbit_by_rep.values()) == 9471

    orbit_sector_count = Counter()
    orbit_sector_size = defaultdict(Counter)
    for rep, o in orbit_by_rep.items():
        s = sector[rep]
        assert all(sector[p] == s for p in o)
        orbit_sector_count[s] += 1
        orbit_sector_size[s][len(o)] += 1

    assert orbit_sector_count == Counter({
        "size4_common": 1950,
        "size7_common": 780,
        "size7_disjoint": 507,
        "size21_common": 39,
        "size21_disjoint": 75,
    })
    assert orbit_sector_size["size4_common"] == Counter({1: 270, 2: 792, 4: 696, 8: 192})
    assert orbit_sector_size["size7_common"] == Counter({1: 180, 2: 408, 4: 192})
    assert orbit_sector_size["size7_disjoint"] == Counter({1: 75, 2: 240, 4: 192})
    assert orbit_sector_size["size21_common"] == Counter({1: 15, 2: 24})
    assert orbit_sector_size["size21_disjoint"] == Counter({1: 27, 2: 36, 4: 12})

    # Independent Burnside count. mask bits are sigma1,sigma2,sigma3.
    fixed = Counter()
    fixed_sector = defaultdict(Counter)
    for mask in range(8):
        for p in pairs:
            if transform_pair(p, mask) == p:
                fixed[mask] += 1
                fixed_sector[mask][sector[p]] += 1

    assert fixed == Counter({
        0: 9471,
        1: 4023,
        2: 4023,
        3: 1567,
        4: 4023,
        5: 1567,
        6: 1567,
        7: 567,
    })
    assert sum(fixed.values()) % 8 == 0
    assert sum(fixed.values()) // 8 == len(orbit_by_rep) == 3351

    expected_sector_orbits = {
        s: sum(fixed_sector[m][s] for m in range(8)) // 8
        for s in orbit_sector_count
    }
    assert Counter(expected_sector_orbits) == orbit_sector_count

    print(
        "SIBLING_ORBIT_QUOTIENT "
        "collisions=9471 group_order=8 orbits=3351 "
        "orbit_size1=567 orbit_size2=1500 orbit_size4=1092 orbit_size8=192"
    )
    print(
        "SIBLING_BURNSIDE_FIXED "
        "id=9471 sigma1=4023 sigma2=4023 sigma1sigma2=1567 "
        "sigma3=4023 sigma1sigma3=1567 sigma2sigma3=1567 "
        "sigma1sigma2sigma3=567"
    )
    print(
        "SIBLING_ORBIT_SECTORS "
        "size4_common=1950 size7_common=780 size7_disjoint=507 "
        "size21_common=39 size21_disjoint=75"
    )
    print("LEVEL5_SIBLING_ORBIT_QUOTIENT_VERIFIED")


if __name__ == "__main__":
    main()

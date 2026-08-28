#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from itertools import product

N = 6
ONE = 1 << 0
VARS = [1 << (1 << i) for i in range(N)]


def iter_bits(x):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def xor(*xs):
    z = 0
    for x in xs:
        z ^= x
    return z


def mul(p, q):
    out = 0
    for a in iter_bits(p):
        for b in iter_bits(q):
            out ^= 1 << (a | b)
    return out


def gf2_rank(vecs):
    piv = {}
    for x in vecs:
        y = x
        while y:
            h = y.bit_length() - 1
            if h in piv:
                y ^= piv[h]
            else:
                piv[h] = y
                break
    return len(piv)


def make_reducer(vecs):
    piv = {}
    for x in vecs:
        y = x
        for h in sorted(piv, reverse=True):
            if (y >> h) & 1:
                y ^= piv[h]
        if y:
            h = y.bit_length() - 1
            for hh in list(piv):
                if (piv[hh] >> h) & 1:
                    piv[hh] ^= y
            piv[h] = y
    return piv


def reduce_mod(x, piv):
    y = x
    for h in sorted(piv, reverse=True):
        if (y >> h) & 1:
            y ^= piv[h]
    return y


def coordinate_solver(basis):
    piv = {}
    for i, b in enumerate(basis):
        y, c = b, 1 << i
        for h in sorted(piv, reverse=True):
            pb, pc = piv[h]
            if (y >> h) & 1:
                y ^= pb
                c ^= pc
        assert y
        piv[y.bit_length() - 1] = (y, c)

    def solve(x):
        y, c = x, 0
        for h in sorted(piv, reverse=True):
            pb, pc = piv[h]
            if (y >> h) & 1:
                y ^= pb
                c ^= pc
        assert y == 0
        return c

    return solve


def wedge_index(i, j, d):
    if i > j:
        i, j = j, i
    k = 0
    for a in range(d):
        for b in range(a + 1, d):
            if a == i and b == j:
                return k
            k += 1
    raise AssertionError((i, j, d))


def wedge(c1, c2, d):
    out = 0
    for i in iter_bits(c1):
        for j in iter_bits(c2):
            if i != j:
                out ^= 1 << wedge_index(i, j, d)
    return out


def topology(bits):
    alpha, beta, p, q, r, s = bits
    x1, x2, x3, x4, x5, x6 = VARS
    a1 = mul(x1, x2)
    X2 = xor(x3, a1 if alpha else 0)
    Y2 = xor(x4, a1 if beta else 0)
    a2 = mul(X2, Y2)
    X3 = xor(x5, a1 if p else 0, a2 if q else 0)
    Y3 = xor(x6, a1 if r else 0, a2 if s else 0)
    a3 = mul(X3, Y3)
    return [(x1, x2, a1), (X2, Y2, a2), (X3, Y3, a3)]


def verify_topology(bits):
    gates = topology(bits)
    S = [ONE] + VARS + [g[2] for g in gates]
    assert gf2_rank(S) == 10
    reducer = make_reducer(S)
    solve = coordinate_solver(S)
    V = S[1:]
    d = 9

    cols = []
    for i in range(d):
        for j in range(i + 1, d):
            cols.append(reduce_mod(mul(V[i], V[j]), reducer))
    image_rank = gf2_rank(cols)
    assert image_rank == 27
    assert len(cols) - image_rank == 9

    def image(w):
        z = 0
        for k, col in enumerate(cols):
            if (w >> k) & 1:
                z ^= col
        return z

    triangles = []
    block_vectors = []
    for X, Y, a in gates:
        cx = solve(X) >> 1
        cy = solve(Y) >> 1
        ca = solve(a) >> 1
        block_vectors.extend([cx, cy, ca])
        triangles.extend([
            wedge(cx, cy, d),
            wedge(ca, cx, d),
            wedge(ca, cy, d),
        ])

    assert gf2_rank(block_vectors) == 9
    assert gf2_rank(triangles) == 9
    assert all(image(t) == 0 for t in triangles)
    return {
        "bits": "".join(map(str, bits)),
        "S_dim": 10,
        "wedge_dim": 36,
        "image_rank": 27,
        "kernel_dim": 9,
        "gate_triangle_rank": 9,
    }


def subspace2_key(p, q):
    assert p and q and p != q
    return tuple(sorted((p, q, p ^ q)))


def cross_class(p, q):
    out = 0
    k = 0
    for bi in range(3):
        for bj in range(bi + 1, 3):
            for i in range(3):
                for j in range(3):
                    pi = (p >> (3 * bi + i)) & 1
                    qi = (q >> (3 * bi + i)) & 1
                    pj = (p >> (3 * bj + j)) & 1
                    qj = (q >> (3 * bj + j)) & 1
                    if (pi & qj) ^ (qi & pj):
                        out |= 1 << k
                    k += 1
    return out


def rank3(rows):
    return gf2_rank(rows)


def matrix_rank(cls, offset):
    rows = []
    for i in range(3):
        row = 0
        for j in range(3):
            if (cls >> (offset + 3 * i + j)) & 1:
                row |= 1 << j
        rows.append(row)
    return rank3(rows)


def block_ranks(cls):
    return (matrix_rank(cls, 0), matrix_rank(cls, 9), matrix_rank(cls, 18))


def verify_fiber_geometry():
    subspaces = {}
    for p in range(1, 1 << 9):
        for q in range(p + 1, 1 << 9):
            key = subspace2_key(p, q)
            subspaces.setdefault(key, (p, q))
    assert len(subspaces) == 43435

    fibers = defaultdict(list)
    for key, (p, q) in subspaces.items():
        fibers[cross_class(p, q)].append(key)

    size_dist = Counter(len(v) for v in fibers.values())
    assert size_dist == Counter({1: 38269, 4: 1029, 7: 147, 21: 1}), size_dist

    pattern_dist = defaultdict(Counter)
    for cls, members in fibers.items():
        pattern_dist[len(members)][block_ranks(cls)] += 1

    expected = {
        21: Counter({(0, 0, 0): 1}),
        7: Counter({(1, 0, 0): 49, (0, 1, 0): 49, (0, 0, 1): 49}),
        4: Counter({(1, 1, 0): 343, (1, 0, 1): 343, (0, 1, 1): 343}),
        1: Counter({
            (2, 2, 2): 12348,
            (1, 1, 1): 6517,
            (2, 1, 1): 6174,
            (1, 2, 1): 6174,
            (1, 1, 2): 6174,
            (2, 0, 0): 294,
            (0, 2, 0): 294,
            (0, 0, 2): 294,
        }),
    }
    for size, want in expected.items():
        assert pattern_dist[size] == want, (size, pattern_dist[size], want)

    zero = fibers[0]
    assert len(zero) == 21
    block_zero = Counter()
    for key in zero:
        # Every nonzero vector of a zero-fiber plane lies in one unique 3D gate block.
        support = None
        for b in range(3):
            mask = 7 << (3 * b)
            if all((v & ~mask) == 0 for v in key):
                support = b
                break
        assert support is not None, key
        block_zero[support] += 1
    assert block_zero == Counter({0: 7, 1: 7, 2: 7})

    return {
        "two_planes": len(subspaces),
        "image_classes": len(fibers),
        "fiber_size_distribution": dict(sorted(size_dist.items())),
        "zero_fiber_planes": len(zero),
        "zero_fiber_by_gate_block": dict(sorted(block_zero.items())),
        "ambiguity": {
            "size_7": "exactly one rank-one cross-block",
            "size_4": "exactly two rank-one cross-blocks",
            "size_1": "all remaining nonzero classes",
        },
    }


def main():
    topo = [verify_topology(bits) for bits in product([0, 1], repeat=6)]
    assert len(topo) == 64
    fiber = verify_fiber_geometry()
    out = {
        "topologies_verified": 64,
        "all_topologies_kernel_exact": True,
        "generic_kernel": "direct sum of three gate-triangle exterior spaces",
        "per_topology": {
            "S_dim": 10,
            "wedge_dim": 36,
            "image_rank": 27,
            "kernel_dim": 9,
            "gate_triangle_rank": 9,
        },
        "fiber_geometry": fiber,
    }
    print("ZLG_MC5_SIBLING_KERNEL_BEGIN")
    print(json.dumps(out, sort_keys=True))
    print("ZLG_MC5_SIBLING_KERNEL_END")
    print("LEVEL5_GENERIC_SIBLING_KERNEL_VERIFIED")


if __name__ == "__main__":
    main()

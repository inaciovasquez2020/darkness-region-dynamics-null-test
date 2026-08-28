#!/usr/bin/env python3
from collections import Counter
from itertools import product
import json
from pathlib import Path

N = 6
M = 1 << N
ONE = (1 << M) - 1


def var(i):
    out = 0
    for x in range(M):
        if (x >> i) & 1:
            out |= 1 << x
    return out


X = [var(i) for i in range(N)]


def cb(b):
    return ONE if b else 0


def pmul(u, v):
    a, b = u
    c, d = v
    return a & c, (a & d) ^ (c & b) ^ (b & d)


def degree(tt):
    a = [(tt >> x) & 1 for x in range(M)]
    for i in range(N):
        bit = 1 << i
        for m in range(M):
            if m & bit:
                a[m] ^= a[m ^ bit]
    return max((m.bit_count() for m, c in enumerate(a) if c), default=-1)


def dimension(tt):
    vals = [(tt >> x) & 1 for x in range(M)]
    structures = 0
    for u in range(M):
        d = vals[0] ^ vals[u]
        if all((vals[x] ^ vals[x ^ u]) == d for x in range(M)):
            structures += 1
    return N - (structures.bit_length() - 1)


def circuit(bits):
    l1, m1, l2, m2, n1, n2, rho, sigma, tau, ups, eps = bits

    g1 = pmul((X[0], cb(l1)), (X[1], cb(m1)))
    g2 = pmul((X[2], cb(l2)), (X[3], cb(m2)))
    g3 = pmul(
        (g1[0] ^ X[4], g1[1] ^ cb(n1)),
        (g2[0] ^ X[5], g2[1] ^ cb(n2)),
    )

    # Disjoint sibling collision:
    #   P=x1, Q=a1+a3,
    #   U=x1+x6+a2, V=a3,
    # and PQ+UV=a1+a3.
    g4 = pmul(
        (X[0], cb(rho)),
        (g1[0] ^ g3[0], g1[1] ^ g3[1] ^ cb(sigma)),
    )
    g5 = pmul(
        (X[0] ^ X[5] ^ g2[0], g2[1] ^ cb(tau)),
        (g3[0], g3[1] ^ cb(ups)),
    )

    zero = g1[0] ^ g3[0] ^ g4[0] ^ g5[0]
    leak = cb(eps) ^ g1[1] ^ g3[1] ^ g4[1] ^ g5[1]

    # Slice-1 prefix outputs; these cost exactly the first three ANDs.
    c1 = g1[0] ^ g1[1]
    c2 = g2[0] ^ g2[1]
    c3 = g3[0] ^ g3[1]

    # Boolean absorption:
    #   c1=(x1+l1)(x2+m1)
    #   (x1+rho)c1 is c1 when rho=l1, and 0 otherwise.
    delta = 1 ^ rho ^ l1

    # The only fourth AND needed after the 3-gate prefix.
    h = (X[5] ^ c2 ^ cb(rho ^ tau)) & c3

    four = h ^ c3
    if 1 ^ delta:
        four ^= c1
    if ups:
        four ^= c2
    if sigma ^ ups:
        four ^= X[0]
    if ups:
        four ^= X[5]
    if eps ^ (sigma & rho) ^ (ups & tau):
        four ^= ONE

    return zero, leak, four


def main():
    unique = set()
    by_label = Counter()

    for bits in product((0, 1), repeat=11):
        zero, leak, four = circuit(bits)
        assert zero == 0, (bits, hex(zero))
        assert leak == four, (bits, hex(leak), hex(four))
        unique.add(leak)
        by_label[(degree(leak), dimension(leak))] += 1

    by_unique = Counter((degree(f), dimension(f)) for f in unique)
    out = {
        "labelings_checked": 1 << 11,
        "distinct_leakage_functions": len(unique),
        "all_zero_slices_vanish": True,
        "all_have_explicit_four_and_realization": True,
        "labeling_degree_dimension_counts": {
            f"deg{d}_dim{di}": c for (d, di), c in sorted(by_label.items())
        },
        "unique_degree_dimension_counts": {
            f"deg{d}_dim{di}": c for (d, di), c in sorted(by_unique.items())
        },
        "result": "LEVEL5_DISJOINT_ABSORPTION_CLOSED",
    }
    Path("/tmp/zlg_mc5_disjoint_absorption.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(out, sort_keys=True))
    print("LEVEL5_DISJOINT_ABSORPTION_CLOSED")


if __name__ == "__main__":
    main()

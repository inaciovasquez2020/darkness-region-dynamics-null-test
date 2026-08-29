#!/usr/bin/env python3
"""Fail-closed verifier for size-7 sibling orbit ((1,28,29),(24,33,57))."""
from itertools import product

PAIR = ((1, 28, 29), (24, 33, 57))


def swap_bits(v, a, b):
    ba, bb = (v >> a) & 1, (v >> b) & 1
    if ba != bb:
        v ^= (1 << a) | (1 << b)
    return v


def act_plane(plane, mask):
    out = []
    for v in plane:
        for i, (a, b) in enumerate(((0, 1), (3, 4), (6, 7))):
            if (mask >> i) & 1:
                v = swap_bits(v, a, b)
        out.append(v)
    return tuple(sorted(out))


def act_pair(pair, mask):
    a, b = act_plane(pair[0], mask), act_plane(pair[1], mask)
    return tuple(sorted((a, b)))


def unsimplified(vals):
    x1, x2, x3, x4, l1, m1, l2, m2, rho, sigma, tau, ups, eps = vals
    a1 = x1 & x2
    a2 = x3 & x4
    d1 = (x1 & m1) ^ (x2 & l1) ^ (l1 & m1)
    d2 = (x3 & m2) ^ (x4 & l2) ^ (l2 & m2)

    # Pi1=<x1,a1+x3+x4>, Pi2=<x3+x4,x1+a2>.
    # PQ+UV=a1, so output correction contributes d1.
    # The a1 term inside Pi1's second factor contributes d1 there;
    # the a2 term inside Pi2's second factor contributes d2 there.
    theta4 = (x1 & (d1 ^ sigma)) ^ ((a1 ^ x3 ^ x4) & rho) ^ (rho & (d1 ^ sigma))
    theta5 = ((x3 ^ x4) & (d2 ^ ups)) ^ ((x1 ^ a2) & tau) ^ (tau & (d2 ^ ups))
    return d1 ^ theta4 ^ theta5 ^ eps


def simplified(vals):
    x1, x2, x3, x4, l1, m1, l2, m2, rho, sigma, tau, ups, eps = vals
    c1 = l1 ^ rho
    c2 = l2 ^ m2 ^ tau
    return (
        (c1 & (x1 & x2))
        ^ (c2 & (x3 & x4))
        ^ ((sigma ^ tau ^ (l1 & m1) ^ (m1 & rho)) & x1)
        ^ ((l1 ^ (l1 & rho)) & x2)
        ^ ((m2 ^ rho ^ ups ^ (l2 & m2) ^ (m2 & tau)) & x3)
        ^ ((l2 ^ rho ^ ups ^ (l2 & m2) ^ (l2 & tau)) & x4)
        ^ (l1 & m1)
        ^ (rho & sigma)
        ^ (tau & ups)
        ^ (l1 & m1 & rho)
        ^ (l2 & m2 & tau)
        ^ eps
    )


def collision(x1, x2, x3, x4):
    a1 = x1 & x2
    a2 = x3 & x4
    pq = x1 & (a1 ^ x3 ^ x4)
    uv = (x3 ^ x4) & (x1 ^ a2)
    return pq ^ uv, a1


def main():
    # Zero-slice identity on all x inputs.
    for xs in product((0, 1), repeat=4):
        lhs, rhs = collision(*xs)
        assert lhs == rhs, (xs, lhs, rhs)

    # Certified G3 orbit size for this canonical pair.
    orbit = {act_pair(PAIR, mask) for mask in range(8)}
    assert len(orbit) == 2, len(orbit)
    assert min(orbit) == PAIR

    truth_tables = set()
    coefficient_counts = {
        (0, 0): 0,
        (1, 0): 0,
        (0, 1): 0,
        (1, 1): 0,
    }
    checked = 0
    for labels in product((0, 1), repeat=9):
        l1, m1, l2, m2, rho, sigma, tau, ups, eps = labels
        coefficient_counts[(l1 ^ rho, l2 ^ m2 ^ tau)] += 1
        tt = []
        for xs in product((0, 1), repeat=4):
            vals = xs + labels
            u = unsimplified(vals)
            s = simplified(vals)
            assert u == s, (vals, u, s)
            tt.append(u)
            checked += 1
        truth_tables.add(tuple(tt))

    assert checked == 8192
    assert coefficient_counts == {
        (0, 0): 128,
        (1, 0): 128,
        (0, 1): 128,
        (1, 1): 128,
    }
    assert len(truth_tables) == 72, len(truth_tables)

    # For every fixed labeling, the only nonlinear x-monomials are
    # c1*x1*x2 and c2*x3*x4. Hence MC_x <= 2 uniformly.
    print(
        "SIBLING_SIZE7_ORBIT_CLOSURE "
        "pair=((1,28,29),(24,33,57)) orbit_size=2 "
        "labelings=512 evaluations=8192 distinct_functions=72"
    )
    print(
        "SIBLING_SIZE7_ORBIT_MC "
        "affine_labelings=128 one_and_labelings=256 "
        "two_and_labelings=128 mc_upper_bound=2"
    )
    print("LEVEL5_SIBLING_SIZE7_ORBIT_1_28_29__24_33_57_CLOSED")


if __name__ == "__main__":
    main()

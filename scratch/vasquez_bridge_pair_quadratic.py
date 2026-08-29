#!/usr/bin/env python3
from itertools import product

# Variables are (w,s1,s2,s3).  For fixed w, SAT is the satisfiability
# predicate of the selector-CNF
#
#   (not s1 or x)
#   (w or not s2 or not x)
#   (not w or not s3 or not x)
#
# over existential logical variable x.
#
# Thus w=0 gives 1+s1*s2 and w=1 gives 1+s1*s3.

XS = list(product((0,1), repeat=4))


def sat_gadget(inp):
    w,s1,s2,s3 = inp
    for x in (0,1):
        c1 = (not s1) or x
        c2 = w or (not s2) or (not x)
        c3 = (not w) or (not s3) or (not x)
        if c1 and c2 and c3:
            return 1
    return 0


def target(inp):
    w,s1,s2,s3 = inp
    return 1 ^ (s1 & (((1 ^ w) & s2) ^ (w & s3)))


def affine(mask, inp):
    # mask bits 0..3 are variable coefficients, bit 4 is constant.
    out = (mask >> 4) & 1
    for i,b in enumerate(inp):
        if (mask >> i) & 1:
            out ^= b
    return out


def one_and(maskL, maskR, outmask, gate_coeff, inp):
    g = affine(maskL, inp) & affine(maskR, inp)
    return affine(outmask, inp) ^ (g if gate_coeff else 0)


def explicit_two_and(inp):
    w,s1,s2,s3 = inp
    g1 = (1 ^ w) & (s2 ^ s3)
    g2 = (1 ^ s1) & (1 ^ s3 ^ g1)
    return s1 ^ s3 ^ g1 ^ g2


def main():
    # Exact selector-CNF identity.
    for inp in XS:
        assert sat_gadget(inp) == target(inp), inp

    # Restricted coordinates are exactly the claimed one-AND functions.
    for s1,s2,s3 in product((0,1), repeat=3):
        assert target((0,s1,s2,s3)) == (1 ^ (s1 & s2))
        assert target((1,s1,s2,s3)) == (1 ^ (s1 & s3))

    # Exhaust all one-AND circuits over four Boolean inputs.
    # 32 choices per affine gate factor, 32 affine outputs, 2 gate-output
    # coefficients = 65,536 candidate circuits.
    attempts = 0
    hits = 0
    for L in range(32):
        for R in range(32):
            for O in range(32):
                for d in (0,1):
                    attempts += 1
                    if all(one_and(L,R,O,d,inp) == target(inp) for inp in XS):
                        hits += 1
    assert attempts == 65536
    assert hits == 0

    # Explicit two-AND synthesis.
    for inp in XS:
        assert explicit_two_and(inp) == target(inp), inp

    print(
        'VASQUEZ_BRIDGE_PAIR_QUADRATIC '
        f'one_and_attempts={attempts} one_and_hits={hits} '
        'explicit_two_and=1 mc_exact=2'
    )
    print('VASQUEZ_BRIDGE_FIRST_SHARED_INCOMPATIBILITY_VERIFIED')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from itertools import product

# Exact finite classifier for one control bit z and three free variables.
# It enumerates every distinct one-AND Boolean function F(z,y1,y2,y3),
# forms Omega(F)=F(0,y) OR F(1,y), and checks that Omega has MC <= 1.


def truth(n, fn):
    out = 0
    for i,x in enumerate(product((0,1), repeat=n)):
        if fn(x):
            out |= 1 << i
    return out


def affine_tables(n):
    out=[]
    for mask in range(1 << (n+1)):
        def f(x, mask=mask):
            v=(mask >> n) & 1
            for j,b in enumerate(x):
                if (mask >> j) & 1:
                    v ^= b
            return v
        out.append(truth(n,f))
    return out


def mc_le_1_functions(n):
    aff=affine_tables(n)
    funcs=set(aff)
    for a in aff:
        for b in aff:
            g=a & b
            for c in aff:
                funcs.add(c ^ g)
    return funcs


def main():
    mc1_free=mc_le_1_functions(3)
    mc1_control=mc_le_1_functions(4)

    assert len(mc1_free) == 128
    assert len(mc1_control) == 1152

    omega_values=set()
    failures=[]
    for F in mc1_control:
        # product() ordering puts z=0 in low 8 bits and z=1 in high 8.
        f0=F & 0xff
        f1=(F >> 8) & 0xff
        omega=f0 | f1
        omega_values.add(omega)
        if omega not in mc1_free:
            failures.append((F,f0,f1,omega))

    assert not failures
    assert len(omega_values) == 128

    print(
        'VASQUEZ_OR_ABSORPTION1 '
        f'child_bundle_functions={len(mc1_control)} '
        f'distinct_parent_or_functions={len(omega_values)} '
        f'mc1_parent_universe={len(mc1_free)} failures={len(failures)}'
    )
    print('VASQUEZ_OR_ABSORPTION1_CLOSED')


if __name__ == '__main__':
    main()

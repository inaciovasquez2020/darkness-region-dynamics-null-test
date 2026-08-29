#!/usr/bin/env python3
from itertools import combinations


def gf2_rank(rows, n):
    rows=list(rows)
    r=0
    for col in range(n):
        p=next((i for i in range(r,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(len(rows)):
            if i!=r and ((rows[i]>>col)&1):
                rows[i]^=rows[r]
        r+=1
    return r


def q_rank(qmask,n):
    rows=[0]*n
    bit=0
    for i,j in combinations(range(n),2):
        if (qmask>>bit)&1:
            rows[i]^=1<<j
            rows[j]^=1<<i
        bit+=1
    return gf2_rank(rows,n)


def eval_quadratic(x,n,qmask,lmask,c):
    v=c
    for i in range(n):
        if ((lmask>>i)&1) and ((x>>i)&1):
            v^=1
    bit=0
    for i,j in combinations(range(n),2):
        if ((qmask>>bit)&1) and ((x>>i)&1) and ((x>>j)&1):
            v^=1
        bit+=1
    return v


def dim_invariant(vals,n):
    cnt=0
    for u in range(1<<n):
        d0=vals[0]^vals[u]
        if all((vals[x]^vals[x^u])==d0 for x in range(1<<n)):
            cnt+=1
    assert cnt and not (cnt&(cnt-1))
    return n-(cnt.bit_length()-1),cnt


def zero_derivative_dirs(vals,n):
    out=[]
    for u in range(1<<n):
        if all((vals[x]^vals[x^u])==0 for x in range(1<<n)):
            out.append(u)
    return out


def lift_vals(fvals,n):
    # variable z is the new top bit
    out=[0]*(1<<(n+1))
    for z in (0,1):
        for x in range(1<<n):
            out[x|(z<<n)] = z & fvals[x]
    return out


def exhaustive_n4():
    n=4
    qbits=n*(n-1)//2
    checked=0
    rank2=0
    rank4=0
    for qmask in range(1,1<<qbits):
        qr=q_rank(qmask,n)
        assert qr in (2,4)
        for lmask in range(1<<n):
            for c in (0,1):
                f=[eval_quadratic(x,n,qmask,lmask,c) for x in range(1<<n)]
                g=lift_vals(f,n)
                dim_g,ls_count=dim_invariant(g,n+1)
                zero_dirs=zero_derivative_dirs(f,n)
                # Exact slice derivative identity gives LS(zf)={0}x Z(f).
                assert ls_count==len(zero_dirs)
                assert dim_g >= qr+1
                checked+=1
                if qr==2: rank2+=1
                else: rank4+=1
    assert checked==2016
    return checked,rank2,rank4


def canonical_sweep():
    rows=[]
    for r in range(1,6):
        n=2*r
        qmask=0
        bit=0
        for i,j in combinations(range(n),2):
            if j==i+1 and i%2==0:
                qmask |= 1<<bit
            bit+=1
        assert q_rank(qmask,n)==2*r
        f=[eval_quadratic(x,n,qmask,0,0) for x in range(1<<n)]
        g=lift_vals(f,n)
        dim_g,ls_count=dim_invariant(g,n+1)
        assert dim_g==2*r+1
        assert ls_count==1
        rows.append((r,n+1,dim_g))
    return rows


def main():
    checked,rank2,rank4=exhaustive_n4()
    rows=canonical_sweep()
    print(
        'VASQUEZ_QUADRATIC_FRESH_LIFT_DIMENSION '
        f'n4_forms_checked={checked} rank2_forms={rank2} rank4_forms={rank4}'
    )
    for r,n,dim in rows:
        print(f'CANONICAL r={r} lifted_variables={n} dim_nl={dim} expected={2*r+1}')
    print('VASQUEZ_QUADRATIC_FRESH_LIFT_DIMENSION_VERIFIED')


if __name__=='__main__':
    main()

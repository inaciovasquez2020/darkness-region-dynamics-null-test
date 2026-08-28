#!/usr/bin/env python3
import json
from itertools import product


def iter_bits(x):
    while x:
        b=x&-x; yield b.bit_length()-1; x^=b

def pxor(*xs):
    z=0
    for x in xs:z^=x
    return z

def mul(p,q):
    out=0
    for a in iter_bits(p):
        for b in iter_bits(q):out^=1<<(a|b)
    return out

def rank(xs):
    piv={}
    for x in xs:
        y=x
        while y:
            h=y.bit_length()-1
            if h in piv:y^=piv[h]
            else:piv[h]=y;break
    return len(piv)

def reducer(xs):
    piv={}
    for x in xs:
        y=x
        for h in sorted(piv,reverse=True):
            if (y>>h)&1:y^=piv[h]
        if y:
            h=y.bit_length()-1
            for hh in list(piv):
                if (piv[hh]>>h)&1:piv[hh]^=y
            piv[h]=y
    return piv

def reduce_mod(x,piv):
    y=x
    for h in sorted(piv,reverse=True):
        if (y>>h)&1:y^=piv[h]
    return y

def solve_factory(basis):
    piv={}
    for i,b in enumerate(basis):
        y,c=b,1<<i
        for h in sorted(piv,reverse=True):
            pb,pc=piv[h]
            if (y>>h)&1:y^=pb;c^=pc
        assert y
        piv[y.bit_length()-1]=(y,c)
    def solve(x):
        y,c=x,0
        for h in sorted(piv,reverse=True):
            pb,pc=piv[h]
            if (y>>h)&1:y^=pb;c^=pc
        assert y==0
        return c
    return solve

def wedge_index(i,j,d):
    if i>j:i,j=j,i
    k=0
    for a in range(d):
        for b in range(a+1,d):
            if (a,b)==(i,j):return k
            k+=1
    raise AssertionError

def wedge(a,b,d):
    z=0
    for i in iter_bits(a):
        for j in iter_bits(b):
            if i!=j:z^=1<<wedge_index(i,j,d)
    return z

def topology(n,bits):
    # Polynomial ANFs are bitsets indexed by Boolean monomial masks.
    one=1<<0
    xs=[1<<(1<<i) for i in range(n)]
    A,B,p,q,r,s=bits
    a1=mul(xs[0],xs[1])
    X2=pxor(xs[2],a1 if A else 0);Y2=pxor(xs[3],a1 if B else 0);a2=mul(X2,Y2)
    X3=pxor(xs[4],a1 if p else 0,a2 if q else 0)
    Y3=pxor(xs[5],a1 if r else 0,a2 if s else 0);a3=mul(X3,Y3)
    return one,xs,[(xs[0],xs[1],a1),(X2,Y2,a2),(X3,Y3,a3)]
def verify(n,bits):
    one,xs,gates=topology(n,bits)
    S=[one]+xs+[g[2] for g in gates]
    assert rank(S)==n+4
    red=reducer(S); solve=solve_factory(S); V=S[1:]; d=n+3
    cols=[]
    for i in range(d):
        for j in range(i+1,d):cols.append(reduce_mod(mul(V[i],V[j]),red))
    image_rank=rank(cols); kernel_dim=len(cols)-image_rank
    assert kernel_dim==9
    tris=[]
    for X,Y,a in gates:
        x=solve(X)>>1;y=solve(Y)>>1;aa=solve(a)>>1
        tris.extend([wedge(x,y,d),wedge(aa,x,d),wedge(aa,y,d)])
    assert rank(tris)==9
    def image(w):
        z=0
        for k,c in enumerate(cols):
            if (w>>k)&1:z^=c
        return z
    assert all(image(t)==0 for t in tris)
    return {"n":n,"S_dim":n+4,"wedge_dim":d*(d-1)//2,"image_rank":image_rank,"kernel_dim":kernel_dim}
def main():
    summary={}
    count=0
    for n in range(6,11):
        vals=[]
        for bits in product([0,1],repeat=6):
            vals.append(verify(n,bits));count+=1
        first=vals[0]
        assert all(v==first for v in vals)
        summary[str(n)]=first
    out={"dimensions_verified":[6,7,8,9,10],"topologies_per_dimension":64,"total_cases":count,"all_kernel_exact":True,"kernel":"nine gate-triangle wedges only","summary":summary}
    print("ZLG_MC5_SIBLING_KERNEL_EXTENDED_BEGIN")
    print(json.dumps(out,sort_keys=True))
    print("ZLG_MC5_SIBLING_KERNEL_EXTENDED_END")
    print("LEVEL5_RANK6_SIBLING_KERNEL_DIM10_VERIFIED")
if __name__=='__main__':main()

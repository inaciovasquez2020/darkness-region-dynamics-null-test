#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from itertools import product


def bits(x):
    while x:
        b=x&-x; yield b.bit_length()-1; x^=b

def xor(*xs):
    z=0
    for x in xs:z^=x
    return z

def mul(p,q):
    z=0
    for a in bits(p):
        for b in bits(q): z ^= 1 << (a|b)
    return z

def rank(xs):
    piv={}
    for x in xs:
        y=x
        while y:
            h=y.bit_length()-1
            if h in piv:y^=piv[h]
            else:piv[h]=y;break
    return len(piv)

def basis(xs):
    out=[]
    for x in xs:
        if rank(out+[x])>len(out):out.append(x)
    return out

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

def solve_factory(bs):
    piv={}
    for i,b in enumerate(bs):
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
    for i in bits(a):
        for j in bits(b):
            if i!=j:z ^= 1 << wedge_index(i,j,d)
    return z

def rank5_forms(rel,n):
    supp=[i for i in range(6) if (rel>>i)&1]
    pivot=supp[-1]
    other=[i for i in range(6) if i!=pivot]
    xs=[1<<(1<<i) for i in range(n)]
    fs=[0]*6
    for j,pos in enumerate(other):fs[pos]=xs[j]
    fs[pivot]=xor(*(fs[i] for i in supp if i!=pivot))
    # Exactly one relation among the six linear parts.
    assert rank(fs)==5
    return fs,xs

def gates_for(fs,t):
    A,B,p,q,r,s=t
    L1,L2,L3,L4,L5,L6=fs
    a1=mul(L1,L2)
    X2=xor(L3,a1 if A else 0);Y2=xor(L4,a1 if B else 0);a2=mul(X2,Y2)
    X3=xor(L5,a1 if p else 0,a2 if q else 0)
    Y3=xor(L6,a1 if r else 0,a2 if s else 0);a3=mul(X3,Y3)
    return [(L1,L2,a1),(X2,Y2,a2),(X3,Y3,a3)]
def classify(rel,t,n):
    fs,xs=rank5_forms(rel,n); gs=gates_for(fs,t)
    S=basis([1]+xs+[g[2] for g in gs])
    red=reducer(S); solve=solve_factory(S); V=S[1:];d=len(V)
    cols=[]
    for i in range(d):
        for j in range(i+1,d):cols.append(reduce_mod(mul(V[i],V[j]),red))
    image_rank=rank(cols); kernel_dim=len(cols)-image_rank
    tris=[]
    for X,Y,a in gs:
        cx=solve(X)>>1;cy=solve(Y)>>1;ca=solve(a)>>1
        tris.extend([wedge(cx,cy,d),wedge(ca,cx,d),wedge(ca,cy,d)])
    tri_rank=rank(tris)
    sdim=len(S)
    if sdim==n+4 and kernel_dim==9 and tri_rank==9:return 'triangle_exact'
    if sdim==n+4 and kernel_dim==11 and tri_rank==9:return 'extra_kernel_2'
    if sdim==n+3 and kernel_dim==6 and tri_rank==6:return 'prefix_degenerate'
    raise AssertionError((rel,t,n,sdim,kernel_dim,tri_rank,image_rank))

def main():
    expected=Counter({'triangle_exact':2352,'extra_kernel_2':1344,'prefix_degenerate':336})
    expected_support={
      1:Counter({'prefix_degenerate':224,'extra_kernel_2':128,'triangle_exact':32}),
      2:Counter({'extra_kernel_2':576,'triangle_exact':272,'prefix_degenerate':112}),
      3:Counter({'triangle_exact':768,'extra_kernel_2':512}),
      4:Counter({'triangle_exact':832,'extra_kernel_2':128}),
      5:Counter({'triangle_exact':384}),
      6:Counter({'triangle_exact':64}),
    }
    per_n={}
    support_ref=defaultdict(Counter)
    total=0
    for n in range(5,11):
        c=Counter()
        support=defaultdict(Counter)
        for rel in range(1,64):
            for t in product([0,1],repeat=6):
                k=classify(rel,t,n);c[k]+=1;support[rel.bit_count()][k]+=1;total+=1
        assert c==expected,(n,c)
        for s,w in expected_support.items():assert support[s]==w,(n,s,support[s],w)
        if n==5:support_ref=support
        per_n[str(n)]=dict(c)
    out={
      'dimensions_verified':list(range(5,11)),
      'dependency_types':63,
      'topologies_per_dependency':64,
      'cases_per_dimension':4032,
      'total_cases':total,
      'classification_per_dimension':dict(expected),
      'support_distribution':{str(s):dict(expected_support[s]) for s in sorted(expected_support)},
      'interpretation':{
        'triangle_exact':'kernel is exactly the nine gate-triangle wedges',
        'extra_kernel_2':'prefix outputs independent modulo affine, but kernel has exactly two additional dimensions',
        'prefix_degenerate':'one prefix gate output is dependent modulo affine; gate-triangle rank drops to six'
      },
      'all_dimensions_stable':True,
      'per_dimension':per_n,
    }
    print('ZLG_MC5_SIBLING_RANK5_SHELL_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC5_SIBLING_RANK5_SHELL_END')
    print('LEVEL5_SIBLING_RANK5_SHELL_CLASSIFIED')
if __name__=='__main__':main()

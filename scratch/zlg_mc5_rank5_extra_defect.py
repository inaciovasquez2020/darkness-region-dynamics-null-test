#!/usr/bin/env python3
import json
from collections import Counter
from itertools import product


def ibits(x):
    while x:
        b=x&-x; yield b.bit_length()-1; x^=b

def xor(*xs):
    z=0
    for x in xs:z^=x
    return z

def mul(p,q):
    z=0
    for a in ibits(p):
        for b in ibits(q):z^=1<<(a|b)
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

def kernel_basis(cols):
    piv={};ker=[]
    for k,c in enumerate(cols):
        y,r=c,1<<k
        while y:
            h=y.bit_length()-1
            if h in piv:
                py,pr=piv[h];y^=py;r^=pr
            else:
                piv[h]=(y,r);break
        if y==0:ker.append(r)
    return ker

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
    for i in ibits(a):
        for j in ibits(b):
            if i!=j:z^=1<<wedge_index(i,j,d)
    return z

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

def rank5_forms(rel):
    supp=[i for i in range(6) if (rel>>i)&1]
    pivot=supp[-1]
    other=[i for i in range(6) if i!=pivot]
    xs=[1<<(1<<i) for i in range(5)]
    fs=[0]*6
    for j,pos in enumerate(other):fs[pos]=xs[j]
    fs[pivot]=xor(*(fs[i] for i in supp if i!=pivot))
    assert rank(fs)==5
    return fs,xs

def gates(fs,t,c=0):
    A,B,p,q,r,s=t
    L=[xor(fs[i],1 if ((c>>i)&1) else 0) for i in range(6)]
    a1=mul(L[0],L[1])
    X2=xor(L[2],a1 if A else 0);Y2=xor(L[3],a1 if B else 0);a2=mul(X2,Y2)
    X3=xor(L[4],a1 if p else 0,a2 if q else 0)
    Y3=xor(L[5],a1 if r else 0,a2 if s else 0);a3=mul(X3,Y3)
    return [(L[0],L[1],a1),(X2,Y2,a2),(X3,Y3,a3)]

def zero_case(rel,t):
    fs,xs=rank5_forms(rel);gs=gates(fs,t,0)
    S=basis([1]+xs+[g[2] for g in gs])
    if len(S)!=9:return None
    V=S[1:];d=8;red=reducer(S);solve=solve_factory(S)
    cols=[reduce_mod(mul(V[i],V[j]),red) for i in range(d) for j in range(i+1,d)]
    K=kernel_basis(cols)
    tris=[]
    for X,Y,a in gs:
        cx=solve(X)>>1;cy=solve(Y)>>1;ca=solve(a)>>1
        tris += [wedge(cx,cy,d),wedge(ca,cx,d),wedge(ca,cy,d)]
    T=basis(tris)
    if len(K)!=11 or len(T)!=9:return None
    cur=T[:];ext=[]
    for k in K:
        if rank(cur+[k])>len(cur):
            ext.append(k);cur.append(k)
            if len(ext)==2:break
    assert len(ext)==2
    return fs,xs,ext,T

def full_defect(fs,xs,t,c,ext,T):
    hs=[g[2] for g in gates(fs,t,c)]
    tau=xs+hs
    S1=basis([1]+xs+hs)
    assert len(tau)==8 and len(S1)==9
    red=reducer(S1)
    cols=[reduce_mod(mul(tau[i],tau[j]),red) for i in range(8) for j in range(i+1,8)]
    def apply(w):
        z=0
        for k in ibits(w):z^=cols[k]
        return z
    assert all(apply(w)==0 for w in T)
    return [apply(ext[0]),apply(ext[1])],S1

def in_span(y,vs):return rank(vs+[y])==rank(vs)
def one_product(S,y):
    V=S[1:];d=len(V);red=reducer(S)
    pp=[[0]*d for _ in range(d)]
    for i in range(d):
        for j in range(i+1,d):
            pp[i][j]=pp[j][i]=reduce_mod(mul(V[i],V[j]),red)
    for r in range(1,1<<d):
        imgs=[]
        for j in range(d):
            z=0
            for i in ibits(r):
                if i!=j:z^=pp[i][j]
            imgs.append(z)
        if in_span(y,imgs):return True
    return False

def main():
    extra=0;parity_checks=0;canonical_rank1_checks=0
    by_support=Counter()
    for rel in range(1,64):
        canonical_c=rel&-rel
        for t in product([0,1],repeat=6):
            z=zero_case(rel,t)
            if z is None:continue
            fs,xs,ext,T=z;extra+=1;by_support[rel.bit_count()]+=1
            # Exact all-leakage parity law: delta=0 gives rank 0, delta=1 gives rank 2.
            for c in range(64):
                imgs,S1=full_defect(fs,xs,t,c,ext,T)
                got=rank(imgs);delta=((rel&c).bit_count()&1)
                assert got==(2 if delta else 0),(rel,t,c,got,delta)
                parity_checks+=1
            # For delta=1, all leakage patterns are related by translating the five
            # independent affine variables by a vector in the rank-five image.
            # It therefore suffices to certify one canonical odd-parity representative.
            imgs,S1=full_defect(fs,xs,t,canonical_c,ext,T)
            assert rank(imgs)==2
            for y in (imgs[0],imgs[1],imgs[0]^imgs[1]):
                assert y and one_product(S1,y),(rel,t,canonical_c)
                canonical_rank1_checks+=1
    assert extra==1344,extra
    assert parity_checks==1344*64,parity_checks
    assert canonical_rank1_checks==1344*3,canonical_rank1_checks
    assert by_support==Counter({1:128,2:576,3:512,4:128}),by_support
    out={
      'extra_cases':extra,
      'all_leakage_patterns_per_case':64,
      'parity_checks':parity_checks,
      'defect_law':'rank 0 iff rho.c=0; rank 2 iff rho.c=1',
      'canonical_odd_parity_cases':extra,
      'nonzero_defect_classes_per_case':3,
      'one_additional_product_checks':canonical_rank1_checks,
      'all_nonzero_odd_defects_one_product_over_prefix':True,
      'support_distribution':dict(sorted(by_support.items())),
      'affine_translation_reduction':'all c with fixed rho.c are affine translations of the canonical representative'
    }
    print('ZLG_MC5_RANK5_EXTRA_DEFECT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC5_RANK5_EXTRA_DEFECT_END')
    print('LEVEL5_RANK5_EXTRA_DEFECT_ONE_PRODUCT_VERIFIED')
if __name__=='__main__':main()

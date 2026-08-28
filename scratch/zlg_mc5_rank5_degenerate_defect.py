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

def span_values(vs):
    vals={0}
    for v in basis(vs):vals|={x^v for x in list(vals)}
    return vals

def wedge_index(i,j,d=8):
    if i>j:i,j=j,i
    k=0
    for a in range(d):
        for b in range(a+1,d):
            if (a,b)==(i,j):return k
            k+=1
    raise AssertionError

def wedge(a,b,d=8):
    z=0
    for i in ibits(a):
        for j in ibits(b):
            if i!=j:z^=1<<wedge_index(i,j,d)
    return z

def all_two_planes():
    seen={}
    for p in range(1,1<<8):
        for q in range(p+1,1<<8):
            key=tuple(sorted((p,q,p^q)))
            if key not in seen:seen[key]=wedge(p,q)
    out=list(seen.values())
    assert len(out)==10795 and len(set(out))==10795
    return out
PLANES=all_two_planes()

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
    return [a1,a2,a3]

def mu_cols(tau):
    S=basis([1]+tau);red=reducer(S);d=len(tau)
    cols=[]
    for i in range(d):
        for j in range(i+1,d):cols.append(reduce_mod(mul(tau[i],tau[j]),red))
    return cols,S

def apply(w,cols):
    z=0
    for k in ibits(w):z^=cols[k]
    return z

def classify_zero(rel,t):
    fs,xs=rank5_forms(rel);tau0=xs+gates(fs,t,0);cols0,S0=mu_cols(tau0)
    # Syntactic factor space E/<1> has dimension 8. Degenerate means its
    # zero evaluation has one dependency: dim S0=8 including the constant.
    if len(S0)!=8:return None
    assert rank(cols0)==15
    K=kernel_basis(cols0)
    assert len(K)==13
    return fs,xs,cols0,S0,K

def main():
    cases=0;residue_checks=0;support=Counter();defect_ranks=Counter();allowed_sizes=Counter()
    for rel in range(1,64):
        c=rel&-rel  # canonical rho.c=1 representative
        for t in product([0,1],repeat=6):
            z=classify_zero(rel,t)
            if z is None:continue
            fs,xs,cols0,S0,K=z;cases+=1;support[rel.bit_count()]+=1
            # Even-parity leakage patterns are translations of c=0 and give zero defect.
            assert all(apply(k,cols0)==0 for k in K)
            # All odd-parity patterns differ from this canonical c by a translation
            # because their difference lies in rho^perp, the rank-five image.
            tau1=xs+gates(fs,t,c);cols1,S1=mu_cols(tau1)
            defect=span_values([apply(k,cols1) for k in K])
            dr=(len(defect)).bit_length()-1;defect_ranks[dr]+=1
            assert dr==6 and len(defect)==64,(rel,t,dr,len(defect))
            allowed={0}
            for w in PLANES:allowed.add(apply(w,cols1))
            allowed_sizes[len(allowed)]+=1
            bad=defect-allowed
            assert not bad,(rel,t,len(bad),next(iter(bad)))
            residue_checks+=len(defect)
    assert cases==336,cases
    assert support==Counter({1:224,2:112}),support
    assert defect_ranks==Counter({6:336}),defect_ranks
    assert residue_checks==336*64,residue_checks
    out={
      'degenerate_cases':cases,
      'dependency_support_distribution':dict(sorted(support.items())),
      'syntactic_factor_dimension_mod_constants':8,
      'zero_mu_rank':15,
      'zero_kernel_dimension':13,
      'canonical_odd_defect_rank':6,
      'canonical_odd_defect_residues_per_case':64,
      'residue_checks':residue_checks,
      'every_full_kernel_residue_zero_or_one_product':True,
      'parity_reduction':'rho.c=0 translates to c=0; rho.c=1 translates to canonical lowest-bit c',
      'consequence':'every sibling collision residue in the rank-five prefix-degenerate shell costs at most one additional product over the three-gate prefix'
    }
    print('ZLG_MC5_RANK5_DEGENERATE_DEFECT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC5_RANK5_DEGENERATE_DEFECT_END')
    print('LEVEL5_RANK5_DEGENERATE_SIBLING_ONE_PRODUCT_VERIFIED')
if __name__=='__main__':main()

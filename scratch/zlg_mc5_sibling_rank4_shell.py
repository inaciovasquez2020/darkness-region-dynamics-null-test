#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
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

def span(bs):
    vals={0}
    for b in basis(bs):vals|={x^b for x in list(vals)}
    return vals

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
            else:piv[h]=(y,r);break
        if y==0:ker.append(r)
    return ker

def apply(w,cols):
    z=0
    for k in ibits(w):z^=cols[k]
    return z

def two_subspaces_6():
    seen={}
    for p in range(1,64):
        for q in range(p+1,64):
            key=tuple(sorted((p,q,p^q)))
            seen[key]=key
    out=sorted(seen)
    assert len(out)==651
    return out

def dot(a,b):return ((a&b).bit_count()&1)
def annihilator_basis(K):
    rows=[]
    for v in range(1,64):
        if all(dot(v,k)==0 for k in K) and rank(rows+[v])>len(rows):
            rows.append(v)
            if len(rows)==4:break
    assert len(rows)==4
    return rows

def leakage_reps(rows):
    R=span(rows); reps={}
    for c in range(64):
        key=min(c^r for r in R)
        reps[key]=key
    out=sorted(reps)
    assert len(out)==4 and out[0]==0
    return out

def forms_from_kernel(K,n):
    rows=annihilator_basis(K)
    xs=[1<<(1<<i) for i in range(n)]
    fs=[]
    for slot in range(6):
        fs.append(xor(*(xs[j] for j,row in enumerate(rows) if (row>>slot)&1)))
    assert rank(fs)==4
    return fs,xs,rows

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

def main():
    Ks=two_subspaces_6();tops=list(product([0,1],repeat=6))
    total=0; stability=0
    shell=Counter(); defect_rank=Counter(); profile=Counter(); sdim_profiles=Counter()
    nonzero_defect_cases=0; max_defect=0
    for K in Ks:
        fs4,xs4,rows=forms_from_kernel(K,4);reps=leakage_reps(rows)
        fs10,xs10,_=forms_from_kernel(K,10)
        for t in tops:
            h0=gates(fs4,t,0);cols0,S0=mu_cols(xs4+h0);K0=kernel_basis(cols0)
            h10=gates(fs10,t,0);cols10,S10=mu_cols(xs10+h10);K10=kernel_basis(cols10)
            assert len(K0)==len(K10),(K,t,len(K0),len(K10),len(S0),len(S10))
            stability+=1
            zero_key=(len(S0),rank(cols0),len(K0))
            shell[zero_key]+=1
            dr=[]
            for c in reps:
                hc=gates(fs4,t,c);colsc,Sc=mu_cols(xs4+hc)
                imgs=[apply(k,colsc) for k in K0]
                rnk=rank(imgs);dr.append(rnk);defect_rank[rnk]+=1;max_defect=max(max_defect,rnk)
                if c and rnk:nonzero_defect_cases+=1
                assert len(Sc)==len(S0),(K,t,c,len(S0),len(Sc))
            profile[tuple(dr)]+=1
            sdim_profiles[(len(S0),tuple(dr))]+=1
            total+=1
    assert total==651*64==41664
    assert stability==total
    out={
      'rank4_dependency_kernels':len(Ks),
      'topologies_per_kernel':64,
      'zero_cases':total,
      'leakage_classes_per_kernel':4,
      'kernel_stability_n4_to_n10_cases':stability,
      'all_zero_kernel_dimensions_stable_through_n10':True,
      'zero_shell_distribution':{str(k):v for k,v in sorted(shell.items())},
      'defect_rank_distribution_all_classes':dict(sorted(defect_rank.items())),
      'defect_profile_distribution':{str(k):v for k,v in sorted(profile.items())},
      'sdim_defect_profile_distribution':{str(k):v for k,v in sorted(sdim_profiles.items())},
      'nonzero_defect_nonzero_leakage_class_occurrences':nonzero_defect_cases,
      'max_defect_rank':max_defect,
    }
    print('ZLG_MC5_SIBLING_RANK4_SHELL_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC5_SIBLING_RANK4_SHELL_END')
    print('LEVEL5_SIBLING_RANK4_SHELL_CLASSIFIED')
if __name__=='__main__':main()

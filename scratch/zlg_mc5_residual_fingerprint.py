#!/usr/bin/env python3
import hashlib, json, re, urllib.request
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

N=6
M=1<<N
ONE=(1<<M)-1
URL3='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc3_dim6.txt'
SHA3='16b37a3091a855610573d8de213c6eaf1cc6cab9'
URL4='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim6.txt'
SHA4='dd99bf00f68a72dfe11f87f15de3c28bd15b4a5a'

def blob_sha(d):
    h=hashlib.sha1();h.update(f'blob {len(d)}\0'.encode());h.update(d);return h.hexdigest()

def get(url,sha):
    d=urllib.request.urlopen(url,timeout=30).read()
    got=blob_sha(d); assert got==sha,(url,got,sha)
    return [s for s in d.decode().splitlines() if s.strip()]

def var(i):
    out=0
    for x in range(M):
        if (x>>i)&1: out|=1<<x
    return out
X=[var(i) for i in range(N)]

def cb(b): return ONE if b else 0

def pmul(u,v):
    a,b=u;c,d=v
    return a&c,(a&d)^(c&b)^(b&d)

def parse_anf(s):
    tt=0
    for x in range(M):
        y=0
        for term in s.split('+'):
            ids=[int(v)-1 for v in re.findall(r'x(\d+)',term)]
            if all((x>>i)&1 for i in ids): y^=1
        if y: tt|=1<<x
    return tt

def vals(tt): return [(tt>>x)&1 for x in range(M)]

def mobius_degree(tt):
    a=vals(tt)
    for i in range(N):
        bit=1<<i
        for m in range(M):
            if m&bit:a[m]^=a[m^bit]
    return max((m.bit_count() for m,c in enumerate(a) if c),default=-1)

def derivative(tt,u):
    out=0
    for x in range(M):
        if ((tt>>x)&1)^((tt>>(x^u))&1):out|=1<<x
    return out

def direction_signature(tt,u):
    d=derivative(tt,u)
    w=d.bit_count(); mw=min(w,M-w)
    return mobius_degree(d),mw

def fingerprint(tt):
    # Under f(x)->f(Ax+b)+ell(x)+c, nonzero directions are permuted;
    # D_u changes only by a constant, so algebraic degree (for nonconstant
    # derivatives) and min(weight,64-weight) are preserved. Full dimension-6
    # functions have no nonzero constant derivative.
    sig=tuple(sorted(direction_signature(tt,u) for u in range(1,M)))
    return sig

def linear_structures(tt):
    a=vals(tt); out=[]
    for u in range(M):
        d=a[0]^a[u]
        if all((a[x]^a[x^u])==d for x in range(M)):out.append((u,d))
    return out

def dimension(tt):
    s=len(linear_structures(tt));return N-(s.bit_length()-1)

def to_anf(tt):
    a=vals(tt)
    for i in range(N):
        bit=1<<i
        for m in range(M):
            if m&bit:a[m]^=a[m^bit]
    terms=[]
    for m,c in enumerate(a):
        if not c:continue
        if m==0:terms.append('1')
        else:terms.append(''.join(f'x{i+1}' for i in range(N) if (m>>i)&1))
    return '+'.join(terms) if terms else '0'

def residual(bits):
    l1,m1,l2,m2,n1,n2,rho,sigma,tau,ups,eps=bits
    g1=pmul((X[0],cb(l1)),(X[1],cb(m1)))
    g2=pmul((X[2],cb(l2)),(X[3],cb(m2)))
    g3=pmul((g1[0]^X[4],g1[1]^cb(n1)),(g2[0]^X[5],g2[1]^cb(n2)))
    # Residual disjoint collision: x5*a3 + a1*(x1+a3) = a1+a3.
    g4=pmul((X[4],cb(rho)),(g3[0],g3[1]^cb(sigma)))
    g5=pmul((g1[0],g1[1]^cb(tau)),(X[0]^g3[0],g3[1]^cb(ups)))
    zero=g1[0]^g3[0]^g4[0]^g5[0]
    leak=cb(eps)^g1[1]^g3[1]^g4[1]^g5[1]
    return zero,leak

def main():
    l3=get(URL3,SHA3);l4=get(URL4,SHA4)
    assert len(l3)==7 and len(l4)==888,(len(l3),len(l4))
    low=[parse_anf(s) for s in l3+l4]
    for t in low:
        assert dimension(t)==6
    lowfps=defaultdict(list)
    for i,t in enumerate(low):lowfps[fingerprint(t)].append(i)

    reps={}
    for bits in product((0,1),repeat=11):
        z,f=residual(bits);assert z==0
        if mobius_degree(f)==4 and dimension(f)==6:
            reps.setdefault(f,bits)
    assert len(reps)==512,len(reps)

    unmatched=[];matched=Counter()
    for f,bits in reps.items():
        hits=lowfps.get(fingerprint(f),[])
        if not hits:
            unmatched.append({'bits':bits,'anf':to_anf(f),'tt_hex':f'{f:016x}'})
        else:
            matched[len(hits)]+=1

    out={
      'inputs':{'mc3_dim6':{'lines':len(l3),'git_blob_sha':SHA3},'mc4_dim6':{'lines':len(l4),'git_blob_sha':SHA4}},
      'quartic_dim6_unique_candidates':len(reps),
      'fingerprint':'multiset over nonzero directions of (degree(D_u f), min(weight(D_u f),64-weight(D_u f)))',
      'fingerprint_matches_distribution':dict(sorted(matched.items())),
      'unmatched_count':len(unmatched),
      'first_unmatched':unmatched[:10],
      'result':'MC5_COUNTEREXAMPLE_CANDIDATE_CERTIFIED_BY_COMPLETE_LOW_MC_FINGERPRINT_EXCLUSION' if unmatched else 'NO_FINGERPRINT_EXCLUSION',
    }
    Path('/tmp/zlg_mc5_residual_fingerprint.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,sort_keys=True))
    print(out['result'])

if __name__=='__main__':main()

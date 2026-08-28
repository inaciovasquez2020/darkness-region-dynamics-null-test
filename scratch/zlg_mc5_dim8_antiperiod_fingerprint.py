#!/usr/bin/env python3
import hashlib, json, re, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc5_dim10.txt'
SHA5='ed42b4f9bb113914122210963d07ac124d6695a9'
URL4='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
SHA4='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'


def blob_sha(data):
    h=hashlib.sha1(); h.update(f'blob {len(data)}\0'.encode()); h.update(data); return h.hexdigest()

def get(url,sha):
    data=urllib.request.urlopen(url,timeout=30).read(); assert blob_sha(data)==sha,(blob_sha(data),sha)
    return [x for x in data.decode().splitlines() if x.strip()]

def parse(s):
    out=[]
    for term in s.split('+'):
        m=0
        for v in re.findall(r'x(\d+)',term): m|=1<<(int(v)-1)
        out.append(m)
    return out

def compact(mask,p): return (mask&((1<<p)-1)) | ((mask>>(p+1))<<p)
def toggle(S,m):
    if m in S:S.remove(m)
    else:S.add(m)
def restrict_anf(mons,a,c,p):
    S=set(); normal=a&~(1<<p)
    for m in mons:
        if not ((m>>p)&1): toggle(S,compact(m,p)); continue
        T=compact(m&~(1<<p),p)
        if c: toggle(S,T)
        x=normal
        while x:
            b=x&-x; j=b.bit_length()-1; x^=b
            toggle(S,T|(1<<(j if j<p else j-1)))
    return S
def quotient_anf(mons,p):
    S=set()
    for m in mons:
        if (m>>p)&1: toggle(S,compact(m&~(1<<p),p))
    return S
def affine(S): return all(m.bit_count()<=1 for m in S)
def truth(S,n):
    return [sum((x&m)==m for m in S)&1 for x in range(1<<n)]
def degree_vals(vals,n):
    a=vals[:]
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit:a[m]^=a[m^bit]
    return max((m.bit_count() for m,c in enumerate(a) if c),default=-1)
def structures(vals,n):
    out=[]
    for u in range(1<<n):
        d=vals[0]^vals[u]
        if all((vals[x]^vals[x^u])==d for x in range(1<<n)): out.append((u,d))
    return out
def embed(y,p,n):
    lo=y&((1<<p)-1); hi=y>>p
    return lo | (hi<<(p+1))
def essentialize(vals,n):
    ss=structures(vals,n)
    assert len(ss)==2,ss
    u,eps=next(x for x in ss if x[0])
    p=(u&-u).bit_length()-1
    h=[]
    for y in range(1<<(n-1)):
        x=embed(y,p,n)
        h.append(vals[x])
        assert vals[x^u]==(vals[x]^eps)
    return h,u,eps
def dweight(vals,u):
    return sum(vals[x]^vals[x^u] for x in range(len(vals)))
def fingerprint(vals,n):
    N=1<<n
    return (degree_vals(vals,n),tuple(sorted(min(dweight(vals,u),N-dweight(vals,u)) for u in range(1,N))))

def main():
    L5=get(URL5,SHA5); L4=get(URL4,SHA4)
    assert len(L5)==575 and len(L4)==42
    targets=[]; byfp=defaultdict(list)
    for i,s in enumerate(L4,1):
        v=truth(set(parse(s)),8); fp=fingerprint(v,8); targets.append((i,s,v,fp)); byfp[fp].append(i)
    counts=Counter(); cases=[]
    for gi,s in enumerate(L5,1):
        mons=parse(s)
        for a in range(1,1<<10):
            p=(a&-a).bit_length()-1
            for c in (0,1):
                R=restrict_anf(mons,a,c,p)
                if not affine(R): continue
                counts['affine_restrictions']+=1
                Q=quotient_anf(mons,p); q=truth(Q,9)
                ss=structures(q,9); dimq=9-(len(ss).bit_length()-1)
                counts[f'q_dim_{dimq}']+=1
                if dimq!=8: continue
                h,u,eps=essentialize(q,9)
                assert degree_vals(h,8)==degree_vals(q,9)
                assert len(structures(h,8))==1
                fp=fingerprint(h,8); matches=byfp.get(fp,[])
                counts[f'fingerprint_matches_{len(matches)}']+=1
                cases.append({'source_rep':gi,'normal':a,'side':c,'pivot':p,'structure_u':u,'structure_derivative':eps,'degree':degree_vals(h,8),'mc4_dim8_fingerprint_matches':matches})
    out={'inputs':{'mc5_dim10':{'sha':SHA5,'lines':len(L5)},'mc4_dim8':{'sha':SHA4,'lines':len(L4)}},'counts':dict(counts),'cases':cases,'all_candidates_have_mc4_fingerprint_match':all(x['mc4_dim8_fingerprint_matches'] for x in cases)}
    Path('/tmp/zlg_mc5_dim8_fp.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_MC5_DIM8_FP_BEGIN'); print(json.dumps(out,sort_keys=True)); print('ZLG_MC5_DIM8_FP_END')

if __name__=='__main__':main()

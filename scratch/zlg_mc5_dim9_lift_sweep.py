#!/usr/bin/env python3
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

URL='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc5_dim10.txt'
EXPECTED_BLOB_SHA='ed42b4f9bb113914122210963d07ac124d6695a9'
N=10


def git_blob_sha(data: bytes) -> str:
    h=hashlib.sha1(); h.update(f'blob {len(data)}\0'.encode()); h.update(data); return h.hexdigest()


def parse_anf(s):
    out=[]
    for term in s.strip().split('+'):
        if not term: continue
        m=0
        for v in re.findall(r'x(\d+)',term): m |= 1 << (int(v)-1)
        out.append(m)
    return out


def compact(mask,p):
    lo=mask & ((1<<p)-1)
    hi=mask >> (p+1)
    return lo | (hi<<p)


def toggle(S,m):
    if m in S: S.remove(m)
    else: S.add(m)


def restrict_anf(mons,a,c,p):
    S=set()
    normal_other=a & ~(1<<p)
    for m in mons:
        if not ((m>>p)&1):
            toggle(S,compact(m,p)); continue
        T=compact(m & ~(1<<p),p)
        if c: toggle(S,T)
        x=normal_other
        while x:
            b=x & -x; j=b.bit_length()-1; x^=b
            toggle(S,T | (1 << (j if j<p else j-1)))
    return S


def quotient_anf(mons,p):
    S=set()
    for m in mons:
        if (m>>p)&1: toggle(S,compact(m & ~(1<<p),p))
    return S


def is_affine_anf(S):
    return all(m.bit_count()<=1 for m in S)


def truth_from_anf(S,n):
    vals=[]
    for x in range(1<<n):
        v=0
        for m in S: v ^= int((x&m)==m)
        vals.append(v)
    return vals


def dim_invariant_from_anf(S,n):
    vals=truth_from_anf(S,n)
    structures=[]
    for u in range(1<<n):
        d=vals[0]^vals[u]
        if all((vals[x]^vals[x^u])==d for x in range(1<<n)):
            structures.append(u)
    size=len(structures)
    lg=size.bit_length()-1
    assert 1<<lg==size,(size,S)
    return n-lg


def anf_str(S):
    if not S: return '0'
    terms=[]
    for m in sorted(S,key=lambda x:(x.bit_count(),x)):
        if m==0: terms.append('1')
        else: terms.append(''.join(f'y{i+1}' for i in range(N-1) if (m>>i)&1))
    return '+'.join(terms)


def main():
    data=urllib.request.urlopen(URL,timeout=30).read(); sha=git_blob_sha(data)
    assert sha==EXPECTED_BLOB_SHA,(sha,EXPECTED_BLOB_SHA)
    lines=[x for x in data.decode().splitlines() if x.strip()]
    counts=Counter(); candidates=[]; quotient_cache={}
    for gi,line in enumerate(lines,1):
        mons=parse_anf(line)
        for a in range(1,1<<N):
            p=(a & -a).bit_length()-1
            for c in (0,1):
                counts['hyperplanes']+=1
                R=restrict_anf(mons,a,c,p)
                if not is_affine_anf(R): continue
                counts['affine_restrictions']+=1
                key=(gi,p)
                if key not in quotient_cache:
                    Q=quotient_anf(mons,p)
                    quotient_cache[key]=(dim_invariant_from_anf(Q,N-1),Q)
                di,Q=quotient_cache[key]
                counts[f'quotient_dim_{di}']+=1
                if di==9:
                    candidates.append({'source_rep':gi,'normal':a,'side':c,'pivot':p,'q_anf':anf_str(Q),'source_anf':line})
    out={
      'source':{'url':URL,'git_blob_sha':sha,'representatives':len(lines)},
      'method':'exact ANF hyperplane substitution; affine restriction; quotient=t coefficient; exact linear-structure dimension',
      'counts':dict(counts),
      'dimension9_candidates':candidates,
      'counterexample_count':len(candidates),
      'dim9_level5_sector_closed':len(candidates)==0,
    }
    Path('/tmp/zlg_mc5_dim9.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_MC5_DIM9_RESULT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC5_DIM9_RESULT_END')
    if candidates:
        print('LEVEL5_DIM9_COUNTEREXAMPLE_CANDIDATE_FOUND')
    else:
        print('LEVEL5_DIM9_SECTOR_CLOSED')

if __name__=='__main__': main()

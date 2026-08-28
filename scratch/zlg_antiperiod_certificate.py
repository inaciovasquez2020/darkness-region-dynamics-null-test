#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path
from zlg_finish_mc4 import (
    fetch, truth, degree, dim_invariant, hyperplane_q, tt_hex, rank,
    affine_equiv_upto_affine,
)
from zlg_finish_mc4_safe import affine_equiv_safe, direction_signature

URL8='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
URL7='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim7.txt'
URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim5.txt'
URL36='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc3_dim6.txt'
SHA8='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'
SHA7='17acdd408959d178fdd0867cf27d777f0dcb5fb9'
SHA5='33498fd9058abb1edae1c040cd430cb4a8bf15e5'
SHA36='16b37a3091a855610573d8de213c6eaf1cc6cab9'

def load(url,sha,expected):
    xs=[x for x in fetch(url,sha) if x.strip()]
    assert len(xs)==expected,(len(xs),expected)
    return xs

def sweep(lines,n):
    counts=Counter(); out=[]
    for gi,s in enumerate(lines,1):
        vals=truth(s,n)
        for a in range(1,1<<n):
            for c in (0,1):
                counts['hyperplanes']+=1
                q=hyperplane_q(vals,n,a,c)
                if q is None: continue
                counts['affine_restrictions']+=1
                d=degree(q,n-1); di=dim_invariant(q,n-1)
                counts[f'deg{d}_dim{di}']+=1
                out.append((gi,a,c,d,di,q))
    return counts,out

def linear_structures(vals,n):
    out=[]
    for u in range(1<<n):
        d0=vals[0]^vals[u]
        if all((vals[x]^vals[x^u])==d0 for x in range(1<<n)):
            out.append((u,d0))
    return out

def essentialize_one(vals,n):
    assert dim_invariant(vals,n)==n-1
    ls=linear_structures(vals,n)
    assert len(ls)==2,ls
    u,epsilon=next((u,e) for u,e in ls if u)
    comp=[]; current=[u]
    for i in range(n):
        e=1<<i
        if rank(current+[e],n)>rank(current,n):
            comp.append(e); current.append(e)
        if len(comp)==n-1: break
    assert len(comp)==n-1 and rank(comp+[u],n)==n
    h=[]
    for y in range(1<<(n-1)):
        x=0
        for i,v in enumerate(comp):
            if (y>>i)&1: x^=v
        h.append(vals[x])
    assert dim_invariant(h,n-1)==n-1
    assert degree(h,n-1)==degree(vals,n)
    for y in range(1<<(n-1)):
        x=0
        for i,v in enumerate(comp):
            if (y>>i)&1: x^=v
        assert vals[x]==h[y]
        assert vals[x^u]==(h[y]^epsilon)
    return h,u,epsilon,comp

def fingerprint(vals,n):
    return tuple(sorted(direction_signature(vals,u,n) for u in range(1,1<<n)))

def main():
    l8=load(URL8,SHA8,42)
    l7=load(URL7,SHA7,321)
    l5=load(URL5,SHA5,26)
    l36=load(URL36,SHA36,7)
    mc3d6=[]
    for i,s in enumerate(l36,1):
        v=truth(s,6)
        mc3d6.append((i,degree(v,6),v,fingerprint(v,6)))
    low_mc4d5=[]; degree5=0
    for i,s in enumerate(l5,1):
        v=truth(s,5); d=degree(v,5)
        if d==5: degree5+=1
        elif d in (3,4): low_mc4d5.append((i,d,v,s,fingerprint(v,5)))
    assert degree5==19 and len(low_mc4d5)==7

    c8,q8=sweep(l8,8)
    dim6=[x for x in q8 if x[4]==6]
    assert len(dim6)==7,len(dim6)
    dim6_verified=[]
    for g,a,c,d,di,q7 in dim6:
        q,u,eps,comp=essentialize_one(q7,7)
        if d<=2:
            dim6_verified.append((g,a,c,d,'quadratic-MC3',u,eps))
            continue
        fp=fingerprint(q,6)
        candidates=[(ti,tv) for ti,td,tv,tfp in mc3d6 if td==d and tfp==fp]
        print('DIM6_FP',g,a,c,d,[ti for ti,_ in candidates],flush=True)
        assert candidates,(g,a,c,d,'no MC3 fingerprint match')
        hits=[]
        for ti,tv in candidates:
            if affine_equiv_upto_affine(q,tv,6): hits.append(ti)
        assert hits,(g,a,c,d,'fingerprint matched but no positive affine witness',[ti for ti,_ in candidates])
        dim6_verified.append((g,a,c,d,hits,u,eps))

    c7,q7=sweep(l7,7)
    dim5_low=[x for x in q7 if x[4]==5 and x[3] in (3,4)]
    assert len(dim5_low)==14,len(dim5_low)
    bad=[]; tested=[]
    for g,a,c,d,di,q6 in dim5_low:
        q,u,eps,comp=essentialize_one(q6,6)
        fp=fingerprint(q,5)
        candidates=[(ti,tv) for ti,td,tv,ts,tfp in low_mc4d5 if td==d and tfp==fp]
        print('DIM5_FP',g,a,c,d,[ti for ti,_ in candidates],flush=True)
        hits=[]
        for ti,tv in candidates:
            if affine_equiv_safe(q,tv,5): hits.append(ti)
        tested.append((g,a,c,d,[ti for ti,_ in candidates],hits,u,eps))
        if hits: bad.append((g,a,c,d,tt_hex(q),hits,u,eps))
    assert not bad,bad

    out={
      'checker':'essentialize one linear-structure direction; affine-invariant directional fingerprint; positive witnesses for dim6; hardened complete negative checker for fingerprint-matched dim5 cases',
      'inputs':{
        'mc4_dim8':{'lines':42,'git_blob_sha':SHA8},
        'mc4_dim7':{'lines':321,'git_blob_sha':SHA7},
        'mc4_dim5':{'lines':26,'git_blob_sha':SHA5},
        'mc3_dim6':{'lines':7,'git_blob_sha':SHA36},
      },
      'dim6_antiperiod_branch':{'dim8_counts':dict(c8),'dim6_zero_fiber_quotients':len(dim6),'all_mc3_or_less':True,'verified':dim6_verified},
      'dim5_antiperiod_branch':{'dim7_counts':dict(c7),'low_degree_dim5_zero_fiber_quotients':len(dim5_low),'mc4_dim5_matches':0,'tested':tested},
      'antiperiod_level4_obstructions_closed':True,
    }
    Path('/tmp/zlg_antiperiod.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_ANTIPERIOD_RESULT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_ANTIPERIOD_RESULT_END')
    print('LEVEL4_ANTIPERIOD_SECTORS_CLOSED')

if __name__=='__main__': main()

#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path
from zlg_finish_mc4 import (
    URL6, URL5, SHA6, SHA5, fetch, truth, degree, dim_invariant,
    rank, hyperplane_q, tt_hex,
)

def derivative(vals,u,n):
    return [vals[x]^vals[x^u] for x in range(1<<n)]

def direction_signature(vals,u,n):
    h=derivative(vals,u,n)
    w=sum(h)
    second=[]
    for v in range(1,1<<n):
        hh=derivative(h,v,n)
        second.append((degree(hh,n),sum(hh)))
    return (degree(h,n),min(w,(1<<n)-w),dim_invariant(h,n),tuple(sorted(second)))

def affine_equiv_safe(src,tgt,n,max_nodes=50_000_000):
    if degree(src,n)!=degree(tgt,n): return False
    N=1<<n
    basis=[1<<i for i in range(n)]
    ss={u:direction_signature(src,u,n) for u in range(1,N)}
    ts={v:direction_signature(tgt,v,n) for v in range(1,N)}
    cand={i:[v for v in range(1,N) if ts[v]==ss[basis[i]]] for i in range(n)}
    order=sorted(range(n),key=lambda i:len(cand[i]))
    chosen={}
    nodes=0
    def rec(pos):
        nonlocal nodes
        nodes+=1
        if nodes>max_nodes: raise RuntimeError(f'node limit {max_nodes}')
        if pos==n:
            for b in range(N):
                h=[]
                for x in range(N):
                    y=b
                    for i in range(n):
                        if (x>>i)&1: y^=chosen[i]
                    h.append(src[x]^tgt[y])
                if degree(h,n)<=1: return True
            return False
        i=order[pos]
        for v in cand[i]:
            vals=list(chosen.values())+[v]
            if rank(vals,n)!=len(vals): continue
            items=list(chosen.items())
            ok=True
            for mask in range(1<<len(items)):
                us=basis[i]; vt=v
                for j,(idx,vj) in enumerate(items):
                    if (mask>>j)&1:
                        us^=basis[idx]; vt^=vj
                if ss[us]!=ts[vt]:
                    ok=False; break
            if not ok: continue
            chosen[i]=v
            if rec(pos+1): return True
            del chosen[i]
        return False
    return rec(0)

def main():
    lines6=[x for x in fetch(URL6,SHA6) if x.strip()]
    lines5=[x for x in fetch(URL5,SHA5) if x.strip()]
    assert len(lines6)==888 and len(lines5)==26
    low5=[]; deg5_count=0
    for i,s in enumerate(lines5,1):
        v=truth(s,5); d=degree(v,5)
        if d==5: deg5_count+=1
        elif d in (3,4): low5.append((i,d,s,v))
        else: raise AssertionError((i,d,s))
    assert deg5_count==19 and len(low5)==7
    counts=Counter(); structural=[]; unique={}
    for gi,s in enumerate(lines6,1):
        vals=truth(s,6)
        for a in range(1,64):
            for c in (0,1):
                counts['hyperplanes']+=1
                q=hyperplane_q(vals,6,a,c)
                if q is None: continue
                counts['affine_restrictions']+=1
                d=degree(q,5); dim=dim_invariant(q,5)
                counts[f'deg{d}_dim{dim}']+=1
                if dim!=5 or d not in (3,4): continue
                counts['structural_survivors']+=1
                hx=tt_hex(q)
                structural.append((gi,a,c,d,hx)); unique.setdefault((d,hx),q)
    class_cache={}
    for (d,hx),q in unique.items():
        hits=[]
        for ti,td,ts,tv in low5:
            if td==d and affine_equiv_safe(q,tv,5): hits.append(ti)
        class_cache[(d,hx)]=hits
    matches=[]
    for gi,a,c,d,hx in structural:
        hits=class_cache[(d,hx)]
        if hits:
            matches.append({'source_mc4_dim6_rep':gi,'a':a,'c':c,'degree':d,'q_hex':hx,'mc4_dim5_classes':hits})
    out={
      'checker':'directional-derivative-signature complete backtracking + direct affine verification',
      'authoritative_inputs':{'mc4_dim6':{'lines':len(lines6),'git_blob_sha':SHA6},'mc4_dim5':{'lines':len(lines5),'git_blob_sha':SHA5}},
      'mc4_dim5_degree5_classes':deg5_count,
      'mc4_dim5_low_degree_classes':[{'index':i,'degree':d,'anf':s} for i,d,s,_ in low5],
      'counts':dict(counts),
      'unique_low_degree_dim5_quotients':len(unique),
      'mc4_dim5_matches':matches,
      'counterexample_count':len(matches),
      'lift_level4_dim5_closed':len(matches)==0,
    }
    Path('/tmp/zlg_result_safe.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_MC4_DIM6_TO_DIM5_SAFE_RESULT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC4_DIM6_TO_DIM5_SAFE_RESULT_END')
    print('COUNTEREXAMPLE_FOUND' if matches else 'DIM5_LOW_DEGREE_SECTOR_CLOSED_SAFE')

if __name__=='__main__': main()

#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, urllib.request
from collections import Counter
from pathlib import Path

URL6='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim6.txt'
URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim5.txt'
SHA6='dd99bf00f68a72dfe11f87f15de3c28bd15b4a5a'
SHA5='33498fd9058abb1edae1c040cd430cb4a8bf15e5'

def git_blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def fetch(url, expected):
    data=urllib.request.urlopen(url, timeout=30).read()
    got=git_blob_sha(data)
    if got!=expected: raise SystemExit(f'BLOB_SHA_MISMATCH expected={expected} got={got}')
    return data.decode().splitlines()

def parse_anf(s,n):
    mons=[]
    for term in s.strip().split('+'):
        if not term: continue
        m=0
        for x in re.findall(r'x(\d+)',term):
            j=int(x)-1
            if not 0<=j<n: raise ValueError((term,j,n))
            m|=1<<j
        mons.append(m)
    return mons

def truth(expr,n):
    mons=parse_anf(expr,n)
    return [sum((x&m)==m for m in mons)&1 for x in range(1<<n)]

def anf_coeffs(vals,n):
    a=vals[:]
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: a[m]^=a[m^bit]
    return a

def degree(vals,n):
    a=anf_coeffs(vals,n)
    return max((m.bit_count() for m,c in enumerate(a) if c),default=-1)

def dim_invariant(vals,n):
    cnt=0
    for u in range(1<<n):
        d0=vals[0]^vals[u]
        if all((vals[x]^vals[x^u])==d0 for x in range(1<<n)): cnt+=1
    if cnt&(cnt-1): raise AssertionError('linear structures not subspace')
    return n-(cnt.bit_length()-1)

def rank(rows,n):
    rows=list(rows); r=0
    for col in range(n):
        p=next((i for i in range(r,len(rows)) if (rows[i]>>col)&1),None)
        if p is None: continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(len(rows)):
            if i!=r and ((rows[i]>>col)&1): rows[i]^=rows[r]
        r+=1
    return r

def diff(vals,dirs,x=0):
    z=0
    for s in range(1<<len(dirs)):
        y=x
        for i,d in enumerate(dirs):
            if (s>>i)&1: y^=d
        z^=vals[y]
    return z

def d2(v,a,b,x=0): return diff(v,[a,b],x)
def d3(v,a,b,c,x=0): return diff(v,[a,b,c],x)
def d4(v,a,b,c,d,x=0): return diff(v,[a,b,c,d],x)

def d3_rank(vals,u,b,n):
    B=[1<<i for i in range(n)]
    return rank([sum(d3(vals,u,v,w,b)<<j for j,w in enumerate(B)) for v in B],n)

def d4_pair_rank(vals,u,v,n):
    B=[1<<i for i in range(n)]
    return rank([sum(d4(vals,u,v,w,t,0)<<j for j,t in enumerate(B)) for w in B],n)

def d4_sig(vals,u,n):
    return tuple(sorted(d4_pair_rank(vals,u,v,n) for v in range(1,1<<n)))

def affine_equiv_upto_affine(src,tgt,n,max_nodes=50_000_000):
    deg=degree(src,n)
    if deg!=degree(tgt,n): return False
    if deg<=1: return True
    B=[1<<i for i in range(n)]
    src_d3r=[d3_rank(src,e,0,n) for e in B] if deg>=3 else [0]*n
    if deg>=4:
        src_d4=[d4_sig(src,e,n) for e in B]
        tgt_d4={v:d4_sig(tgt,v,n) for v in range(1,1<<n)}
    else:
        src_d4=tgt_d4=None
    nodes=0
    for b in range(1<<n):
        tgt_d3r={v:d3_rank(tgt,v,b,n) for v in range(1,1<<n)} if deg>=3 else {v:0 for v in range(1,1<<n)}
        cand=[]
        for i in range(n):
            arr=[]
            for v in range(1,1<<n):
                if tgt_d3r[v]!=src_d3r[i]: continue
                if deg>=4 and tgt_d4[v]!=src_d4[i]: continue
                arr.append(v)
            cand.append(arr)
        order=sorted(range(n),key=lambda i:len(cand[i]))
        chosen={}; span=[]
        def independent(vs): return rank(vs,n)==len(vs)
        def rec(pos):
            nonlocal nodes
            nodes+=1
            if nodes>max_nodes: raise RuntimeError(f'node limit {max_nodes}')
            if pos==n: return dict(chosen)
            i=order[pos]
            for v in cand[i]:
                if not independent(span+[v]): continue
                ok=True
                for j,vj in chosen.items():
                    if d2(src,B[i],B[j],0)!=d2(tgt,v,vj,b): ok=False; break
                if not ok: continue
                items=list(chosen.items())
                if deg>=3:
                    for aa in range(len(items)):
                        j,vj=items[aa]
                        for bb in range(aa+1,len(items)):
                            k,vk=items[bb]
                            if d3(src,B[i],B[j],B[k],0)!=d3(tgt,v,vj,vk,b): ok=False; break
                        if not ok: break
                if not ok: continue
                if deg>=4:
                    for aa in range(len(items)):
                        j,vj=items[aa]
                        for bb in range(aa+1,len(items)):
                            k,vk=items[bb]
                            for cc in range(bb+1,len(items)):
                                l,vl=items[cc]
                                if d4(src,B[i],B[j],B[k],B[l],0)!=d4(tgt,v,vj,vk,vl,0): ok=False; break
                            if not ok: break
                        if not ok: break
                if not ok: continue
                chosen[i]=v; span.append(v)
                got=rec(pos+1)
                if got is not None: return got
                span.pop(); del chosen[i]
            return None
        mp=rec(0)
        if mp is None: continue
        h=[]
        for x in range(1<<n):
            y=b
            for i in range(n):
                if (x>>i)&1: y^=mp[i]
            h.append(src[x]^tgt[y])
        if degree(h,n)<=1: return True
    return False

def hyperplane_q(vals,n,a,c):
    p=(a&-a).bit_length()-1
    others=[j for j in range(n) if j!=p]
    m=n-1
    g0=[0]*(1<<m); g1=[0]*(1<<m)
    for y in range(1<<m):
        xb=0; parity=0
        for k,j in enumerate(others):
            bit=(y>>k)&1
            if bit: xb|=1<<j
            if ((a>>j)&1) and bit: parity^=1
        xp=c^parity
        x0=xb|(xp<<p); x1=x0^(1<<p)
        g0[y]=vals[x0]; g1[y]=vals[x1]
    if degree(g0,m)>1: return None
    return [u^v for u,v in zip(g0,g1)]

def tt_hex(vals):
    z=sum(b<<i for i,b in enumerate(vals))
    return f'{z:0{(len(vals)+3)//4}x}'

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
    counts=Counter(); structural=[]; unique={}; matches=[]
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
        hit=[]
        for ti,td,ts,tv in low5:
            if td==d and affine_equiv_upto_affine(q,tv,5): hit.append(ti)
        class_cache[(d,hx)]=hit
    for gi,a,c,d,hx in structural:
        hit=class_cache[(d,hx)]
        if hit: matches.append({'source_mc4_dim6_rep':gi,'a':a,'c':c,'degree':d,'q_hex':hx,'mc4_dim5_classes':hit})
    out={'authoritative_inputs':{'mc4_dim6':{'lines':len(lines6),'git_blob_sha':SHA6},'mc4_dim5':{'lines':len(lines5),'git_blob_sha':SHA5}},'mc4_dim5_degree5_classes':deg5_count,'mc4_dim5_low_degree_classes':[{'index':i,'degree':d,'anf':s} for i,d,s,_ in low5],'counts':dict(counts),'unique_low_degree_dim5_quotients':len(unique),'mc4_dim5_matches':matches,'counterexample_count':len(matches),'lift_level4_dim5_closed':len(matches)==0}
    Path('/tmp/zlg_result.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_MC4_DIM6_TO_DIM5_RESULT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_MC4_DIM6_TO_DIM5_RESULT_END')
    print('COUNTEREXAMPLE_FOUND' if matches else 'DIM5_LOW_DEGREE_SECTOR_CLOSED')

if __name__=='__main__': main()

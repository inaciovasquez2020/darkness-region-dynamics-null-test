#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path
from zlg_finish_mc4 import fetch, truth, degree, dim_invariant, hyperplane_q, tt_hex
from zlg_finish_mc4_safe import affine_equiv_safe

URL8='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
URL7='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim7.txt'
URL6='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim6.txt'
URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim5.txt'
URL36='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc3_dim6.txt'
SHA8='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'
SHA7='17acdd408959d178fdd0867cf27d777f0dcb5fb9'
SHA6='dd99bf00f68a72dfe11f87f15de3c28bd15b4a5a'
SHA5='33498fd9058abb1edae1c040cd430cb4a8bf15e5'
SHA36='16b37a3091a855610573d8de213c6eaf1cc6cab9'

def load(url,sha,expected):
    xs=[x for x in fetch(url,sha) if x.strip()]
    assert len(xs)==expected,(url,len(xs),expected)
    return xs

def sweep(lines,n):
    out=[]; counts=Counter()
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

def main():
    l8=load(URL8,SHA8,42)
    l7=load(URL7,SHA7,321)
    l6=load(URL6,SHA6,888)
    l5=load(URL5,SHA5,26)
    l36=load(URL36,SHA36,7)

    # dimension 7 -> hypothetical MC4 lift has dimension 8.
    c8,q8=sweep(l8,8)
    bad8=[(g,a,c,d,di,tt_hex(q)) for g,a,c,d,di,q in q8 if di==7]

    # dimension 6 -> hypothetical MC4 lift has dimension 7.
    c7,q7=sweep(l7,7)
    mc3d6=[]
    for i,s in enumerate(l36,1):
        v=truth(s,6); mc3d6.append((i,degree(v,6),v))
    relevant6=[]; unclassified6=[]
    cache6={}
    for g,a,c,d,di,q in q7:
        if di!=6: continue
        if d==2:
            relevant6.append((g,a,c,d,'quadratic-MC3'))
            continue
        if d not in (3,4): continue
        hx=tt_hex(q); key=(d,hx)
        if key not in cache6:
            hits=[]
            for ti,td,tv in mc3d6:
                if td==d and affine_equiv_safe(q,tv,6): hits.append(ti)
            cache6[key]=hits
        hits=cache6[key]
        relevant6.append((g,a,c,d,hits))
        if not hits: unclassified6.append((g,a,c,d,hx))

    # dimension 5 -> hypothetical MC4 lift has dimension 6.
    c6,q6=sweep(l6,6)
    mc4d5=[]; deg5_count=0
    for i,s in enumerate(l5,1):
        v=truth(s,5); d=degree(v,5)
        if d==5: deg5_count+=1
        elif d in (3,4): mc4d5.append((i,d,v,s))
        else: raise AssertionError((i,d,s))
    assert deg5_count==19 and len(mc4d5)==7
    relevant5=[]; bad5=[]; cache5={}
    for g,a,c,d,di,q in q6:
        if di!=5 or d not in (3,4): continue
        hx=tt_hex(q); key=(d,hx)
        if key not in cache5:
            hits=[]
            for ti,td,tv,ts in mc4d5:
                if td==d and affine_equiv_safe(q,tv,5): hits.append(ti)
            cache5[key]=hits
        hits=cache5[key]
        relevant5.append((g,a,c,d,hits))
        if hits: bad5.append((g,a,c,d,hx,hits))

    closed=(not bad8 and not unclassified6 and not bad5)
    out={
      'checker':'complete directional-derivative-signature backtracking with direct affine verification',
      'inputs':{
        'mc4_dim8':{'lines':42,'git_blob_sha':SHA8},
        'mc4_dim7':{'lines':321,'git_blob_sha':SHA7},
        'mc4_dim6':{'lines':888,'git_blob_sha':SHA6},
        'mc4_dim5':{'lines':26,'git_blob_sha':SHA5},
        'mc3_dim6':{'lines':7,'git_blob_sha':SHA36},
      },
      'dim8_to_dim7':{'counts':dict(c8),'dim7_quotients':len(bad8),'bad':bad8},
      'dim7_to_dim6':{'counts':dict(c7),'relevant_dim6_quotients':len(relevant6),'unclassified_against_mc3_dim6':len(unclassified6),'bad':unclassified6},
      'dim6_to_dim5':{'counts':dict(c6),'degree5_mc4_dim5_classes':deg5_count,'low_degree_mc4_dim5_classes':len(mc4d5),'relevant_dim5_low_degree_quotients':len(relevant5),'unique_relevant_quotients':len(cache5),'mc4_dim5_matches':len(bad5),'bad':bad5},
      'level4_lift_closed':closed,
    }
    Path('/tmp/zlg_level4_complete.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_LEVEL4_COMPLETE_RESULT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_LEVEL4_COMPLETE_RESULT_END')
    print('LEVEL4_LIFT_CLOSED' if closed else 'LEVEL4_LIFT_NOT_CLOSED')
    if not closed: raise SystemExit(2)

if __name__=='__main__': main()

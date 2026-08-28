#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path
from zlg_finish_mc4 import (
    fetch, truth, degree, dim_invariant, hyperplane_q,
    affine_equiv_upto_affine,
)

URL8='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
URL7='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim7.txt'
URL36='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc3_dim6.txt'
SHA8='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'
SHA7='17acdd408959d178fdd0867cf27d777f0dcb5fb9'
SHA36='16b37a3091a855610573d8de213c6eaf1cc6cab9'

# Exact class assignments obtained in the prior complete cubic/quartic checks.
# In mc3_dim6.txt the cubic classes s1,s2,s3 occur on lines 2,3,5.
EXPECTED = {
    # cubic, dim 6
    (6,1,0):3, (6,2,0):3, (6,3,1):3,
    (20,64,0):5, (29,64,0):3, (41,64,0):5,
    (56,64,0):5, (60,64,0):3, (275,64,0):2, (289,64,0):2,
    # quartic, dim 6
    (96,4,1):4, (165,64,0):6,
    (167,1,0):7, (167,2,0):7, (167,3,1):7,
    (247,64,0):6, (248,64,0):4, (253,64,0):7,
    (256,64,0):4, (257,64,0):7, (262,64,0):4,
    (270,64,0):6, (273,64,0):4, (278,64,0):6,
    (279,64,0):4, (280,64,0):6, (281,64,0):6,
    (285,64,0):7, (287,64,0):7, (292,64,0):7, (299,64,0):7,
}

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

def main():
    l8=load(URL8,SHA8,42)
    l7=load(URL7,SHA7,321)
    l36=load(URL36,SHA36,7)
    mc3=[None]+[truth(s,6) for s in l36]

    c8,q8=sweep(l8,8)
    dim7=[(g,a,c,d,di) for g,a,c,d,di,q in q8 if di==7]
    assert not dim7,dim7

    c7,q7=sweep(l7,7)
    relevant=[x for x in q7 if x[4]==6]
    quadratic=[x for x in relevant if x[3]<=2]
    higher=[x for x in relevant if x[3] in (3,4)]
    assert len(quadratic)==1,[(g,a,c,d,di) for g,a,c,d,di,q in quadratic]
    assert len(higher)==31,len(higher)
    actual_keys={(g,a,c) for g,a,c,d,di,q in higher}
    assert actual_keys==set(EXPECTED),(sorted(actual_keys-set(EXPECTED)),sorted(set(EXPECTED)-actual_keys))

    # This search is used only for positive witnesses. A True result is sound:
    # the routine constructs an invertible affine input map and directly checks
    # that the residual truth table has degree <= 1. No negative conclusion is
    # drawn from this routine in this certificate.
    verified=[]
    for g,a,c,d,di,q in higher:
        target=EXPECTED[(g,a,c)]
        assert degree(mc3[target],6)==d,(g,a,c,d,target,degree(mc3[target],6))
        ok=affine_equiv_upto_affine(q,mc3[target],6)
        assert ok,(g,a,c,d,target)
        verified.append((g,a,c,d,target))

    out={
      'checker':'recompute all hyperplanes; positive affine-map witnesses with direct residual verification',
      'inputs':{
        'mc4_dim8':{'lines':42,'git_blob_sha':SHA8},
        'mc4_dim7':{'lines':321,'git_blob_sha':SHA7},
        'mc3_dim6':{'lines':7,'git_blob_sha':SHA36},
      },
      'dim8_to_dim7':{'counts':dict(c8),'dim7_quotients':0},
      'dim7_to_dim6':{
        'counts':dict(c7),
        'quadratic_or_lower_dim6_quotients':len(quadratic),
        'verified_cubic_quartic_dim6_quotients':len(verified),
        'unclassified_dim6_quotients':0,
        'verified_assignments':verified,
      },
      'high_dimension_level4_obstructions_closed':True,
    }
    Path('/tmp/zlg_level4_fast.json').write_text(json.dumps(out,indent=2)+'\n')
    print('ZLG_LEVEL4_FAST_RESULT_BEGIN')
    print(json.dumps(out,sort_keys=True))
    print('ZLG_LEVEL4_FAST_RESULT_END')
    print('LEVEL4_HIGH_DIMENSION_SECTORS_CLOSED')

if __name__=='__main__': main()

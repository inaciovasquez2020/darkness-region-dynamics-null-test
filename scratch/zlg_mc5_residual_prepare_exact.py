#!/usr/bin/env python3
import sys
from collections import defaultdict
from itertools import product
from pathlib import Path

from zlg_mc5_residual_fingerprint import (
    residual, mobius_degree, dimension, fingerprint, to_anf, parse_anf
)


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: prep mc3_dim6.txt mc4_dim6.txt')
    l3=[s.strip() for s in Path(sys.argv[1]).read_text().splitlines() if s.strip()]
    l4=[s.strip() for s in Path(sys.argv[2]).read_text().splitlines() if s.strip()]
    assert len(l3)==7 and len(l4)==888,(len(l3),len(l4))

    low=[]
    for mc,lines in ((3,l3),(4,l4)):
        for line_no,s in enumerate(lines,1):
            tt=parse_anf(s)
            assert dimension(tt)==6
            low.append((mc,line_no,s,fingerprint(tt)))
    buckets=defaultdict(list)
    for mc,line_no,s,fp in low:
        buckets[fp].append((mc,line_no,s))

    reps={}
    for bits in product((0,1),repeat=11):
        zero,f=residual(bits)
        assert zero==0
        if mobius_degree(f)==4 and dimension(f)==6:
            reps.setdefault(f,bits)
    assert len(reps)==512,len(reps)

    rows=[]
    for idx,(f,bits) in enumerate(sorted(reps.items()),1):
        hits=buckets[fingerprint(f)]
        assert len(hits)==1,(idx,bits,len(hits))
        mc,line_no,target=hits[0]
        rows.append((idx,mc,line_no,to_anf(f),target,''.join(map(str,bits))))

    Path('/tmp/zlg_mc5_residual_exact_pairs.tsv').write_text(
        '\n'.join(f'{i}\t{mc}\t{ln}\t{src}\t{tgt}\t{bits}' for i,mc,ln,src,tgt,bits in rows)+'\n'
    )
    c3=sum(mc==3 for _,mc,_,_,_,_ in rows)
    c4=sum(mc==4 for _,mc,_,_,_,_ in rows)
    print(f'EXACT_PAIR_PREP candidates={len(rows)} mc3_targets={c3} mc4_targets={c4}')

if __name__=='__main__':
    main()

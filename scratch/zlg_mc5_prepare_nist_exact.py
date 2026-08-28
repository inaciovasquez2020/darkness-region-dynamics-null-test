#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

UNRESOLVED={75:[3],284:[42],285:[41],286:[17],288:[37,38],290:[39],291:[14],295:[7],314:[5],315:[35],316:[21],317:[18],318:[8],443:[36],444:[33],533:[27],535:[40],537:[34],538:[26],565:[28],566:[24]}

def parse(s):
    S=set()
    for term in s.strip().split('+'):
        if not term: continue
        m=0
        for v in re.findall(r'x(\d+)',term): m|=1<<(int(v)-1)
        if m in S:S.remove(m)
        else:S.add(m)
    return S

def compact(mask,p): return (mask&((1<<p)-1))|((mask>>(p+1))<<p)
def toggle(S,m):
    if m in S:S.remove(m)
    else:S.add(m)
def source_h(line):
    # Coefficient of x9; remove the compact anti-period x10 affine direction.
    q=set()
    for m in parse(line):
        if (m>>8)&1: toggle(q,compact(m&~(1<<8),8))
    h={m for m in q if m.bit_count()>=2}
    assert all(not ((m>>8)&1) for m in h)
    return h

def anf(S,n=8):
    if not S:return '0'
    out=[]
    for m in sorted(S,key=lambda z:(z.bit_count(),z)):
        if m==0:out.append('1');continue
        out.append(''.join(f'x{i+1}' for i in range(n) if (m>>i)&1))
    return '+'.join(out)

def main():
    if len(sys.argv)!=3: raise SystemExit('usage: prep mc5_dim10.txt mc4_dim8.txt')
    l5=[x.strip() for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
    l4=[x.strip() for x in Path(sys.argv[2]).read_text().splitlines() if x.strip()]
    assert len(l5)==575 and len(l4)==42
    rows=[]
    for gi,targets in UNRESOLVED.items():
        s=anf(source_h(l5[gi-1]))
        for ti in targets:
            rows.append((gi,ti,s,l4[ti-1]))
    Path('/tmp/zlg_mc5_nist_pairs.tsv').write_text('\n'.join(f'{g}\t{t}\t{s}\t{u}' for g,t,s,u in rows)+'\n')
    print(json.dumps({'source_cases':len(UNRESOLVED),'pair_attempts':len(rows)},sort_keys=True))
if __name__=='__main__':main()

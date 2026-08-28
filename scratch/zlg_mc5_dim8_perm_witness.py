#!/usr/bin/env python3
import hashlib, itertools, json, re, urllib.request
from pathlib import Path

URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc5_dim10.txt'
SHA5='ed42b4f9bb113914122210963d07ac124d6695a9'
URL4='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
SHA4='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'
ASSIGN={8:[1],68:[19],70:[30],74:[31],75:[3],86:[4],102:[10],284:[42],285:[41],286:[17],288:[37,38],289:[37,38],290:[39],291:[14],292:[15],293:[13],294:[16],295:[7],296:[12],314:[5],315:[35],316:[21],317:[18],318:[8],320:[9],323:[2],443:[36],444:[33],445:[23],532:[32],533:[27],535:[40],536:[29],537:[34],538:[26],561:[25],562:[20],563:[22],564:[11],565:[28],566:[24],568:[6]}

def blob_sha(d):
 h=hashlib.sha1(); h.update(f'blob {len(d)}\0'.encode()); h.update(d); return h.hexdigest()
def get(url,sha):
 d=urllib.request.urlopen(url,timeout=30).read(); assert blob_sha(d)==sha; return [x for x in d.decode().splitlines() if x.strip()]
def parse(s):
 S=set()
 for term in s.split('+'):
  m=0
  for v in re.findall(r'x(\d+)',term):m|=1<<(int(v)-1)
  if m in S:S.remove(m)
  else:S.add(m)
 return S
def compact(mask,p):return (mask&((1<<p)-1))|((mask>>(p+1))<<p)
def toggle(S,m):
 if m in S:S.remove(m)
 else:S.add(m)
def quotient_x9(source):
 # coefficient of x9 in 10-variable ANF -> 9-variable q
 S=set()
 for m in source:
  if (m>>8)&1: toggle(S,compact(m&~(1<<8),8))
 return S
def essential_x10(q):
 # In every certified candidate, x10 compacted to bit8 is an anti-period.
 # q = h(x1..x8) + x9, up to affine terms; remove all affine terms and bit8.
 h=set()
 for m in q:
  if m.bit_count()<=1: continue
  assert not ((m>>8)&1), ('nonlinear anti-period variable',m)
  h.add(m)
 return h
def nonlinear(S): return {m for m in S if m.bit_count()>=2}
def perm_mask(m,p):
 out=0
 for i in range(8):
  if (m>>i)&1:out|=1<<p[i]
 return out
def find_perm(src_nonlin,tgt_nonlin):
 # Degree histogram is cheap guard.
 if sorted(m.bit_count() for m in src_nonlin)!=sorted(m.bit_count() for m in tgt_nonlin):return None
 for p in itertools.permutations(range(8)):
  if {perm_mask(m,p) for m in src_nonlin}==tgt_nonlin:return p
 return None
def main():
 l5=get(URL5,SHA5); l4=get(URL4,SHA4); assert len(l5)==575 and len(l4)==42
 targets=[None]+[nonlinear(parse(s)) for s in l4]
 verified=[]; unresolved=[]
 for gi,choices in ASSIGN.items():
  h=essential_x10(quotient_x9(parse(l5[gi-1])))
  found=None
  for ti in choices:
   p=find_perm(h,targets[ti])
   if p is not None:
    found={'source_rep':gi,'target_mc4_dim8':ti,'permutation':list(p)};break
  if found: verified.append(found); print('PERM_VERIFIED',gi,'->',found['target_mc4_dim8'],found['permutation'])
  else: unresolved.append({'source_rep':gi,'targets':choices})
 out={'inputs':{'mc5_dim10':{'sha':SHA5,'lines':len(l5)},'mc4_dim8':{'sha':SHA4,'lines':len(l4)}},'verified_by_variable_permutation_plus_affine_output':len(verified),'unresolved_count':len(unresolved),'verified':verified,'unresolved':unresolved}
 Path('/tmp/zlg_mc5_dim8_perm.json').write_text(json.dumps(out,indent=2)+'\n')
 print('ZLG_MC5_DIM8_PERM_BEGIN');print(json.dumps(out,sort_keys=True));print('ZLG_MC5_DIM8_PERM_END')

if __name__=='__main__':main()

#!/usr/bin/env python3
import hashlib, json, re, urllib.request
from collections import deque
from pathlib import Path

URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc5_dim10.txt'
SHA5='ed42b4f9bb113914122210963d07ac124d6695a9'
URL4='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
SHA4='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'
ASSIGN={8:[1],68:[19],70:[30],74:[31],75:[3],86:[4],102:[10],284:[42],285:[41],286:[17],288:[37,38],289:[37,38],290:[39],291:[14],292:[15],293:[13],294:[16],295:[7],296:[12],314:[5],315:[35],316:[21],317:[18],318:[8],320:[9],323:[2],443:[36],444:[33],445:[23],532:[32],533:[27],535:[40],536:[29],537:[34],538:[26],561:[25],562:[20],563:[22],564:[11],565:[28],566:[24],568:[6]}


def blob_sha(d):
 h=hashlib.sha1();h.update(f'blob {len(d)}\0'.encode());h.update(d);return h.hexdigest()
def get(url,sha):
 d=urllib.request.urlopen(url,timeout=30).read();assert blob_sha(d)==sha;return [x for x in d.decode().splitlines() if x.strip()]
def parse(s):
 S=set()
 for term in s.split('+'):
  m=0
  for v in re.findall(r'x(\d+)',term):m|=1<<(int(v)-1)
  if m in S:S.remove(m)
  else:S.add(m)
 return frozenset(S)
def compact(mask,p):return (mask&((1<<p)-1))|((mask>>(p+1))<<p)
def toggle(S,m):
 if m in S:S.remove(m)
 else:S.add(m)
def source_h(line):
 # For all 42 dimension-10 affine-zero-fiber cases, G=x9*q and q has only
 # affine dependence on compact x10. The essential nonlinear h is exactly the
 # nonlinear coefficient of x9 after removing that affine direction.
 q=set()
 for m in parse(line):
  if (m>>8)&1:toggle(q,compact(m&~(1<<8),8))
 h={m for m in q if m.bit_count()>=2}
 assert all(not ((m>>8)&1) for m in h)
 return frozenset(h)
def nonlinear(S):return frozenset(m for m in S if m.bit_count()>=2)
def apply_gen(state,g,keep_affine=False):
 typ,i,j=g;out=set()
 def tog(m):
  if m in out:out.remove(m)
  else:out.add(m)
 if typ=='s':
  for m in state:
   tog(m)
   if (m>>i)&1:
    m2=(m&~(1<<i))|(1<<j)
    tog(m2)
 elif typ=='p':
  bi=1<<i;bj=1<<j
  for m in state:
   ni=(m>>i)&1;nj=(m>>j)&1;m2=m&~(bi|bj)
   if ni:m2|=bj
   if nj:m2|=bi
   tog(m2)
 else:raise ValueError(g)
 if not keep_affine:out={m for m in out if m.bit_count()>=2}
 return frozenset(out)
GENS=[('s',i,j) for i in range(8) for j in range(8) if i!=j]+[('p',i,j) for i in range(8) for j in range(i+1,8)]

def radius(root,depth):
 seen={root:()};front=[root]
 for _ in range(depth):
  new=[]
  for st in front:
   seq=seen[st]
   for g in GENS:
    z=apply_gen(st,g)
    if z not in seen:
     seen[z]=seq+(g,);new.append(z)
  front=new
 return seen

def find_short(src,tgt):
 if src==tgt:return ()
 # radius 2 + radius 2 covers <=4 elementary generators.
 T=radius(tgt,2)
 S=radius(src,2)
 common=set(T).intersection(S)
 if common:
  # generators are involutions, so reverse target path.
  m=min(common,key=lambda x:len(S[x])+len(T[x]))
  return S[m]+tuple(reversed(T[m]))
 # Escalate source side to radius 3, target remains radius 2 => <=5.
 front=[st for st,seq in S.items() if len(seq)==2]
 seen=dict(S)
 for st in front:
  seq=seen[st]
  for g in GENS:
   z=apply_gen(st,g)
   if z in seen:continue
   seen[z]=seq+(g,)
   if z in T:return seen[z]+tuple(reversed(T[z]))
 return None
def verify_full(src_full,tgt_full,seq):
 st=src_full
 for g in seq:st=apply_gen(st,g,keep_affine=True)
 diff=set(st)^set(tgt_full)
 return all(m.bit_count()<=1 for m in diff),sorted(diff)
def main():
 l5=get(URL5,SHA5);l4=get(URL4,SHA4);targets=[None]+[parse(s) for s in l4]
 verified=[];unresolved=[]
 for gi,choices in ASSIGN.items():
  src_non=source_h(l5[gi-1]);found=None
  # source full essential polynomial differs from src_non only by affine terms,
  # which are irrelevant and stay affine under linear generators.
  for ti in choices:
   seq=find_short(src_non,nonlinear(targets[ti]))
   if seq is None:continue
   ok,diff=verify_full(src_non,targets[ti],seq)
   assert ok,(gi,ti,seq,diff)
   found={'source_rep':gi,'target_mc4_dim8':ti,'generator_count':len(seq),'generators':[list(g) for g in seq],'residual_affine_monomials':diff};break
  if found:
   verified.append(found);print('SHEAR_VERIFIED',gi,'->',found['target_mc4_dim8'],'len',found['generator_count'],found['generators'])
  else:unresolved.append({'source_rep':gi,'targets':choices})
 out={'inputs':{'mc5_dim10':{'sha':SHA5,'lines':len(l5)},'mc4_dim8':{'sha':SHA4,'lines':len(l4)}},'generator_set':'56 transvections xi<-xi+xj plus 28 swaps; all involutions','verified_count':len(verified),'unresolved_count':len(unresolved),'verified':verified,'unresolved':unresolved,'all_42_short_linear_witnesses':len(verified)==42,'dim8_antiperiod_level5_sector_closed':len(verified)==42}
 Path('/tmp/zlg_mc5_dim8_shear.json').write_text(json.dumps(out,indent=2)+'\n')
 print('ZLG_MC5_DIM8_SHEAR_BEGIN');print(json.dumps(out,sort_keys=True));print('ZLG_MC5_DIM8_SHEAR_END')

if __name__=='__main__':main()

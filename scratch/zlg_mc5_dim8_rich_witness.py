#!/usr/bin/env python3
import hashlib, json, re, urllib.request
from functools import lru_cache
from pathlib import Path

URL5='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc5_dim10.txt'
SHA5='ed42b4f9bb113914122210963d07ac124d6695a9'
URL4='https://raw.githubusercontent.com/usnistgov/Circuits/master/data/mc_dim/mc4_dim8.txt'
SHA4='e2750dd6b5c9a0771de80c117939ea47f8f1bf37'
N=8
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
 return S
def compact(mask,p):return (mask&((1<<p)-1))|((mask>>(p+1))<<p)
def toggle(S,m):
 if m in S:S.remove(m)
 else:S.add(m)
def truth(S,n):return [sum((x&m)==m for m in S)&1 for x in range(1<<n)]
def quotient_x9(source):
 S=set()
 for m in source:
  if (m>>8)&1:toggle(S,compact(m&~(1<<8),8))
 return S
def structures(vals,n):
 out=[]
 for u in range(1<<n):
  d=vals[0]^vals[u]
  if all((vals[x]^vals[x^u])==d for x in range(1<<n)):out.append((u,d))
 return out
def embed(y,p):return (y&((1<<p)-1))|((y>>p)<<(p+1))
def essential_h(line):
 q=truth(quotient_x9(parse(line)),9);ss=structures(q,9);assert len(ss)==2,ss
 u,eps=next(z for z in ss if z[0]);assert eps==1
 p=(u&-u).bit_length()-1;h=[]
 for y in range(1<<8):
  x=embed(y,p);h.append(q[x]);assert q[x^u]==(q[x]^1)
 assert len(structures(h,8))==1
 return h,u
def mobius_degree(vals,n):
 a=vals[:]
 for i in range(n):
  b=1<<i
  for m in range(1<<n):
   if m&b:a[m]^=a[m^b]
 return max((m.bit_count() for m,c in enumerate(a) if c),default=-1)
def derivative(vals,u):return [vals[x]^vals[x^u] for x in range(len(vals))]
def minweight(vals):
 w=sum(vals);return min(w,len(vals)-w)
def linstruct_dim(vals,n):
 sz=len(structures(vals,n));return n-(sz.bit_length()-1)
def rich_signatures(vals):
 Nn=8;M=1<<Nn
 ds=[None]*M
 for u in range(1,M):ds[u]=derivative(vals,u)
 sig=[None]*M
 for u in range(1,M):
  du=ds[u]
  second=tuple(sorted(minweight([du[x]^du[x^v] for x in range(M)]) for v in range(1,M)))
  sig[u]=(mobius_degree(du,Nn),minweight(du),linstruct_dim(du,Nn),second)
 return sig
def is_affine(vals):
 c=vals[0];bits=0
 for i in range(N):
  if vals[1<<i]^c:bits|=1<<i
 for x,v in enumerate(vals):
  if (c^((bits&x).bit_count()&1))!=v:return None
 return {'constant':c,'linear_bits':bits}
def find_map(src,tgt,max_nodes=20_000_000):
 ss=rich_signatures(src);ts=rich_signatures(tgt);basis=[1<<i for i in range(N)]
 # Global signature multiset is a necessary equivalence condition.
 assert sorted(ss[1:])==sorted(ts[1:])
 buckets={}
 for e in basis:buckets[e]=[v for v in range(1,1<<N) if ts[v]==ss[e]]
 order=sorted(basis,key=lambda e:len(buckets[e]))
 chosen={};span={0:0};nodes=0
 def rec(pos):
  nonlocal nodes,span
  nodes+=1
  if nodes>max_nodes:raise RuntimeError(f'node limit {max_nodes}')
  if pos==N:
   amap=[span[x] for x in range(1<<N)]
   for b in range(1<<N):
    diff=[src[x]^tgt[amap[x]^b] for x in range(1<<N)]
    aff=is_affine(diff)
    if aff is not None:return {'translation':b,'basis_images':[chosen[1<<i] for i in range(N)],'affine_output':aff,'nodes':nodes}
   return None
  e=order[pos];old=dict(span);vals=set(old.values())
  for v in buckets[e]:
   if v in vals:continue
   if any(ss[s^e]!=ts[t^v] for s,t in old.items()):continue
   chosen[e]=v;new=dict(old)
   for s,t in old.items():new[s^e]=t^v
   span=new
   z=rec(pos+1)
   if z is not None:return z
   span=old;del chosen[e]
  return None
 return rec(0)
def main():
 l5=get(URL5,SHA5);l4=get(URL4,SHA4);targets=[None]+[truth(parse(s),8) for s in l4]
 verified=[]
 for gi,choices in ASSIGN.items():
  h,u=essential_h(l5[gi-1]);found=None
  for ti in choices:
   # Fast fingerprint mismatch skip; rich global signature asserts exact necessary match.
   try:w=find_map(h,targets[ti])
   except AssertionError:w=None
   if w is not None:
    found={'source_rep':gi,'target_mc4_dim8':ti,'anti_period_structure':u,'witness':w};break
  if found is None:raise AssertionError((gi,choices,'no rich affine witness'))
  verified.append(found);print('RICH_VERIFIED',gi,'->',found['target_mc4_dim8'],'nodes',found['witness']['nodes'])
 out={'inputs':{'mc5_dim10':{'sha':SHA5,'lines':len(l5)},'mc4_dim8':{'sha':SHA4,'lines':len(l4)}},'verified_count':len(verified),'all_42_verified':len(verified)==42,'verified':verified,'dim8_antiperiod_level5_sector_closed':len(verified)==42}
 Path('/tmp/zlg_mc5_dim8_rich.json').write_text(json.dumps(out,indent=2)+'\n')
 print('ZLG_MC5_DIM8_RICH_BEGIN');print(json.dumps(out,sort_keys=True));print('ZLG_MC5_DIM8_RICH_END')

if __name__=='__main__':main()

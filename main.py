import json as J,os,sys,urllib.request as U2
U=os.environ.get("MAKEFUN_ENV_URL") or sys.exit("no env")
A="abcdefgh"
Q="qrbn"
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":0}
D={"n":[(-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2)],"b":[(-1,-1),(-1,1),(1,-1),(1,1)],"r":[(-1,0),(1,0),(0,-1),(0,1)],"q":[(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]}
def post(p,b):
 r=U2.Request(U+p,data=J.dumps(b).encode(),headers={"content-type":"application/json"})
 return J.load(U2.urlopen(r))
def bd(fen):
 b={}
 for i,r in enumerate(fen.split()[0].split("/")):
  f=0
  for c in r:
   if c.isdigit():f+=int(c)
   else:b[8*i+f]=c;f+=1
 return b
def mvgen(b,w):
 ms=[]
 for s,p in b.items():
  lo=p.lower()
  P=p.isupper()
  if P!=w:continue
  r,c=divmod(s,8)
  if lo=="p":
   dr=-1 if p.isupper() else 1
   st=r+dr
   if 0<=st<8 and st*8+c not in b:
    e=st*8+c
    if st in(0,7):
     ms+=[(s,e,x) for x in Q]
    else:
     ms.append((s,e))
     sr=6 if p.isupper() else 1
     if r==sr and (r+2*dr)*8+c not in b:ms.append((s,(r+2*dr)*8+c))
   for dc in(-1,1):
    if c+dc>=0 and c+dc<8 and 0<=st<8:
     e=st*8+c+dc
     t=b.get(e)
     if t and t.isupper()!=P:
      if st in(0,7):ms+=[(s,e,x) for x in Q]
      else:ms.append((s,e))
  elif lo=="k":
   for d in D["q"]:
    nr,nc=r+d[0],c+d[1]
    if 0<=nr<8 and 0<=nc<8:
     e=nr*8+nc;t=b.get(e)
     if not t or t.isupper()!=P:ms.append((s,e))
  else:
   for d in D[lo]:
    nr,nc=r+d[0],c+d[1]
    while 0<=nr<8 and 0<=nc<8:
     e=nr*8+nc;t=b.get(e)
     if not t:ms.append((s,e))
     else:
      if t.isupper()!=P:ms.append((s,e))
      break
     if lo in"brq":nr+=d[0];nc+=d[1]
     else:break
 return ms
def ksq(b,w):
 for s,p in b.items():
  if p=="K" if w else p=="k":return s
def attack(b,s,w):
 r,c=divmod(s,8)
 for d in D["n"]:
  nr,nc=r+d[0],c+d[1]
  p=b.get(nr*8+nc) if 0<=nr<8 and 0<=nc<8 else 0
  if p and p.lower()=="n" and p.isupper()==w:return 1
 for d in D["q"]:
  dg=d[0]!=0 and d[1]!=0
  nr,nc=r+d[0],c+d[1]
  while 0<=nr<8 and 0<=nc<8:
   p=b.get(nr*8+nc)
   if p:
    if p.isupper()==w and(p.lower()=="q" or p.lower()==("b" if dg else "r")):return 1
    break
   nr+=d[0];nc+=d[1]
 for dc in(-1,1):
  nr=r+(-1 if w else 1)
  p=b.get(nr*8+c+dc) if 0<=nr<8 and 0<=c+dc<8 else 0
  if p and p.lower()=="p" and p.isupper()==w:return 1
 return 0
def legal(b,w,lm=None):
 out=[]
 if ksq(b,w) is None:return out
 for m in (lm if lm is not None else mvgen(b,w)):
  a=m[0];e=m[1]
  nb=dict(b)
  p=nb.pop(a);cap=nb.get(e)
  nb[e]=(Q[m[2]] if w else Q[m[2]].upper()) if len(m)>2 else p
  if p.lower()=="p" and cap is None and a%8!=e%8:nb.pop(e+(8 if w else -8),None)
  k=e if p.lower()=="k" else ksq(nb,w)
  if k is not None and not attack(nb,k,not w):out.append(m)
 return out
def ev(b):
 s=0
 for sq,p in b.items():
  r,c=divmod(sq,8)
  v=V[p.lower()]+abs(3.5-r)*2
  s+=v if p.isupper() else -v
 return s
def apply(b,m,w):
 a=m[0];e=m[1]
 p=b.pop(a);b[e]=(Q[m[2]] if w else Q[m[2]].upper()) if len(m)>2 else p
 if p.lower()=="p" and e not in b and a%8!=e%8:b.pop(e+(8 if w else -8),None)
def srch(b,w,d,al,be,lm=None):
 if d==0:return ev(b) if w else -ev(b)
 ms=legal(b,w,lm)
 if not ms:return -9e9+d
 bst=-9e9
 for m in ms:
  nb=dict(b);apply(nb,m,w)
  sc=-srch(nb,not w,d-1,-be,-al)
  if sc>bst:bst=sc
  if sc>al:al=sc
  if al>=be:break
 return bst
def ci(c):return A.find(c[0])+(8-int(c[1]))*8
def toint(m):return (ci(m[:2]),ci(m[2:4]))+((Q.index(m[4]),) if len(m)>4 else ())
def back(m):
 a=m[0];e=m[1]
 r=A[a%8]+str(8-a//8)+A[e%8]+str(8-e//8)
 if len(m)>2:r+=Q[m[2]]
 return r
while 1:
 g=post("/game",{})
 if g["status"]=="done":
  print(f"done {g.get('wins')}w {g.get('draws')}d {g.get('losses')}l",file=sys.stderr);break
 while g["status"]=="your_move":
  f=g["fen"];w=f.split()[1]=="w"
  bm=bd(f)
  lm=[toint(m) for m in g["legal_moves"]]
  lm=legal(bm,w,lm)
  best=None;bv=-9e9;al=-9e9
  D2=4 if len(bm)<14 else 3
  for m in lm:
   nb=dict(bm);apply(nb,m,w)
   sc=-srch(nb,not w,D2,-9e9,-al)
   if sc>bv:bv=sc;best=m
   if sc>al:al=sc
  g=post("/move",{"game":g["game"],"move":back(best)})
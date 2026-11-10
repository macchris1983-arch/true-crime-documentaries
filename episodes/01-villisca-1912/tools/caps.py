import json,re,os,numpy as np
TL=json.load(open('tl.json'));FPS=24;start={}
for a in TL:start.setdefault(a['ch'],a['t'])
SR=48000
src=open('/home/claude/villisca_vo_source.txt').read();p=re.split(r'=== CHUNK (\w+) ===\n',src)[1:]
fmt=lambda t:"%02d:%02d:%02d,%03d"%(t//3600,t//60%60,t%60,(t%1)*1000)
out=[];k=1;chap={}
from lines import line_times
for n,b in zip(p[0::2],p[1::2]):
    LT,_=line_times(n,b);L=[x[0] for x in LT];seg=[(x[1],x[2]) for x in LT]
    for l,(a,bb) in zip(L,seg):
        out.append(f"{k}\n{fmt(start[n]+a)} --> {fmt(start[n]+max(bb,a+0.6))}\n{l}\n");k+=1
    chap[n]=start[n]
open('/home/claude/Villisca_1912_captions.srt','w').write("\n".join(out))
json.dump(chap,open('chap.json','w'));print(k-1,'captions');print({c:"%d:%02d"%(t//60,t%60) for c,t in chap.items()})

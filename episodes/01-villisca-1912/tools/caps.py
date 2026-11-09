import json,re,os,numpy as np
TL=json.load(open('tl.json'));FPS=24;start={}
for a in TL:start.setdefault(a['ch'],a['t'])
SR=48000
src=open('/home/claude/villisca_vo_source.txt').read();p=re.split(r'=== CHUNK (\d+) ===\n',src)[1:]
fmt=lambda t:"%02d:%02d:%02d,%03d"%(t//3600,t//60%60,t%60,(t%1)*1000)
out=[];k=1;chap={}
for n,b in zip(p[0::2],p[1::2]):
    L=[re.sub(r'\[[^\]]+\]\s*','',l).replace('...','').strip() for l in b.strip().splitlines() if l.strip()!='[pause]']
    L=[l for l in L if l]
    x=np.fromfile(f"voice2/{n}.pcm",dtype=np.int16).astype(float);fl=int(.02*SR);kk=len(x)//fl
    r=np.sqrt((x[:kk*fl].reshape(kk,fl)**2).mean(1));q=r<max(10**(-42/20)*32768,np.percentile(r,5)*2)
    gaps=[];i=0
    while i<kk:
        if q[i]:
            j=i
            while j<kk and q[j]:j+=1
            if (j-i)*.02>=.2:gaps.append((i*.02,j*.02))
            i=j
        else:i+=1
    s0=gaps[0][1] if gaps and gaps[0][0]==0 else 0
    e0=gaps[-1][0] if gaps and gaps[-1][1]>=kk*.02-.05 else kk*.02
    inner=[g for g in gaps if g[0]>s0 and g[1]<e0]
    w=np.array([len(l.split()) for l in L],float);cum=np.cumsum(w)[:-1]/w.sum()
    # map speech-time fraction to boundaries, snap to nearest unused gap
    sp=np.cumsum(~q)*.02;tot=sp[-1]
    def at(f):
        idx=np.searchsorted(sp,f*tot);return idx*.02
    bounds=[];used=set()
    for f in cum:
        t=at(f);c=[(abs((g[0]+g[1])/2-t),ii) for ii,g in enumerate(inner) if ii not in used and (not bounds or g[0]>bounds[-1][1]-1e-6)]
        if c and min(c)[0]<1.5:
            ii=min(c)[1];used.add(ii);bounds.append(inner[ii])
        else:bounds.append((t,t))
    seg=[];st=s0
    for g in bounds:seg.append((st,g[0]));st=g[1]
    seg.append((st,e0))
    for l,(a,bb) in zip(L,seg):
        out.append(f"{k}\n{fmt(start[n]+a)} --> {fmt(start[n]+max(bb,a+0.6))}\n{l}\n");k+=1
    chap[n]=start[n]
open('/home/claude/Villisca_1912_captions.srt','w').write("\n".join(out))
json.dump(chap,open('chap.json','w'));print(k-1,'captions');print({c:"%d:%02d"%(t//60,t%60) for c,t in chap.items()})

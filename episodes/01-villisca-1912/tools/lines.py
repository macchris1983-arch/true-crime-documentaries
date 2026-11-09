import re,numpy as np
SR=48000
def chunks():
    src=open('/home/claude/villisca_vo_source.txt').read();p=re.split(r'=== CHUNK (\d+) ===\n',src)[1:]
    return dict(zip(p[0::2],p[1::2]))
def line_times(n,b):
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
    sp=np.cumsum(~q)*.02;tot=sp[-1]
    bounds=[];used=set()
    for f in cum:
        t=np.searchsorted(sp,f*tot)*.02
        c=[(abs((g[0]+g[1])/2-t),ii) for ii,g in enumerate(inner) if ii not in used and (not bounds or g[0]>bounds[-1][1]-1e-6)]
        if c and min(c)[0]<1.5:
            ii=min(c)[1];used.add(ii);bounds.append(inner[ii])
        else:bounds.append((t,t))
    seg=[];st=s0
    for g in bounds:seg.append((st,g[0]));st=g[1]
    seg.append((st,e0))
    return [(l,a,b) for l,(a,b) in zip(L,seg)],e0

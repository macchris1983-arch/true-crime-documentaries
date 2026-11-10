import re,json,numpy as np,subprocess
from isl import load,islands
SR=48000
import splice_map
def norm(s):return re.sub(r'[^a-z0-9 ]','',s.lower().replace('-',' ')).split()
NUM={'1912':'nineteen twelve','10':'tenth','43':'forty three','39':'thirty nine','19':'nineteen','11':'eleven','12':'twelve','519':'five nineteen'}
def tight_map(n):
    """fixed-time -> tight-time, replicating tighten_fixed.py"""
    x=np.fromfile(f"voice_fixed/{n}.raw",dtype=np.int16).astype(np.float32);fl=int(.02*SR);k=len(x)//fl
    rms=np.sqrt(np.mean(x[:k*fl].reshape(k,fl)**2,axis=1));th=max(10**(-42/20)*32768,np.percentile(rms,5)*2.0);q=rms<th
    gaps=[];i=0
    while i<k:
        if q[i]:
            j=i
            while j<k and q[j]:j+=1
            if (j-i)*.02>=.16:gaps.append((i*.02,j*.02))
            i=j
        else:i+=1
    return gaps
def build():
    tx=[l.split(' ',3) for l in open('fix/transcript.txt').read().strip().splitlines()]
    segs={}
    for c,a,b,t in tx:segs.setdefault(c,[]).append((float(a),t))
    src=open('/home/claude/villisca_vo_source_v1.txt').read();p=re.split(r'=== CHUNK (\w+) ===\n',src)[1:]
    C=dict(zip(p[0::2],p[1::2]))
    tm=json.load(open('tight_gaps.json'))
    out={}
    for n,b in C.items():
        L=[re.sub(r'\[[^\]]+\]\s*','',l).replace('...','').strip() for l in b.strip().splitlines() if l.strip()!='[pause]'];L=[l for l in L if l]
        LN=[norm(l) for l in L]
        gaps=tm[n];anc=[]
        for a,t in segs.get(n,[]):
            w=norm(' '.join(NUM.get(x,x) for x in t.split()))[:3]
            if len(w)<2:continue
            for i,l in enumerate(LN):
                if l[:min(3,len(l))]==w[:min(3,len(l))] and i not in [x[0] for x in anc]:
                    # raw -> fixed -> tight
                    f=splice_map.raw2fixed(n,a)
                    # tight: subtract removed silence for gaps before f
                    rem=0
                    for g0,g1,keep in gaps:
                        if g1<=f:rem+=(g1-g0)-keep
                        elif g0<f<g1:rem+=(f-g0)-min(keep,f-g0)
                    anc.append((i,f-rem));break
        out[n]=sorted(anc)
    return out

import subprocess,re,numpy as np,json
SR=48000
src=open('/home/claude/villisca_vo_source.txt').read()
p=re.split(r'=== CHUNK (\d+) ===\n',src)[1:]
info={}
for n,b in zip(p[0::2],p[1::2]):
    ws=0;pp=[]
    W=lambda t:len(re.findall(r"[A-Za-z0-9'\-]+",re.sub(r'\[[^\]]+\]','',t)))
    tot=W(b)
    for l in b.strip().splitlines():
        if l.strip()=='[pause]':pp.append(ws/tot)
        ws+=W(l)
    info[n]=(tot,pp)
def load(f):
    r=subprocess.check_output(["ffmpeg","-v","error","-f","s16le","-ar","48000","-ac","1","-i",f,"-f","s16le","-ac","1","-ar",str(SR),"-"]);return np.frombuffer(r,dtype=np.int16).astype(np.float32)
GAP=0.90;PAUSE=1.4
res={};ts=0;tw=0
for n in sorted(info):
    x=load(f"voice_fixed/{n}.raw");fl=int(.02*SR);k=len(x)//fl
    rms=np.sqrt(np.mean(x[:k*fl].reshape(k,fl)**2,axis=1))
    th=max(10**(-42/20)*32768,np.percentile(rms,5)*2.0);q=rms<th
    gaps=[];i=0
    while i<k:
        if q[i]:
            j=i
            while j<k and q[j]:j+=1
            if (j-i)*.02>=.16:gaps.append([i,j])
            i=j
        else:i+=1
    # speech position of each gap
    sp=np.cumsum(~q);fr=[sp[min(a,k-1)]/max(sp[-1],1) for a,b in gaps]
    keep=[GAP]*len(gaps)
    for t in info[n][1]:
        c=[i for i in range(len(gaps))]
        if c:
            b=min(c,key=lambda i:abs(fr[i]-t));keep[b]=PAUSE
    out=[];pos=0
    for (a,b),kp in zip(gaps,keep):
        s,e=a*fl,b*fl
        out.append(x[pos:s]);L=min(e-s,int(kp*SR)) if kp==GAP else int(kp*SR)
        out.append(np.zeros(L));pos=e
    out.append(x[pos:]);y=np.concatenate(out).astype(np.int16)
    # trim ends
    res[n]=y;d=len(y)/SR;ts+=d;tw+=info[n][0]
    y.tofile(f"voice2/{n}.pcm")
    print(n,round(len(x)/SR,1),'->',round(d,1),'gaps',len(gaps),'wpm',round(info[n][0]/d*60))
print(ts,tw,tw/ts*60)
json.dump({'tot':ts,'tw':tw},open('voice2/m.json','w'))

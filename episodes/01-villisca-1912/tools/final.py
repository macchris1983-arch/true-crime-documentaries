import json,re,subprocess,os,numpy as np
TL=json.load(open('tl.json'));FPS=24;total=sum(a['fr'] for a in TL)/FPS
start={};end={}
for a in TL:
    start.setdefault(a['ch'],a['t']);end[a['ch']]=a['t']+a['fr']/FPS
SR=48000;x=np.zeros(int(total*SR)+SR,dtype=np.int16)
for n in sorted(start):
    if n=="12":continue
    y=np.fromfile(f"voice2/{n}.pcm",dtype=np.int16);i=int(start[n]*SR);x[i:i+len(y)]=y
x[:int(total*SR)].tofile("voice2/all.pcm")
win=[(end[c]-5.0,end[c]) for c in ("03","07","09","10")]
expr="+".join(f"between(t,{a:.3f},{b:.3f})" for a,b in win)
subprocess.check_call(["ffmpeg","-y","-v","error","-f","s16le","-ar","48000","-ac","1","-i","voice2/all.pcm","-f","lavfi","-i",f"anoisesrc=c=brown:a=0.03:r=48000:d={total:.3f}","-filter_complex",
 f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[v];[1:a]lowpass=f=500,volume=15dB,volume='if({expr},0,1)':eval=frame[t];[v][t]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89,aresample=48000[o]","-map","[o]","-c:a","pcm_s16le","voice2/mix.wav"])
subprocess.check_call(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i","list.txt","-i","voice2/mix.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest","Villisca.tmp.mp4"])
os.rename("Villisca.tmp.mp4","/home/claude/Villisca_1912_The_Inventory_FINAL.mp4")
# captions: words proportionally across each section
src=open('/home/claude/villisca_vo_source.txt').read();p=re.split(r"=== CHUNK (\w+) ===\n",src)[1:]
fmt=lambda t:"%02d:%02d:%02d,%03d"%(t//3600,t//60%60,t%60,(t%1)*1000)
out=[];k=1
for n,b in zip(p[0::2],p[1::2]):
    L=[]
    for l in b.strip().splitlines():
        if l.strip()=='[pause]':L.append(None);continue
        L.append(re.sub(r'\[[^\]]+\]\s*','',l).replace('...','').strip())
    d=os.path.getsize(f"voice2/{n}.pcm")/96000;w=[len(x.split())+1.5 if x else 3.5 for x in L];u=d/sum(w);t=start[n]
    for x,ww in zip(L,w):
        if x:
            out.append(f"{k}\n{fmt(t)} --> {fmt(t+ww*u)}\n{x}\n");k+=1
        t+=ww*u
open('/home/claude/Villisca_1912_captions.srt','w').write("\n".join(out))
print('final done',total)

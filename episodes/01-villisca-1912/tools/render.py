import sys,json,subprocess,os,re
from shots import *
FPS=24
dur={n:os.path.getsize(f"voice2/{n}.pcm")/96000+(5 if n in("03","07","09","10") else 0) for n in ["01","02","03","04","05","06","07","08","09","10","11"]}
sil={"03","07","09","10"}
ALL=[]
from cues import CUE,N as NEW
from timing import starts
T=0;ST=starts()
for n in sorted(CUE):
    st,d=ST[n];bounds=st[1:]+[d];base=T;prev=0
    for i,(k,cue) in enumerate(CUE[n]):
        x=NEW[k] if isinstance(k,str) else S[n][k]
        b=x[0]=="B"; fn=x[1] if b else x[0]; cit=x[2] if b else x[1]
        endf=round((base+bounds[i])*FPS)-round(T*FPS)
        last=i==len(CUE[n])-1
        ALL.append(dict(ch=n,k=i,fn=fn,cit=cit,fr=endf,black=b,sil=last and n in sil and b,t=T));T+=endf/FPS
ALL.append(dict(ch="12",k=0,fn=lambda:card("Sources in the description.\nNo one has ever been convicted of these murders.",size=76),cit="",fr=round(10.5*FPS),black=False,sil=False,t=T))
def plate(c):
    i=Image.new("RGBA",(1920,1080),(0,0,0,0))
    if c:
        d=ImageDraw.Draw(i);F=f(MO,26);d.rectangle([44,1000,70+d.textlength(c,font=F),1046],fill=(10,10,9,215));d.text((58,1007),c,font=F,fill=(226,219,203,255))
    return i
def go(a):
    n="%s_%02d"%(a['ch'],a['k']);p=f"png/{n}.png";pl=f"png/{n}_p.png"
    a['fn']().save(p);plate(a['cit']).save(pl)
    out=f"mp4/{n}.mp4";tmp=f"mp4/{n}.tmp.mp4"
    if os.path.exists(out):return
    N=a['fr'];mv=a['k']%4
    fade=[]
    if a['sil']: fade.append(f"fade=t=out:st={max(N/FPS-5.5,0):.2f}:d=0.5")
    if a["black"] or mv in (0,2):
        v=f"[0:v]scale=1920:1080,fps={FPS},loop=-1:1,trim=duration={N/FPS:.4f},setpts=PTS-STARTPTS[b]"
        args=["-framerate",str(FPS),"-i",p]
    else:
        A=0.10 if mv==1 else 0.15
        v=f"[0:v]zoompan=z='1+{A}*(0.5-0.5*cos(PI*on/{N}))':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={N}:s=1920x1080:fps={FPS},trim=end_frame={N},setpts=PTS-STARTPTS[b]"
        args=["-framerate",str(FPS),"-i",p]
    ff=f";[b][1:v]overlay=0:0:format=auto"+("," + ",".join(fade) if fade else "")+",format=yuv420p"
    cmd=["ffmpeg","-y","-v","error"]+args+["-i",pl,"-filter_complex",v+ff,"-frames:v",str(N),"-c:v","libx264","-preset","veryfast","-crf","18","-r",str(FPS),"-an",tmp]
    subprocess.check_call(cmd);os.rename(tmp,out)
if __name__=="__main__":
    mode=sys.argv[1]
    if mode=="key":
        for ch,k in [("01",3),("02",5),("03",7),("05",6),("08",8),("08",11),("10",3)]:
            a=[x for x in ALL if x['ch']==ch and x['k']==k][0]
            im=a['fn']().convert("RGB").resize((1920,1080));im.paste(plate(a['cit']),(0,0),plate(a['cit']));im.resize((960,540)).save(f"key_{ch}_{k}.jpg",quality=85)
    else:
        print(len(ALL),sum(a['fr'] for a in ALL)/FPS)
        for a in ALL: go(a)
        open("list.txt","w").write("".join(f"file 'mp4/{a['ch']}_{a['k']:02d}.mp4'\n" for a in ALL))
        json.dump([{k:a[k] for k in('ch','k','fr','sil','t')} for a in ALL],open("tl.json","w"))
        print("done")

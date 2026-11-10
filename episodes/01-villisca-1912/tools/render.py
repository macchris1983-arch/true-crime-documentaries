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
ALL.append(dict(ch="12",k=0,fn=lambda:card("Sources in the description.\nNo one has ever been convicted of these murders.\n\nIf this was worth your time: like, comment, and subscribe to story timez.",size=70),cit="",fr=round(10.5*FPS),black=False,sil=False,t=T))
from draw import wrap,SER
def plate(c,strip=""):
    i=Image.new("RGBA",(1920,1080),(0,0,0,0));d=ImageDraw.Draw(i)
    if strip:
        F=f(SER,40);L=wrap(d,strip,F,1667);h=56*len(L)+47;y0=980-h
        d.rectangle([0,y0,1920,980],fill=(12,12,11,232));y=y0+23
        for l in L:d.text(((1920-d.textlength(l,font=F))/2,y),l,font=F,fill=(232,226,212,255));y+=56
    if c:
        F=f(MO,26);d.rectangle([44,1000,70+d.textlength(c,font=F),1046],fill=(10,10,9,215));d.text((58,1007),c,font=F,fill=(226,219,203,255))
    return i
def go(a):
    n="%s_%02d"%(a['ch'],a['k']);p=f"png/{n}.png";pl=f"png/{n}_p.png"
    im=a['fn']();scan=im.info.get("scan",False);a["strip"]=bool(im.info.get("strip",""));im.save(p);plate(a['cit'],im.info.get("strip","")).save(pl)
    out=f"mp4/{n}.mp4";tmp=f"mp4/{n}.tmp.mp4"
    if os.path.exists(out):return
    N=a['fr'];k=a['k']
    fade=[]
    if a['sil']: fade.append(f"fade=t=out:st={max(N/FPS-5.5,0):.2f}:d=0.5")
    E=f"(0.5-0.5*cos(PI*on/{N}))"
    if a['sil']:
        v=f"[0:v]scale=1920:1080,fps={FPS},loop=-1:1,trim=duration={N/FPS:.4f},setpts=PTS-STARTPTS[b]"
    else:
        if scan:
            Z=1.12;d=k%3
            if d==0:x,y=f"(iw-iw/zoom)*{E}","(ih-ih/zoom)/2"
            elif d==1:x,y=f"(iw-iw/zoom)*(1-{E})","(ih-ih/zoom)/2"
            else:x,y="(iw-iw/zoom)/2",f"(ih-ih/zoom)*{E}"
            z=str(Z)
        else:
            A=0.04 if a['black'] else (0.06 if k%2 else 0.10)
            z=f"1+{A}*{E}";x="iw/2-iw/zoom/2";y="ih/2-ih/zoom/2"
        v=f"[0:v]zoompan=z='{z}':x='{x}':y='{y}':d={N}:s=1920x1080:fps={FPS},trim=end_frame={N},setpts=PTS-STARTPTS[b]"
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
        json.dump([{k:a[k] for k in('ch','k','fr','sil','t','strip') if k in a} for a in ALL],open("tl.json","w"))
        print("done")

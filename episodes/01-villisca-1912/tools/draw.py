import re,json,math
from PIL import Image,ImageDraw,ImageFont
W,H=2880,1620
SER="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"; SB="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"; MO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
import glob
for p in glob.glob('/usr/share/fonts/truetype/liberation*/LiberationSerif-Regular.ttf'): SER=p; SB=p.replace('Regular','Bold')
BG=(14,14,13);INK=(232,226,212);DIM=(142,137,125);PAP=(226,219,203);PINK=(30,28,24);RED=(158,44,34);HI=(214,190,120)
f=lambda p,s:ImageFont.truetype(p,s)
def wrap(d,t,fnt,w):
    out=[]
    for para in t.split("\n"):
        cur=""
        for wd in para.split():
            n=(cur+" "+wd).strip()
            if d.textlength(n,font=fnt)<=w: cur=n
            else: out.append(cur);cur=wd
        out.append(cur)
    return out
def base(c=BG): 
    i=Image.new("RGB",(W,H),c);return i,ImageDraw.Draw(i)
def center(d,lines,fnt,y,col,lh):
    for l in lines:
        d.text(((W-d.textlength(l,font=fnt))/2,y),l,font=fnt,fill=col);y+=lh
    return y
def card(big,kick="",attr="",size=118):
    i,d=base();F=f(SER,size);L=wrap(d,big,F,2200);lh=int(size*1.34)
    tot=lh*len(L);y=(H-tot)/2-60
    if kick: center(d,[kick],f(MO,44),y-140,DIM,60)
    y=center(d,L,F,y,INK,lh)
    if attr: center(d,[attr],f(SER,56),y+70,DIM,70)
    return i
def doc(text,hi=None,head=""):
    i,d=base();m=380;d.rectangle([m,170,W-m,H-300],fill=PAP)
    d.text((m+90,230),"TRANSCRIBED FROM THE PAGE",font=f(MO,38),fill=(105,98,84))
    if head:d.text((m+90,290),head,font=f(SB,58),fill=PINK)
    F=f(SER,76);L=wrap(d,text,F,W-2*m-180);lh=108;y=(H-470-lh*len(L))/2+300
    words_hi=hi or ""
    full=" ".join(L)
    start=full.find(words_hi) if words_hi else -1;end=start+len(words_hi);pos=0
    for l in L:
        x=m+90
        if start>=0:
            a=max(start,pos);b=min(end,pos+len(l))
            if a<b:
                x0=x+d.textlength(l[:a-pos],font=F);x1=x+d.textlength(l[:b-pos],font=F)
                d.rectangle([x0-6,y+6,x1+6,y+92],fill=HI)
        d.text((x,y),l,font=F,fill=PINK);y+=lh;pos+=len(l)+1
    return i
def ledger(rows,title="INVENTORY"):
    i,d=base();m=460;d.rectangle([m,130,W-m,H-260],fill=PAP)
    d.text((m+80,175),title,font=f(SB,70),fill=PINK)
    y0=300;step=96
    for k in range(10):
        d.line([m+60,y0+k*step,W-m-60,y0+k*step],fill=(170,162,144),width=3)
    F=f(SER,66)
    for k,r in enumerate(rows):
        t,st=r if isinstance(r,tuple) else (r,"")
        y=y0+k*step+12
        d.text((m+90,y),t,font=F,fill=PINK)
        if st=="x":
            yy=y+44;d.line([m+80,yy,m+110+d.textlength(t,font=F),yy],fill=RED,width=7)
        elif st:
            d.text((W-m-100-d.textlength(st,font=f(MO,40)),y+18),st,font=f(MO,40),fill=RED)
    return i
def plan(hi=(),note=""):
    i,d=base();T=f(SER,52)
    rooms={"parlor":(420,560,960,1030,"Parlor"),"bed":(420,1030,960,1370,"Bedroom off the parlor"),"dining":(960,560,1400,1030,"Dining room"),"kitchen":(960,1030,1400,1370,"Kitchen"),
           "north":(1620,560,2100,1370,"North room"),"south":(2100,560,2520,1370,"South room")}
    d.text((420,470),"DOWNSTAIRS",font=f(MO,42),fill=DIM);d.text((1620,470),"UPSTAIRS",font=f(MO,42),fill=DIM)
    for k,(a,b,c,e,n) in rooms.items():
        d.rectangle([a,b,c,e],fill=HI if k in hi else BG,outline=INK,width=6)
        col=PINK if k in hi else INK
        L=wrap(d,n,T,c-a-60);y=(b+e)/2-len(L)*34
        for l in L:
            d.text(((a+c-d.textlength(l,font=T))/2,y),l,font=T,fill=col);y+=68
    d.text((420,170),"Schematic of rooms named in testimony. Not to scale.",font=f(MO,44),fill=DIM)
    if note: d.text((420,270),note,font=f(SER,92),fill=INK)
    return i
def evo(steps,title):
    i,d=base();d.text((300,170),title,font=f(MO,50),fill=DIM);F=f(SER,74);y=310;n=len(steps);gap=min(190,1040/max(n,1))
    for k,(dt,t) in enumerate(steps):
        last=k==n-1
        d.text((300,y+8),dt,font=f(MO,50),fill=HI if last else DIM)
        L=wrap(d,t,F,1760)
        d.text((800,y),L[0],font=F,fill=INK if last else DIM)
        if len(L)>1:d.text((800,y+86),L[1],font=f(SER,62),fill=INK if last else DIM)
        y+=gap
    return i
def years(marks,upto=None):
    i,d=base();x0,x1,y=380,2500,800;d.line([x0,y,x1,y],fill=DIM,width=6);X=lambda v:x0+(x1-x0)*(v-1912)/19
    for v in (1912,1917,1931):
        d.line([X(v),y-24,X(v),y+24],fill=DIM,width=5);t=str(v);d.text((X(v)-d.textlength(t,font=f(MO,48))/2,y+50),t,font=f(MO,48),fill=DIM)
    for k,(v,t) in enumerate(marks):
        d.ellipse([X(v)-16,y-16,X(v)+16,y+16],fill=HI)
        Yy=y-160-(k%3)*130;d.line([X(v),y-16,X(v),Yy+80],fill=HI,width=3);
        tw=d.textlength(t,font=f(SER,62));xx=min(max(X(v)-tw/2,120),W-120-tw);d.text((xx,Yy),t,font=f(SER,62),fill=INK)
    return i
def blk(t="",attr=""):
    return card(t,attr=attr,size=86) if t else base()[0]
def counter():
    i,d=base();Fb=f(SB,300);Fs=f(SER,62);cols=[("15","times asked if he killed the parents first. He said no."),("25","times told no promise would be made."),("51","times admonished to tell the truth.")]
    for k,(n,t) in enumerate(cols):
        x=320+k*800;d.text((x,470),n,font=Fb,fill=HI)
        y=850
        for l in wrap(d,t,Fs,640):d.text((x,y),l,font=Fs,fill=INK);y+=84
    return i

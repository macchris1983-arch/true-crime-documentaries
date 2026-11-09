import json,re,subprocess
TL=json.load(open('tl.json'));FPS=24;total=sum(a['fr'] for a in TL)/FPS
ends={}
for a in TL: ends[a['ch']]=a['t']+a['fr']/FPS
win=[(ends[c]-5.0,ends[c]) for c in ("03","07","09","10")]
expr="+".join(f"between(t,{a:.2f},{b:.2f})" for a,b in win)
subprocess.check_call(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i","list.txt","-f","lavfi","-i",f"anoisesrc=c=brown:a=0.03:r=48000:d={total:.2f},lowpass=f=500,volume='if({expr},0,1)':eval=frame","-c:v","copy","-c:a","aac","-b:a","160k","-ar","48000","-movflags","+faststart","-shortest","Villisca_1912_picture_cut_NO_VOICE.tmp.mp4"])
import os;os.rename("Villisca_1912_picture_cut_NO_VOICE.tmp.mp4","Villisca_1912_picture_cut_NO_VOICE.mp4")

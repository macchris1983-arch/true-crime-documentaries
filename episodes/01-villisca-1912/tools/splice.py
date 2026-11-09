import numpy as np,json,sys,os,subprocess
from isl import load,SR,islands
CUT={"02":[(28.12,30.15)],"05":[(14.95,15.45)],"07":[(43.06,45.80)],"09":[(7.72,11.45)]}
REP={"01":[(64.40,68.40,"01_027")],"05":[(9.70,12.30,"05_125"),(55.40,59.25,"05_SUIT")],
"06":[(1.95,5.90,"06_151"),(50.45,54.00,"06_165"),(75.40,76.40,"06_BEC"),(77.00,78.30,"06_WHO")],
"10":[(35.85,38.45,"10_276")],"02":[(13.35,15.20,"02_HER")],"03":[(25.33,27.65,"03_RET")],
"04":[(58.85,59.92,"04_BED")],"07":[(58.04,58.92,"07_OATH")]}
PICK=json.load(open("picks.json"))
os.makedirs("voice_fixed",exist_ok=True)
def rms(a):return np.sqrt(np.mean(a[np.abs(a)>300]**2)) if np.any(np.abs(a)>300) else 1
for n in ["%02d"%i for i in range(1,12)]:
    x=load(f"voice_emo_in/{n}.mp3")
    ed=[(a,b,None) for a,b in CUT.get(n,[])]+[(a,b,PICK[k]) for a,b,k in REP.get(n,[]) if k in PICK]
    ed.sort();out=[];pos=0
    for a,b,f in ed:
        out.append(x[pos:int(a*SR)])
        if f:
            y=load("fix3/"+f);I=islands(y,0.2);y=np.concatenate([np.concatenate([y[int(a*SR):int(b*SR)],np.zeros(int(.12*SR))]) for a,b in I])[:-int(.12*SR)];y=y*(rms(x[int(a*SR):int(b*SR)])/rms(y))
            out.append(np.zeros(int(.05*SR)));out.append(y);out.append(np.zeros(int(.05*SR)))
        pos=int(b*SR)
    out.append(x[pos:]);z=np.clip(np.concatenate(out),-32768,32767).astype(np.int16)
    z.tofile(f"voice_fixed/{n}.raw");print(n,round(len(x)/SR,1),'->',round(len(z)/SR,1),len(ed),'edits')

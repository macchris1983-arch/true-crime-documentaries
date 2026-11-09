import base64,json,re,collections
src=open('/home/claude/villisca_vo_source.txt').read()
ph={"Villisca":"Vih-LISS-kuh","Stillinger":"Still-inger","Peckham":"Peck-um","Epperly":"Epper-lee","Lyn":"Lin","Ina":"Eye-nuh","Lena":"Lee-nuh"}
def fix(t):
    for a,b in ph.items(): t=re.sub(r'\b'+a+r'\b',b,t)
    return t
M={"plain":(.40,.35,.30),"tender":(.55,.30,.42),"dread":(.50,.22,.55),"tense":(.70,.38,.28),"grief":(.72,.25,.60)}
default={"01":"dread","02":"tender","03":"dread","04":"plain","05":"plain","06":"dread","07":"tense","08":"tense","09":"grief","10":"plain","11":"grief"}
O=[("My wife did, yes","grief"),("about three different times","grief"),("She expected them back","grief"),("Her two daughters","tender"),
("What I can give you","plain"),("I can't tell you who","dread"),("No one can","dread"),
("Everyone who tells","plain"),("The evidence was lost","plain"),("it kept getting more","dread"),
("So I won't give you one","dread"),("Nobody who saw","dread"),
("A small boy","grief"),("A gauze undershirt","grief"),("I lifted that off","grief"),("lifted it off","grief"),("to see which one","grief"),("Dr. Williams told","dread"),
("Remember that","tense"),("It is the last moment","dread"),("who had been inside","dread"),
("It cannot explain","dread"),("But loss only","dread"),
("kept changing","dread"),("The containers stayed","dread"),
("Her parents were alive","grief"),("who was going to pay","dread"),("It had become","dread"),("The question had stopped","dread"),
("Albert Jones was never charged","plain"),("Both men denied","plain"),("The prosecution attacked","plain"),("A sound","dread"),("became a man","dread"),("You have met Landers","dread"),
("that's a lie","tense"),("Early the next morning","dread"),("Kelly said,","tense"),("No record I have read","dread"),("whether that is","dread"),("He was charged","plain"),("He had been charged","plain"),("I have no recollection","grief"),("It cannot show you","dread"),("The record shows a signature","dread"),
("forgot Lena","grief"),("The last confession","dread"),("Six people","dread"),("Officers said","dread"),("He was found not guilty","plain"),("That is the verdict","plain"),
("Some of it","plain"),("This film is drawn","plain"),("A report is not proof","plain"),("Everyone named here","plain"),("No one has ever been convicted","plain"),("Reverend Kelly was acquitted","plain"),("Frank and Albert","plain"),("is a mother","grief"),("on a Monday","grief"),("calling a house","grief"),("nobody needed to invent","grief"),("The one thing","grief")]
items=[];cnt=collections.Counter();parts=re.split(r'=== CHUNK (\d+) ===\n',src)[1:]
for n,b in zip(parts[0::2],parts[1::2]):
    for l in b.strip().splitlines():
        if l.strip()=='[pause]': items.append(dict(c=n,pause=1.4));continue
        mode=default[n]
        for k,v in O:
            if k in l: mode=v;break
        cnt[mode]+=1;e,c,tail=M[mode]
        t=l.replace('[low voice] ','').replace('...',',').strip()
        items.append(dict(c=n,text=fix(t),e=e,cfg=c,tail=max(tail,.8 if l.rstrip().endswith('...') else 0)))
print(cnt,len(items))
ref=base64.b64encode(open('ref.mp3','rb').read()).decode()
gen=r'''
import json, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
m = ChatterboxTTS.from_pretrained(device="cuda")
L = json.load(open("/content/v/lines.json")); os.makedirs("/content/v/out", exist_ok=True)
sil = lambda s: torch.zeros(1, int(s * m.sr))
def trim(w):
    x = w.abs().max(dim=0).values; fl = int(.02 * m.sr); n = x.shape[0] // fl
    e = x[:n * fl].reshape(n, fl).max(dim=1).values; on = (e > 0.02).nonzero()
    return w if len(on) == 0 else w[:, max(0, on[0].item() - 2) * fl : min(n, on[-1].item() + 5) * fl]
parts = {}
for i, l in enumerate(L):
    p = parts.setdefault(l["c"], [])
    if "pause" in l: p.append(sil(l["pause"])); continue
    torch.manual_seed(7)
    w = trim(m.generate(l["text"], audio_prompt_path="/content/v/ref.wav", exaggeration=l["e"], cfg_weight=l["cfg"], temperature=0.7))
    p += [w.cpu(), sil(l["tail"])]
    print(i + 1, "/", len(L), l["text"], flush=True)
for c, p in parts.items():
    ta.save(f"/content/v/raw_{c}.wav", torch.cat(p, dim=1), m.sr)
'''
def code(s):return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":s.strip("\n").splitlines(True)}
cells=[{"cell_type":"markdown","metadata":{},"source":["# Villisca narration with emotion\n"]},
code('import subprocess\ngpu=subprocess.run(["nvidia-smi","-L"],capture_output=True,text=True).stdout\nprint(gpu or "NO GPU"); assert gpu'),
code('!pip install -q chatterbox-tts && pip install -q torchvision==0.21.0'),
code('import base64,json,os,subprocess\nos.makedirs("/content/v",exist_ok=True)\nREF='+json.dumps(ref)+'\nLINES='+json.dumps(items)+'\nopen("/content/v/ref.mp3","wb").write(base64.b64decode(REF))\nsubprocess.run(["ffmpeg","-y","-loglevel","error","-i","/content/v/ref.mp3","-ac","1","-ar","24000","/content/v/ref.wav"],check=True)\njson.dump(LINES,open("/content/v/lines.json","w"))\nopen("/content/v/gen.py","w").write('+json.dumps(gen)+')\nprint(len(LINES),"lines")'),
code('r=subprocess.run(["python","/content/v/gen.py"],capture_output=True,text=True)\nprint(r.stdout[-1200:]); print(r.stderr[-1500:] if r.returncode else "done"); assert r.returncode==0'),
code('import glob,shutil\nfor f in sorted(glob.glob("/content/v/raw_*.wav")):\n    n=f[-6:-4]\n    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f,"-af","atempo=0.97","-ar","48000",f"/content/v/out/{n}.wav"],check=True)\nshutil.make_archive("/content/villisca_voice_emotion","zip","/content/v/out")\nfrom google.colab import files\nfiles.download("/content/villisca_voice_emotion.zip")')]
nb={"cells":cells,"metadata":{"accelerator":"GPU","colab":{"provenance":[],"gpuType":"T4"},"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":0}
json.dump(nb,open('/home/claude/Villisca_voice_with_emotion.ipynb','w'),indent=1)

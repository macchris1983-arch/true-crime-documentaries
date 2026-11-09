import base64,json,re
src=open('/home/claude/villisca_vo_source.txt').read()
ph={"Villisca":"Vih-LISS-kuh","Stillinger":"Still-inger","Peckham":"Peck-um","Epperly":"Epper-lee","Lyn":"Lin","Ina":"Eye-nuh","Lena":"Lee-nuh"}
def fix(t):
    for a,b in ph.items(): t=re.sub(r'\b'+a+r'\b',b,t)
    return t
items=[];parts=re.split(r'=== CHUNK (\d+) ===\n',src)[1:]
for n,b in zip(parts[0::2],parts[1::2]):
    for l in b.strip().splitlines():
        if l.strip()=='[pause]': items.append(dict(c=n,pause=1.4));continue
        t=l.replace('[low voice] ','').replace('...',',').strip()
        items.append(dict(c=n,text=fix(t),tail=0.8 if l.rstrip().endswith('...') else 0.32))
ref=base64.b64encode(open('ref.mp3','rb').read()).decode()
gen=r'''
import json, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
m = ChatterboxTTS.from_pretrained(device="cuda")
L = json.load(open("/content/v/lines.json")); os.makedirs("/content/v/out", exist_ok=True)
sil = lambda s: torch.zeros(1, int(s * m.sr))
parts = {}
for i, l in enumerate(L):
    p = parts.setdefault(l["c"], [])
    if "pause" in l: p.append(sil(l["pause"])); continue
    torch.manual_seed(7)
    w = m.generate(l["text"], audio_prompt_path="/content/v/ref.wav", exaggeration=0.35, cfg_weight=0.3, temperature=0.6)
    p += [w.cpu(), sil(l["tail"])]
    print(i + 1, "/", len(L), l["text"], flush=True)
for c, p in parts.items():
    ta.save(f"/content/v/raw_{c}.wav", torch.cat(p, dim=1), m.sr)
'''
def md(s):return {"cell_type":"markdown","metadata":{},"source":s.strip("\n").splitlines(True)}
def code(s):return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":s.strip("\n").splitlines(True)}
cells=[md("# Villisca narration in your CapCut voice\n\n**Run:** Runtime > Change runtime type > **T4 GPU** > Save, then **Runtime > Run all**. Result: `villisca_voice.zip`, downloaded and saved in Google Drive > FOUR DEEP."),
code('import subprocess\ngpu=subprocess.run(["nvidia-smi","-L"],capture_output=True,text=True).stdout\nprint(gpu or "NO GPU: Runtime > Change runtime type > T4 GPU, then Run all again"); assert gpu'),
code('!pip install -q chatterbox-tts && pip install -q torchvision==0.21.0'),
code('import base64,json,os,subprocess\nos.makedirs("/content/v",exist_ok=True)\nREF='+json.dumps(ref)+'\nLINES='+json.dumps(items)+'\nopen("/content/v/ref.mp3","wb").write(base64.b64decode(REF))\nsubprocess.run(["ffmpeg","-y","-loglevel","error","-i","/content/v/ref.mp3","-ac","1","-ar","24000","/content/v/ref.wav"],check=True)\njson.dump(LINES,open("/content/v/lines.json","w"))\nopen("/content/v/gen.py","w").write('+json.dumps(gen)+')\nprint(len(LINES),"lines")'),
code('r=subprocess.run(["python","/content/v/gen.py"],capture_output=True,text=True)\nprint(r.stdout[-1500:]); print(r.stderr[-1500:] if r.returncode else "done"); assert r.returncode==0'),
code('import glob,shutil\nfor f in sorted(glob.glob("/content/v/raw_*.wav")):\n    n=f[-6:-4]\n    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f,"-af","atempo=0.94","-ar","48000",f"/content/v/out/{n}.wav"],check=True)\nshutil.make_archive("/content/villisca_voice","zip","/content/v/out")\ntry:\n    from google.colab import drive\n    drive.mount("/content/drive"); os.makedirs("/content/drive/MyDrive/FOUR DEEP",exist_ok=True)\n    shutil.copy("/content/villisca_voice.zip","/content/drive/MyDrive/FOUR DEEP/"); print("saved to Drive")\nexcept Exception as e: print("Drive save skipped:",e)\nfrom google.colab import files\nfiles.download("/content/villisca_voice.zip")')]
nb={"cells":cells,"metadata":{"accelerator":"GPU","colab":{"provenance":[],"gpuType":"T4"},"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":0}
json.dump(nb,open('/home/claude/Villisca_voice_in_your_CapCut_voice.ipynb','w'),indent=1)
print(len(items),sum('text' in i for i in items),[i for i in items if 'text' in i][:2])

#!/usr/bin/env python3
"""Oklahoma City episode: build in the Higgsfield sandbox.
usage: python3 sbx_build.py align|shots|video|audio|subs|all [only_chunks]"""
import json, os, re, subprocess, sys, difflib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

R = "/home/user/repo/episodes/03-oklahoma-city-1995"
O = "/home/user/okc"
B = f"{O}/build"; os.makedirs(f"{B}/shots", exist_ok=True)
ORDER = ["00a", "00b", "00c", "01", "02", "03", "04", "05", "06", "07", "08", "09"]
PAUSE = {"04", "05", "07"}           # 5 s of silence after these
GAP = 0.7                             # breath between chunks
TEMPO = {"05": 0.94, "06": 0.95}      # slow the two fast takes slightly
FIXED = {"00b": 4.5, "09": 10.0}      # title and end card
VID = {"raw": "DOD_107913656.mp4", "imp": "DOD_107941468.mp4", "sec": "DOD_107904996-640x480-922k.mp4", "b19": "v784827.mp4"}
VFIX = {("imp", 470): 421, ("imp", 482): 446, ("imp", 120): 165, ("raw", 30): 8}
import glob as _g
FONT = (_g.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True) + _g.glob("/usr/share/fonts/**/*Montserrat*Regular*.ttf", recursive=True) + _g.glob("/usr/share/fonts/**/*.ttf", recursive=True))[0]
W, H, FPS = 1920, 1080, 30
sh = lambda c: subprocess.check_call(c, shell=True)


def src_lines():
    out = {}; cur = None
    for l in open(f"{R}/script/okc_vo_source.txt"):
        m = re.match(r"=== CHUNK (\w+) ===", l)
        if m: cur = m.group(1); out[cur] = []; continue
        if cur and l.strip(): out[cur].append(l.strip())
    return out


def norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())


def prep_voice():
    os.makedirs(f"{B}/voice", exist_ok=True)
    for c in ORDER:
        src = f"{R}/voice/{c}.wav"; dst = f"{B}/voice/{c}.wav"
        if c in FIXED or not os.path.exists(src): continue
        af = f"atempo={TEMPO[c]}," if c in TEMPO else ""
        sh(f'ffmpeg -y -v error -i {src} -af "{af}silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,aresample=48000" -ac 1 {dst}')


def dur(f): return float(subprocess.check_output(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {f}", shell=True))


def align():
    prep_voice()
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    S = src_lines(); res = {}
    for c in ORDER:
        f = f"{B}/voice/{c}.wav"
        if c in FIXED or not os.path.exists(f): continue
        segs, _ = m.transcribe(f, word_timestamps=True, language="en")
        words = [(w.word, w.start, w.end) for s in segs for w in s.words]
        hyp = [norm(w[0]) for w in words]
        ref = []; owner = []
        for i, l in enumerate(S[c]):
            for w in l.split():
                if norm(w): ref.append(norm(w)); owner.append(i)
        sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
        r2h = {}
        for a, b_, n in sm.get_matching_blocks():
            for k in range(n): r2h[a + k] = b_ + k
        D = dur(f); lines = []
        for i, l in enumerate(S[c]):
            idx = [k for k in range(len(ref)) if owner[k] == i]
            hits = [r2h[k] for k in idx if k in r2h]
            st = words[min(hits)][1] if hits else None
            en = words[max(hits)][2] if hits else None
            lines.append([l, st, en])
        # fill gaps by interpolation
        for i, L in enumerate(lines):
            if L[1] is None:
                prev = next((lines[j][2] for j in range(i - 1, -1, -1) if lines[j][2] is not None), 0)
                nxt = next((lines[j][1] for j in range(i + 1, len(lines)) if lines[j][1] is not None), D)
                L[1] = prev + 0.05; L[2] = max(L[1] + 0.5, nxt - 0.05)
        res[c] = {"dur": D, "lines": lines, "heard": " ".join(w[0].strip() for w in words)}
        print(c, round(D, 1), "matched", sum(1 for k in range(len(ref)) if k in r2h), "/", len(ref), flush=True)
    json.dump(res, open(f"{B}/align.json", "w"), indent=1)


def timeline():
    A = json.load(open(f"{B}/align.json")); P = json.load(open(f"{R}/build/plan.json"))
    t = 0.0; T = {}; shots = []
    for c in ORDER:
        if c in FIXED: d = FIXED[c]; lines = []
        elif c in A: d = A[c]["dur"]; lines = A[c]["lines"]
        else: continue
        tail = (5.0 if c in PAUSE else 0) + (GAP if c not in FIXED else 0)
        T[c] = {"start": t, "voice": d, "end": t + d + tail}
        for s in P[c]:
            if s["cue"] == "@0": st = 0
            elif s["cue"] == "@end": st = d + 0.3
            else:
                hit = [L for L in lines if L[0].startswith(s["cue"])]
                if not hit: raise SystemExit(f"cue not found {c}: {s['cue']}")
                st = max(0, hit[0][1] - 0.15)
            s2 = dict(s)
            if s2.get("kind") == "vid": s2["vt"] = s2.pop("t")
            s2.update(ch=c, t=t + st); shots.append(s2)
        t = T[c]["end"]
    shots.sort(key=lambda s: s["t"])
    shots[0]["t"] = 0
    for i, s in enumerate(shots):
        nx = shots[i + 1]["t"] if i + 1 < len(shots) else t
        s["fr"] = max(1, round((nx - s["t"]) * FPS)); s["t"] = round(s["t"] * FPS) / FPS
    tot = sum(s["fr"] for s in shots) / FPS
    json.dump({"chunks": T, "shots": shots, "total": tot}, open(f"{B}/timeline.json", "w"), indent=1)
    print(len(shots), "shots", round(tot, 1), "s")


def cite_png(text, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if text:
        d = ImageDraw.Draw(im); F = ImageFont.truetype(FONT, 20)
        d.text((36, H - 44), text, font=F, fill=(205, 200, 188, 210))
    im.save(path)


def fit_img(src, out):
    P = Image.open(src).convert("RGB")
    bg = P.resize((W, H)).filter(ImageFilter.GaussianBlur(30)); bg = ImageEnhance.Brightness(bg).enhance(0.25)
    h = 960; w = int(P.width * h / P.height)
    if w > 1760: w = 1760; h = int(P.height * w / P.width)
    bg.paste(P.resize((w, h), Image.LANCZOS), ((W - w) // 2, (H - h) // 2)); bg.save(out)


def shots(only=None):
    TL = json.load(open(f"{B}/timeline.json"))
    for i, s in enumerate(TL["shots"]):
        out = f"{B}/shots/{i:03d}.mp4"
        if os.path.exists(out) or (only and s["ch"] not in only): continue
        d = s["fr"] / FPS; cp = f"{B}/shots/c{i:03d}.png"; cite_png(s.get("cite", ""), cp)
        tmp = out + ".tmp.mp4"
        if s["kind"] in ("card", "img"):
            img = f"{R}/build/{s['src']}" if s["kind"] == "card" else f"{B}/shots/i{i:03d}.png"
            if s["kind"] == "img": fit_img(f"{O}/stills/{s['src']}", img)
            zp = "" if s.get("black") else f",zoompan=z='1+0.05*on/{s['fr']}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={s['fr']}:s={W}x{H}:fps={FPS}"
            sh(f'ffmpeg -y -v error -loop 1 -framerate {FPS} -i {img} -i {cp} -filter_complex "[0:v]scale={W*2}:{H*2}{zp},scale={W}:{H},setsar=1[b];[b][1:v]overlay=0:0,format=yuv420p,fade=t=in:d=0.25" -frames:v {s["fr"]} -r {FPS} -c:v libx264 -preset veryfast -crf 19 {tmp}')
        else:
            src = f"{O}/{VID[s['src']]}"; st = VFIX.get((s["src"], s["vt"]), s["vt"])
            sh(f'ffmpeg -y -v error -ss {st} -i {src} -i {cp} -filter_complex "[0:v]yadif,scale={W}:-2,crop={W}:{H},hqdn3d=2:2:3:3,eq=saturation=0.85,setsar=1,fps={FPS}[b];[b][1:v]overlay=0:0,format=yuv420p,fade=t=in:d=0.25" -frames:v {s["fr"]} -an -c:v libx264 -preset veryfast -crf 19 {tmp}')
        os.rename(tmp, out)
        print("shot", i, s["key"], round(d, 1), flush=True)


def video():
    TL = json.load(open(f"{B}/timeline.json"))
    with open(f"{B}/list.txt", "w") as f:
        for i in range(len(TL["shots"])): f.write(f"file 'shots/{i:03d}.mp4'\n")
    sh(f"cd {B} && ffmpeg -y -v error -f concat -safe 0 -i list.txt -c copy video_noaudio.mp4")


def audio():
    TL = json.load(open(f"{B}/timeline.json")); tot = TL["total"]
    ins = []; fl = []
    for k, (c, v) in enumerate([(c, v) for c, v in TL["chunks"].items() if c not in FIXED]):
        ins.append(f"-i {B}/voice/{c}.wav"); ms = int(v["start"] * 1000)
        fl.append(f"[{k}:a]adelay={ms}|{ms}[v{k}]")
    n = len(ins)
    vmix = "".join(f"[v{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0,apad,atrim=duration={tot},loudnorm=I=-16:TP=-1.5:LRA=11[voice]"
    sh(f'ffmpeg -y -v error {" ".join(ins)} -filter_complex "{";".join(fl)};{vmix}" -map "[voice]" -ar 48000 -ac 1 {B}/voice_track.wav')
    # music: Satie bed, out during the 5 s pauses and the title, ducked under the voice
    segs = []; mus = ["g1", "g3", "g2"]; k = 0
    for c, v in TL["chunks"].items():
        if c in ("00b",): continue
        a = v["start"]; b = v["start"] + v["voice"] + (GAP if c not in FIXED else 0)
        if c == "09": b = v["end"]
        segs.append((a, b, mus[k % 3], 0)); k += 1
    # merge consecutive segments into runs broken only at pauses
    runs = []
    for a, b, m, _ in segs:
        if runs and abs(runs[-1][1] - a) < 1.0: runs[-1][1] = b
        else: runs.append([a, b])
    ins = []; fl = []; lab = []
    for k, (a, b) in enumerate(runs):
        m = mus[k % 3]; d = b - a; ins.append(f"-stream_loop -1 -i /home/user/mus/{m}.ogg")
        fl.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,atrim=duration={d},asetpts=PTS-STARTPTS,loudnorm=I=-31:TP=-8,aresample=48000,afade=t=in:d=2,afade=t=out:st={max(0,d-2):.2f}:d=2,adelay={int(a*1000)}[m{k}]"); lab.append(f"[m{k}]")
    n = len(runs)
    sh(f'ffmpeg -y -v error {" ".join(ins)} -i {B}/voice_track.wav -filter_complex "{";".join(fl)};{"".join(lab)}amix=inputs={n}:normalize=0,apad,atrim=duration={tot}[mus];[{n}:a]asplit[v][key];[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=600[duck];[v][duck]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]" -map "[a]" -ar 48000 -ac 2 -c:a aac -b:a 192k {B}/mix.m4a')


def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def subs():
    TL = json.load(open(f"{B}/timeline.json")); A = json.load(open(f"{B}/align.json"))
    ev = []
    for c, v in TL["chunks"].items():
        if c not in A: continue
        L = A[c]["lines"]
        for i, (txt, st, en) in enumerate(L):
            nx = L[i + 1][1] if i + 1 < len(L) else en + 0.6
            a = v["start"] + st; b = v["start"] + min(nx, en + 0.6)
            if len(txt) > 46:
                words = txt.split(); half = len(txt) / 2; acc = 0
                for j, w in enumerate(words):
                    acc += len(w) + 1
                    if acc >= half: txt = " ".join(words[:j + 1]) + "\\N" + " ".join(words[j + 1:]); break
            ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{txt}")
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Serif,44,&H00F0EBE0,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,10,0,2,160,160,96,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(f"{B}/subs.ass", "w").write(hdr + "\n".join(ev) + "\n")
    sh(f"cd {B} && ffmpeg -y -v error -i video_noaudio.mp4 -i mix.m4a -vf subtitles=subs.ass -map 0:v -map 1:a -c:v libx264 -preset veryfast -crf 20 -c:a copy -shortest -movflags +faststart OKC_1995_SUBTITLED.mp4")
    sh(f"cd {B} && ffmpeg -y -v error -i video_noaudio.mp4 -i mix.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart OKC_1995_FINAL.mp4")


if __name__ == "__main__":
    step = sys.argv[1]; only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    if step in ("align", "all"): align()
    if step in ("timeline", "all"): timeline()
    if step in ("shots", "all"): shots(only)
    if step in ("video", "all"): video()
    if step in ("audio", "all"): audio()
    if step in ("subs", "all"): subs()
    print("STEP_DONE", step)

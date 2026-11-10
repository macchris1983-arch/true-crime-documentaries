import json
T=json.load(open('tl.json'))
S=open('/home/claude/Villisca_1912_captions.srt').read().strip().split('\n\n')
def ts(s):h,m,r=s.split(':');sec,ms=r.split(',');return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def ass(t):return "%d:%02d:%02d.%02d"%(t//3600,t//60%60,int(t%60),int(t*100)%100)
head="""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Liberation Serif,46,&H00D4E2E8,&H00D4E2E8,&H38000000,&H38000000,0,0,0,0,100,100,0,0,4,10,0,2,80,80,88,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[];up=0
for b in S:
    L=b.split('\n');a,e=[ts(x) for x in L[1].split(' --> ')]
    s=[x for x in T if x['t']<=a+0.05<x['t']+x['fr']/24]
    u=bool(s and s[0].get('strip'));up+=u
    ev.append(f"Dialogue: 0,{ass(a)},{ass(e)},Cap,,0,0,0,,{{\\an2\\pos(960,{862 if u else 990})}}{L[2]}")
open('caps_burn.ass','w').write(head+"\n".join(ev)+"\n");print(len(ev),'captions,',up,'raised')

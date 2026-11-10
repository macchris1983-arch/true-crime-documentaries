import json,numpy as np
from isl import load,SR,islands
src=open('splice.py').read();ns={};exec(src[src.index('CUT='):src.index('PICK=')],ns)
CUT,REP=ns['CUT'],ns['REP'];PICK=json.load(open('picks.json'));_E={}
def edits(n):
    if n in _E:return _E[n]
    ed=[(a,b,0.0) for a,b in CUT.get(n,[])]
    for a,b,k in REP.get(n,[]):
        if k in PICK:
            y=load("fix3/"+PICK[k]);I=islands(y,0.2);L=sum(b1-a1 for a1,b1 in I)+0.12*(len(I)-1)+0.10
            ed.append((a,b,L))
    _E[n]=sorted(ed);return _E[n]
def raw2fixed(n,t):
    off=0
    for a,b,L in edits(n):
        if t>=b:off+=L-(b-a)
        elif t>a:return a+off
    return t+off

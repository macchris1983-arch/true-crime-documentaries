import os
from lines import *;from cues import CUE
def starts():
    C=chunks();R={}
    for n in sorted(CUE):
        LT,e0=line_times(n,C[n]);d=os.path.getsize(f"voice2/{n}.pcm")/96000+(5 if n in("03","07","09","10") else 0)
        st=[];j=0
        for k,cue in CUE[n]:
            if cue=="@END":st.append(e0+0.3);continue
            while not LT[j][0].startswith(cue):j+=1
            st.append(max(0,LT[j][1]-0.25))
        st[0]=0;R[n]=(st,d)
    return R
if __name__=="__main__":
    for n,(st,d) in starts().items():
        ends=st[1:]+[d];print(n,[(k,round(float(b-a),1)) for (k,_),a,b in zip(CUE[n],st,ends)])

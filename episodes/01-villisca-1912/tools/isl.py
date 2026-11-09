import subprocess,numpy as np,sys
SR=48000
def load(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',f,'-f','s16le','-ac','1','-ar',str(SR),'-']),dtype=np.int16).astype(np.float32)
def islands(x,mg=0.12):
    fl=int(.01*SR);k=len(x)//fl;r=np.sqrt((x[:k*fl].reshape(k,fl)**2).mean(1));q=r<10**(-40/20)*32768
    out=[];i=0
    while i<k:
        if not q[i]:
            j=i
            while j<k:
                if q[j]:
                    m=j
                    while m<k and q[m]:m+=1
                    if (m-j)*.01>=mg:break
                    j=m
                else:j+=1
            out.append((i*.01,j*.01));i=j
        else:i+=1
    return out
if __name__=="__main__":
    n=sys.argv[1];a,b=float(sys.argv[2]),float(sys.argv[3])
    x=load(f"voice_emo_in/{n}.mp3")
    print(' '.join('%.2f-%.2f'%s for s in islands(x) if s[1]>a and s[0]<b))

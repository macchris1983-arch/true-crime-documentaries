import re,json,numpy as np
SR=48000
def chunks():
    src=open('/home/claude/villisca_vo_source.txt').read();p=re.split(r'=== CHUNK (\w+) ===\n',src)[1:]
    return dict(zip(p[0::2],p[1::2]))
def _gaps(n):
    x=np.fromfile(f"voice2/{n}.pcm",dtype=np.int16).astype(float);fl=int(.01*SR);kk=len(x)//fl
    r=np.sqrt((x[:kk*fl].reshape(kk,fl)**2).mean(1));q=r<10**(-42/20)*32768
    g=[];i=0
    while i<kk:
        if q[i]:
            j=i
            while j<kk and q[j]:j+=1
            g.append((i*.01,j*.01));i=j
        else:i+=1
    return g,kk*.01,q
def _anchors(n):
    A=json.load(open('anchors.json'))
    if n=='00':return [(i-12,t-28.15+0.4) for i,t in A['01'] if 12<=i<=25]
    if n=='01':return [(i,t) for i,t in A['01'] if i<=11]+[(i-14,t-63.40+27.88+0.7) for i,t in A['01'] if i>=26]
    return [tuple(x) for x in A.get(n,[])]
def line_times(n,b):
    L=[re.sub(r'\[[^\]]+\]\s*','',l).replace('...','').strip() for l in b.strip().splitlines() if l.strip()!='[pause]']
    L=[l for l in L if l]
    g,T,q=_gaps(n)
    s0=g[0][1] if g and g[0][0]==0 else 0
    e0=g[-1][0] if g and g[-1][1]>=T-.02 else T
    G=[x for x in g if x[0]>s0 and x[1]<e0 and x[1]-x[0]>=0.12]
    w=np.array([len(l) for l in L],float)
    anc=dict(_anchors(n));anc.setdefault(0,s0)
    # expected start time of every line: anchors fixed, others interpolated by characters between anchors
    ks=sorted(anc);E=np.zeros(len(L));cw=np.concatenate([[0],np.cumsum(w)])
    for i in range(len(L)):
        lo=max([k for k in ks if k<=i]);hi=[k for k in ks if k>i]
        if i==lo:E[i]=anc[lo];continue
        if hi:hi=hi[0];th=anc[hi]
        else:hi=len(L);th=e0
        E[i]=anc[lo]+(th-anc[lo])*(cw[i]-cw[lo])/(cw[hi]-cw[lo])
    isA=[i in anc for i in range(len(L))]
    M=len(L)-1;K=len(G)
    if M==0 or K<M:
        # fallback: proportional
        bounds=[(E[i],E[i]) for i in range(1,len(L))]
    else:
        INF=1e18;dp=np.full((M+1,K+1),INF);bk=np.zeros((M+1,K+1),int);dp[0,:]=0
        for m in range(1,M+1):
            best=INF;bi=-1
            for k in range(1,K+1):
                # choose gap k-1 for boundary m-1, previous boundary used gap < k-1
                if dp[m-1,k-1]<best:best=dp[m-1,k-1];bi=k-1
                ln=G[k-1][1]-G[k-1][0]
                g0,g1=G[k-1];a=E[m];dd=max(g0-0.35-a,a-g1-0.35,0) if isA[m] else abs((g0+g1)/2-a)
                c=(dd/(0.3 if isA[m] else 1.2))**2 - 1.5*min(ln,0.9)
                if best<INF and best+c<dp[m,k]:dp[m,k]=best+c;bk[m,k]=bi
                # dp[m,k]: boundary m uses gap k-1
        # find best end
        k=int(np.argmin(dp[M,1:]))+1;sel=[]
        for m in range(M,0,-1):
            sel.append(k-1);k=bk[m,k]
        sel=sel[::-1];bounds=[G[i] for i in sel]
    seg=[];st=s0
    for b0 in bounds:seg.append((st,b0[0]));st=b0[1]
    seg.append((st,e0))
    return [(l,a,b) for l,(a,b) in zip(L,seg)],e0

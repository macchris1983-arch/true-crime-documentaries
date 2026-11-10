import re,numpy as np
SR=48000
def chunks():
    src=open('/home/claude/villisca_vo_source.txt').read();p=re.split(r'=== CHUNK (\w+) ===\n',src)[1:]
    return dict(zip(p[0::2],p[1::2]))
def _sp(n):
    x=np.fromfile(f"voice2/{n}.pcm",dtype=np.int16).astype(float);fl=int(.01*SR);kk=len(x)//fl
    r=20*np.log10(np.sqrt((x[:kk*fl].reshape(kk,fl)**2).mean(1))/32768+1e-9);q=r<-45
    g=[];i=0
    while i<kk:
        if q[i]:
            j=i
            while j<kk and q[j]:j+=1
            g.append((i*.01,j*.01));i=j
        else:i+=1
    return g,kk*.01,q
def line_times(n,b):
    raw=[l.strip() for l in b.strip().splitlines() if l.strip()]
    L=[];strong=[]
    for l in raw:
        if l=='[pause]':
            if strong:strong[-1]=True
            continue
        t=re.sub(r'\[[^\]]+\]\s*','',l).strip()
        L.append(t.replace('...','').strip());strong.append(bool(re.search(r'([.?!]|\.\.\.)$',t)))
    g,T,q=_sp(n)
    s0=g[0][1] if g and g[0][0]==0 else 0
    e0=g[-1][0] if g and g[-1][1]>=T-.02 else T
    G=[x for x in g if x[0]>s0 and x[1]<e0 and x[1]-x[0]>=0.10]
    w=np.array([len(l) for l in L],float);cw=np.concatenate([[0],np.cumsum(w)])
    sp=np.cumsum(~q)*.01;tot=sp[-1]
    def t_at(frac):return np.searchsorted(sp,frac*tot)*.01
    M=len(L)-1;start=[s0]+[None]*M
    # pass 1: sentence boundaries -> long pauses, monotonic DP
    S=[m for m in range(1,M+1) if strong[m-1]]
    GL=[x for x in G if x[1]-x[0]>=0.28]
    if S and len(GL)>=len(S):
        E=[t_at(cw[m]/cw[-1]) for m in S];K=len(GL);INF=1e18
        dp=np.full((len(S)+1,K+1),INF);bk=np.zeros((len(S)+1,K+1),int);dp[0,:]=0
        for i in range(1,len(S)+1):
            best=INF;bi=-1
            for k in range(1,K+1):
                if dp[i-1,k-1]<best:best=dp[i-1,k-1];bi=k-1
                a,b2=GL[k-1];c=(((a+b2)/2-E[i-1])/3.0)**2-2.5*min(b2-a,1.2)
                if best<INF:dp[i,k]=best+c;bk[i,k]=bi
        k=int(np.argmin(dp[len(S),1:]))+1;sel=[]
        for i in range(len(S),0,-1):sel.append(k-1);k=bk[i,k]
        for m,gi in zip(S,sel[::-1]):start[m]=GL[gi][1]
    # pass 2: other boundaries, interpolated between known starts, snapped to a nearby pause
    known=[m for m in range(M+1) if start[m] is not None]
    for m in range(1,M+1):
        if start[m] is not None:continue
        lo=max(k for k in known if k<m);hi=[k for k in known if k>m]
        tl=start[lo];th=start[hi[0]] if hi else e0;ch=cw[hi[0]] if hi else cw[-1]
        e=tl+(th-tl)*(cw[m]-cw[lo])/(ch-cw[lo])
        c=[x for x in G if abs((x[0]+x[1])/2-e)<0.8 and x[1]>tl and (not hi or x[0]<th)]
        start[m]=min(c,key=lambda x:abs((x[0]+x[1])/2-e))[1] if c else e
    out=[]
    for m in range(M+1):
        a=start[m];b2=(start[m+1]-0.05) if m<M else e0
        out.append((L[m],a,max(b2,a+0.3)))
    return out,e0

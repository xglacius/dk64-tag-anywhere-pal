import sys; sys.argv=['x']
exec(open('xmap.py').read().split("if __name__")[0])
def jal(a): return 0x0C000000|((a&0x0FFFFFFF)>>2)
def regval(W,s,reg):
    for k in [s+1]+list(range(s-1,s-10,-1)):
        x=int(W[k])
        if (x>>26) in (9,0xD) and ((x>>21)&31)==0 and ((x>>16)&31)==reg: return x&0xFFFF
        if (x>>26)==0 and (x&0x3F)==0x25 and ((x>>11)&31)==reg: return None
    return None
def callmap(ufunc, reg=4):
    pf=match_code(ufunc); pairs={}
    sites=np.nonzero(UW==jal(ufunc))[0]
    for s in sites:
        p=match_code(US_BASE+s*4,quiet=True)
        if p is None: continue
        pi=(p-PAL_BASE)//4
        if int(PW[pi])!=jal(pf): continue
        u=regval(UW,s,reg); q=regval(PW,pi,reg)
        if u is not None and q is not None: pairs.setdefault(u,set()).add(q)
    return pairs
if __name__=='__main__':
    which=sys.orig_argv[-1] if hasattr(sys,'orig_argv') else ''

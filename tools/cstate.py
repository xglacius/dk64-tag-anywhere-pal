import sys; sys.argv=['x']
exec(open('xmap.py').read().split("if __name__")[0])
# Find "lb/lbu rX, 0x154(rY)" followed within 6 instrs by "li at,N" + beq/bne rX,at   (or addiu at,zero,N)
def consts(W, i):
    x=int(W[i]); rx=(x>>16)&31; out=[]
    for k in range(i+1, i+8):
        y=int(W[k]); op=y>>26
        if op==9 and ((y>>21)&31)==0:
            r=(y>>16)&31; val=y&0xFFFF
            for j in range(k+1,k+4):
                z=int(W[j]); zo=z>>26
                if zo in (4,5,0x14,0x15) and {(z>>21)&31,(z>>16)&31}=={rx,r}:
                    out.append((k,val)); break
    return out
pairs={}
for i in range(len(UW)):
    x=int(UW[i])
    if (x>>26) in (0x20,0x24) and (x&0xFFFF)==0x154:
        cu=consts(UW,i)
        if not cu: continue
        p=match_code(US_BASE+i*4,quiet=True)
        if p is None: continue
        pi=(p-PAL_BASE)//4
        cp=consts(PW,pi)
        if len(cp)!=len(cu): continue
        for (a,u),(b,q) in zip(cu,cp): pairs.setdefault(u,set()).add(q)
for k in sorted(pairs): print('cstate US %3d (0x%02x) -> PAL %s'%(k,k,sorted(pairs[k])))

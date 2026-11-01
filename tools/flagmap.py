import sys; sys.argv=['x']
exec(open('xmap.py').read().split("if __name__")[0])
def jal(a): return 0x0C000000 | ((a & 0x0FFFFFFF) >> 2)
def consts(words, i):
    """Return dict reg->const set by 'addiu/ori reg, zero, imm' in [i-6, i+1] (i+1 = delay slot)."""
    regs = {}
    for k in list(range(max(0, i - 8), i)) + [i + 1]:
        x = int(words[k]); op = x >> 26; rs = (x >> 21) & 31; rt = (x >> 16) & 31
        if op in (0x09, 0x0D) and rs == 0:
            regs[rt] = x & 0xFFFF if op == 0x0D else ((x & 0xFFFF) ^ 0x8000) - 0x8000
        elif op == 0 and (x & 0x3F) == 0x25 and ((x >> 16) & 31) == 0 and rs == 0:  # move rd, zero
            regs[(x >> 11) & 31] = 0
        elif op == 0 and (x & 0x3F) in (0x25, 0x21) and ((x >> 16) & 31) == 0:
            rd = (x >> 11) & 31; regs.pop(rd, None)
        elif op in IMM_OPS and op not in range(0x28, 0x30):
            if not (op in (0x09, 0x0D) and rs == 0): regs.pop(rt, None)
    return regs
res = {}
for name, ua, pa in [('check', 0x8073110C, 0x8072B850), ('set', 0x8073129C, 0x8072B9E0)]:
    sites = np.nonzero(UW == jal(ua))[0]
    for s in sites:
        uc_ = consts(UW, s)
        if 4 not in uc_: continue
        ftype = uc_.get(5 if name == 'check' else 6)
        if ftype is None: continue
        p = match_code(US_BASE + s * 4, quiet=True)
        if p is None: continue
        pi = (p - PAL_BASE) // 4
        if int(PW[pi]) != jal(pa): continue
        pc_ = consts(PW, pi)
        if 4 not in pc_: continue
        res.setdefault(ftype, {}).setdefault(uc_[4], set()).add(pc_[4])
for t in sorted(res):
    d = res[t]
    diffs = {k: v for k, v in d.items() if v != {k}}
    print('type', t, 'n=', len(d), 'diffs:', {k: sorted(v) for k, v in sorted(diffs.items())})
    print('   all US:', sorted(d))

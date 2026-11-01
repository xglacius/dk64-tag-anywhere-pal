#!/usr/bin/env python3
"""USA -> PAL address mapper for DK64 global_asm code/data, via masked instruction matching."""
import numpy as np, sys, os

W = os.path.dirname(os.path.abspath(__file__)) + '/../work/'

US_BASE = 0x805FB300
PAL_BASE = 0x805F4300

def load(v):
    code = open(W + v + '.code.bin', 'rb').read()
    data = open(W + v + '.data.bin', 'rb').read()
    return code, data

uc, ud = load('usa')
pc, pd = load('pal')
US_DATA = US_BASE + len(uc)
PAL_DATA = PAL_BASE + len(pc)

def words(b):
    return np.frombuffer(b[:len(b) // 4 * 4], dtype='>u4').astype(np.uint32)

UW = words(uc)
PW = words(pc)

IMM_OPS = {0x09, 0x0D, 0x0C, 0x0F, 0x08, 0x0A, 0x0B, 0x0E} | set(range(0x20, 0x30)) | {0x31, 0x35, 0x37, 0x39, 0x3D, 0x3F}

def masks(w):
    op = w >> 26
    m = np.full(w.shape, 0xFFFFFFFF, dtype=np.uint32)
    jj = (op == 2) | (op == 3)
    m[jj] = 0xFC000000
    imm = np.isin(op, list(IMM_OPS))
    m[imm] = 0xFFFF0000
    return m

UM = masks(UW)
PM = masks(PW)

def match_code(us_addr, before=24, after=24, quiet=False):
    """Return PAL address for a US code address."""
    idx = (us_addr - US_BASE) // 4
    for b, a in ((before, after), (16, 16), (40, 40), (8, 8), (64, 64)):
        lo = max(0, idx - b); hi = min(len(UW), idx + a)
        pat = UW[lo:hi] & UM[lo:hi]
        pm = UM[lo:hi]
        n = len(pat)
        # candidate scan using first word
        cands = np.nonzero((PW[:len(PW) - n] & pm[0]) == pat[0])[0]
        res = []
        for c in cands:
            if np.array_equal(PW[c:c + n] & pm, pat):
                res.append(c)
                if len(res) > 1:
                    break
        if len(res) == 1:
            return PAL_BASE + (res[0] + (idx - lo)) * 4
    if not quiet:
        print('  no unique match for %08x' % us_addr, file=sys.stderr)
    return None

def hi_lo_refs(addr, ram_words, base):
    """Find (lui_index, use_index) pairs that compose `addr` in a code image."""
    hi = (addr + 0x8000) >> 16
    lo = addr & 0xFFFF
    w = ram_words
    op = w >> 26
    luis = np.nonzero((op == 0x0F) & ((w & 0xFFFF) == hi))[0]
    out = []
    for li in luis:
        rt = (int(w[li]) >> 16) & 31
        for j in range(li + 1, min(li + 12, len(w))):
            x = int(w[j]); o = x >> 26
            rs = (x >> 21) & 31; rtt = (x >> 16) & 31
            if o in IMM_OPS and o != 0x0F and rs == rt and (x & 0xFFFF) == lo:
                out.append((li, j))
            # register overwritten -> stop
            if o in IMM_OPS and o not in range(0x28, 0x30) and o not in (0x39, 0x3D, 0x3F) and rtt == rt and o != 0x0F:
                if (x & 0xFFFF) != lo or rs != rt:
                    pass
            if o == 0x0F and rtt == rt:
                break
    return out

def match_data(us_addr, maxrefs=12):
    """Map a US data address to PAL by following code references."""
    refs = hi_lo_refs(us_addr, UW, US_BASE)
    votes = {}
    for li, j in refs[:maxrefs]:
        pal_use = match_code(US_BASE + j * 4, quiet=True)
        pal_lui = match_code(US_BASE + li * 4, quiet=True)
        if pal_use is None or pal_lui is None:
            continue
        pj = (pal_use - PAL_BASE) // 4; pl = (pal_lui - PAL_BASE) // 4
        hw = int(PW[pl]); lw = int(PW[pj])
        if (hw >> 26) != 0x0F:
            continue
        val = ((hw & 0xFFFF) << 16) + (((lw & 0xFFFF) ^ 0x8000) - 0x8000)
        val &= 0xFFFFFFFF
        votes[val] = votes.get(val, 0) + 1
    return votes, len(refs)

if __name__ == '__main__':
    for a in sys.argv[2:]:
        a = int(a, 16)
        if sys.argv[1] == 'code':
            r = match_code(a)
            print('%08x -> %s' % (a, ('%08x' % r) if r else None))
        else:
            v, n = match_data(a)
            print('%08x -> %s (refs %d)' % (a, {('%08x' % k): c for k, c in v.items()}, n))

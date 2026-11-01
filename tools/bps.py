#!/usr/bin/env python3
"""Minimal BPS patch apply/create (beat format)."""
import sys, zlib


def _rnum(d, i):
    data, shift = 0, 1
    while True:
        x = d[i]; i += 1
        data += (x & 0x7f) * shift
        if x & 0x80:
            break
        shift <<= 7
        data += shift
    return data, i


def _wnum(out, n):
    while True:
        x = n & 0x7f
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            break
        out.append(x)
        n -= 1


def apply(src, patch):
    assert patch[:4] == b'BPS1'
    i = 4
    ssize, i = _rnum(patch, i)
    tsize, i = _rnum(patch, i)
    msize, i = _rnum(patch, i)
    meta = patch[i:i + msize]; i += msize
    end = len(patch) - 12
    scrc, tcrc, pcrc = [int.from_bytes(patch[end + k:end + k + 4], 'little') for k in (0, 4, 8)]
    if zlib.crc32(patch[:-4]) != pcrc:
        raise ValueError('patch crc mismatch')
    if len(src) != ssize or zlib.crc32(src) != scrc:
        raise ValueError('source mismatch: size %x/%x crc %08x/%08x' % (len(src), ssize, zlib.crc32(src), scrc))
    out = bytearray(tsize)
    o = 0; srel = 0; trel = 0
    while i < end:
        n, i = _rnum(patch, i)
        cmd, length = n & 3, (n >> 2) + 1
        if cmd == 0:
            out[o:o + length] = src[o:o + length]; o += length
        elif cmd == 1:
            out[o:o + length] = patch[i:i + length]; i += length; o += length
        else:
            v, i = _rnum(patch, i)
            off = (-1 if v & 1 else 1) * (v >> 1)
            if cmd == 2:
                srel += off
                out[o:o + length] = src[srel:srel + length]; srel += length; o += length
            else:
                trel += off
                for _ in range(length):
                    out[o] = out[trel]; o += 1; trel += 1
    if zlib.crc32(out) != tcrc:
        raise ValueError('target crc mismatch')
    return bytes(out), meta


def create(src, tgt, meta=b''):
    """Simple linear BPS: SourceRead for matching runs, TargetRead otherwise.
    Also uses SourceCopy for long matches found through a block hash index."""
    out = bytearray(b'BPS1')
    _wnum(out, len(src)); _wnum(out, len(tgt)); _wnum(out, len(meta)); out += meta
    B = 16
    index = {}
    for p in range(0, len(src) - B, 4):
        index.setdefault(src[p:p + B], p)
    o = 0; srel = 0; pending = bytearray()

    def flush():
        nonlocal pending
        if pending:
            _wnum(out, ((len(pending) - 1) << 2) | 1); out.extend(pending); pending = bytearray()

    n = len(tgt)
    while o < n:
        # same-offset run
        L = 0
        while o + L < n and o + L < len(src) and src[o + L] == tgt[o + L]:
            L += 1
        if L >= 8:
            flush(); _wnum(out, ((L - 1) << 2) | 0); o += L; continue
        p = index.get(tgt[o:o + B]) if o + B <= n else None
        if p is not None:
            L = 0
            while o + L < n and p + L < len(src) and src[p + L] == tgt[o + L]:
                L += 1
            if L >= 32:
                flush()
                _wnum(out, ((L - 1) << 2) | 2)
                d = p - srel
                _wnum(out, (abs(d) << 1) | (1 if d < 0 else 0))
                srel = p + L; o += L; continue
        pending.append(tgt[o]); o += 1
    flush()
    out += zlib.crc32(src).to_bytes(4, 'little') + zlib.crc32(tgt).to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little')
    return bytes(out)


if __name__ == '__main__':
    if sys.argv[1] == 'apply':
        s = open(sys.argv[2], 'rb').read(); p = open(sys.argv[3], 'rb').read()
        t, m = apply(s, p)
        open(sys.argv[4], 'wb').write(t)
        print('ok', len(t), m)
    elif sys.argv[1] == 'create':
        s = open(sys.argv[2], 'rb').read(); t = open(sys.argv[3], 'rb').read()
        p = create(s, t)
        assert apply(s, p)[0] == t
        open(sys.argv[4], 'wb').write(p)
        print('ok', len(p))

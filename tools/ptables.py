"""DK64 pointer table reader (USA / PAL)."""
import zlib, hashlib

PT_OFFSET = {'usa': 0x101C50, 'us': 0x101C50, 'pal': 0x1038D0}
NUM_TABLES = 32


class PT:
    def __init__(self, rom, base):
        self.rom = rom
        self.base = base
        r = lambda a: int.from_bytes(rom[a:a + 4], 'big')
        self.table_addr = [r(base + i * 4) + base for i in range(NUM_TABLES)]
        self.table_len = [r(base + NUM_TABLES * 4 + i * 4) for i in range(NUM_TABLES)]

    def raw_entry(self, t, i):
        a = self.table_addr[t] + i * 4
        return int.from_bytes(self.rom[a:a + 4], 'big')

    def entry(self, t, i):
        """Return (start, end, bit_set) absolute addresses."""
        cur = self.raw_entry(t, i)
        nxt = self.raw_entry(t, i + 1)
        start = (cur & 0x7FFFFFFF) + self.base
        end = (nxt & 0x7FFFFFFF) + self.base
        return start, end, bool(cur & 0x80000000)

    def file(self, t, i):
        s, e, bit = self.entry(t, i)
        if bit:
            idx = int.from_bytes(self.rom[s:s + 2], 'big')
            return self.file(t, idx)
        return self.rom[s:e]

    def decompressed(self, t, i):
        d = self.file(t, i)
        if d[:2] == b'\x1f\x8b':
            return zlib.decompressobj(31).decompress(d)
        return d

    def uncompressed_size_addr(self, t, i):
        return self.table_addr[26] + 0 if False else None


def sha(b):
    return hashlib.sha1(b).hexdigest()[:12]

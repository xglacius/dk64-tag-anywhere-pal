"""DK64 text file (pointer table 12) editor.

Layout: <header with string records> <u16 total text length> <text area>
Each string record is 9 bytes: 01 00 00 <u16 offset> <u16 length> 00 00
(offset relative to the start of the text area). Records are located by scanning
the header and validated by checking that they tile the text area exactly.
"""


class TextFile:
    def __init__(self, data, expected_records=None):
        data = bytes(data)
        starts = [p for p in range(2, len(data)) if int.from_bytes(data[p - 2:p], 'big') == len(data) - p]
        if not starts:
            raise ValueError('cannot find text area')
        self.ts = starts[0]
        self.header = bytearray(data[:self.ts - 2])
        self.text = data[self.ts:]
        recs = []
        h = self.header
        for k in range(1, len(h) - 8):
            if h[k] == 1 and h[k + 1] == 0 and h[k + 2] == 0 and h[k + 7] == 0 and h[k + 8] == 0:
                off = int.from_bytes(h[k + 3:k + 5], 'big')
                ln = int.from_bytes(h[k + 5:k + 7], 'big')
                recs.append([k, off, ln])
        pos = 0
        for _, off, ln in sorted(recs, key=lambda r: r[1]):
            if off != pos:
                raise ValueError('records do not tile the text area at 0x%x' % pos)
            pos = off + ln
        if pos != len(self.text):
            raise ValueError('records do not cover the text area')
        if expected_records is not None and len(recs) != expected_records:
            raise ValueError('expected %d records, found %d' % (expected_records, len(recs)))
        # strings in record (header) order
        self.records = recs
        self.strings = [self.text[off:off + ln] for _, off, ln in recs]

    def find(self, s):
        s = s.encode('ascii') if isinstance(s, str) else s
        hits = [i for i, x in enumerate(self.strings) if x == s]
        if len(hits) != 1:
            raise ValueError('string %r found %d times' % (s, len(hits)))
        return hits[0]

    def replace(self, old, new):
        i = self.find(old)
        self.strings[i] = new.encode('ascii') if isinstance(new, str) else new

    def build(self):
        # Keep the original text order (sorted by original offset), rewrite offsets/lengths
        order = sorted(range(len(self.records)), key=lambda i: self.records[i][1])
        text = bytearray()
        h = bytearray(self.header)
        for i in order:
            k = self.records[i][0]
            s = self.strings[i]
            h[k + 3:k + 5] = len(text).to_bytes(2, 'big')
            h[k + 5:k + 7] = len(s).to_bytes(2, 'big')
            text += s
        return bytes(h) + len(text).to_bytes(2, 'big') + bytes(text)

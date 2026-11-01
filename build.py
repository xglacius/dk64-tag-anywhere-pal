#!/usr/bin/env python3
"""Donkey Kong 64 - Tag Anywhere V5, multi-version build (USA / PAL).

Linux port of Isotarge's build system. Requires mips64-elf-gcc and armips in PATH.

    python3 build.py --version pal --rom "Donkey Kong 64 (Europe).z64" --out rom/dk64-tag-anywhere-pal.z64 --bps
"""
import argparse, gzip, hashlib, os, shutil, subprocess, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools'))
from ptables import PT, PT_OFFSET          # noqa: E402
from dktext import TextFile                # noqa: E402
from n64tex import ENCODERS                # noqa: E402
import bps                                 # noqa: E402

VANILLA_SHA1 = {
    'us': 'cf806ff2603640a748fca5026ded28802f1f4a50',
    'pal': 'f96af883845308106600d84e0618c1a066dc6676',
}

# Pointer table file indices differ between versions
TEXTURES = {
    'us':  [('bin/Nintendo.png', 94, 'rgba5551', 'gzip'),
            ('bin/Dolby.png', 176, 'i4', 'gzip'),
            ('bin/Title.png', 44, 'rgba5551', 'zlib')],
    'pal': [('bin/Nintendo.png', 97, 'rgba5551', 'gzip'),
            ('bin/Dolby.png', 179, 'i4', 'gzip'),
            ('bin/Title.png', 47, 'rgba5551', 'zlib')],
}

# Text replacements: (file index, expected record count, [(old, new), ...])
# USA strings are exactly the ones used by the original patch (same length, same spacing).
TEXT = {
    'us': [
        (13, 3, [('PRESENTED IN', ' ' * 12),
                 ('DOLBY AND THE DOUBLE-D SYMBOL ARE', '  WITH HELP FROM THE DK64 CREW   '),
                 ('TRADEMARKS OF DOLBY LABORATORIES.', 'IT TAKES A VILLAGE TO FREE A KONG')]),
        (37, 102, [('STORY SKIP', 'SPEED MODE')]),
    ],
    # PAL text files hold 4 strings per entry: English, French, German, Spanish
    'pal': [
        (13, 12, [('PRESENTED IN', ' ' * 12),
                  ('PRESENTE EN', ' ' * 11),
                  (b'PR\xc4SENTIERT IN', ' ' * 14),
                  ('PRESENTADO EN', ' ' * 13),
                  # English and Spanish share an identical string in the vanilla file -> handled below
                  ('DOLBY ET LE SYMBOLE DOUBLE-D SONT', 'GRACE A LA DK64 CREW'),
                  ('DOLBY UND DAS DOPPEL-D SYMBOL SIND', 'MIT HILFE DER DK64 CREW'),
                  ('DES MARQUES DEPOSEES DE DOLBY LABORATORIES.', 'IL FAUT TOUT UN VILLAGE POUR LIBERER UN KONG'),
                  ('EINGETRAGENE MARKENZEICHEN DER DOLBY LABORATORIES.', 'ES BRAUCHT EIN DORF UM EINEN KONG ZU BEFREIEN')]),
        (37, 408, [('STORY SKIP', 'SPEED MODE'),
                   ('PASSER HISTOIRE', 'MODE VITESSE'),
                   ('ZWISCHENSEQUENZEN', 'SPEED-MODUS'),
                   ('SALTAR HISTORIA', 'MODO VELOCIDAD')]),
    ],
}
# PAL Dolby text: English and Spanish slots contain the same English strings.
# Record order inside each entry is EN, FR, DE, ES.
PAL_DOLBY_DUPLICATES = [
    ('DOLBY AND THE DOUBLE-D SYMBOL ARE', ['  WITH HELP FROM THE DK64 CREW   ', 'CON LA AYUDA DE LA DK64 CREW']),
    ('TRADEMARKS OF DOLBY LABORATORIES.', ['IT TAKES A VILLAGE TO FREE A KONG', 'HACE FALTA UNA ALDEA PARA LIBERAR A UN KONG']),
]

RELOCATE_TABLES = [12, 14]
FREE_SPACE = 0x2000000  # tables are appended after the original 32MB


def gz(data, level=9):
    c = bytearray(gzip.compress(data, compresslevel=level, mtime=0))
    c[9] = 3  # OS = Unix, like the vanilla files
    return bytes(c)


def zl(data):
    co = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, 25)
    c = bytearray(co.compress(data) + co.flush())
    c[4:8] = b'\0\0\0\0'
    c[9] = 3
    return bytes(c)


def patch_assets(rom, version, log):
    pt = PT(rom, PT_OFFSET[version])
    new_files = {}  # (table, index) -> (compressed bytes, uncompressed size)

    for path, idx, fmt, comp in TEXTURES[version]:
        raw = ENCODERS[fmt](os.path.join(HERE, path))
        new_files[(14, idx)] = (gz(raw) if comp == 'gzip' else zl(raw), len(raw))
        log(' - texture %s -> table 14 file %d (%s, 0x%x bytes)' % (path, idx, fmt, len(raw)))

    for idx, nrec, reps in TEXT[version]:
        tf = TextFile(pt.decompressed(12, idx), expected_records=nrec)
        assert tf.build() == pt.decompressed(12, idx), 'text round trip failed'
        for old, new in reps:
            tf.replace(old, new)
        if version == 'pal' and idx == 13:
            for old, news in PAL_DOLBY_DUPLICATES:
                old_b = old.encode('ascii')
                hits = [i for i, s in enumerate(tf.strings) if s == old_b]
                assert len(hits) == 2, (old, hits)
                for i, new in zip(hits, news):
                    tf.strings[i] = new.encode('ascii')
        raw = tf.build()
        new_files[(12, idx)] = (gz(raw), len(raw))
        log(' - text table 12 file %d (%d strings, 0x%x bytes)' % (idx, len(tf.strings), len(raw)))

    # Relocate the modified pointer tables (with all their files) to the end of the ROM
    write_ptr = max(len(rom), FREE_SPACE)
    if len(rom) < write_ptr:
        rom.extend(b'\xff' * (write_ptr - len(rom)))
    for t in RELOCATE_TABLES:
        n = pt.table_len[t]
        files = []
        for i in range(n):
            s, e, bit = pt.entry(t, i)
            assert not bit, 'bit_set entries are not supported'
            files.append(new_files[(t, i)][0] if (t, i) in new_files else pt.file(t, i))
        table_addr = write_ptr
        data_addr = table_addr + (n + 1) * 4
        blob = bytearray()
        ptrs = []
        for f in files:
            ptrs.append(data_addr + len(blob) - pt.base)
            blob += f
            if len(blob) % 2:
                blob += b'\0'
        ptrs.append(data_addr + len(blob) - pt.base)
        table = b''.join(p.to_bytes(4, 'big') for p in ptrs)
        rom.extend(table + blob)
        write_ptr = len(rom)
        while write_ptr % 0x10:
            rom.append(0)
            write_ptr += 1
        rom[pt.base + t * 4:pt.base + t * 4 + 4] = (table_addr - pt.base).to_bytes(4, 'big')
        log(' - table %d relocated to 0x%x (%d entries)' % (t, table_addr, n))

    # Uncompressed file sizes (table 26) for every replaced file
    for (t, i), (_, usize) in sorted(new_files.items()):
        size_tab = pt.entry(26, t)[0]
        a = size_tab + i * 4
        usize += usize & 1
        rom[a:a + 4] = usize.to_bytes(4, 'big')


def compile_c(version, log):
    obj = os.path.join(HERE, 'obj')
    shutil.rmtree(obj, ignore_errors=True)
    os.makedirs(obj)
    lines = []
    for root, _, files in os.walk(os.path.join(HERE, 'src')):
        for f in sorted(files):
            if not f.endswith('.c'):
                continue
            src = os.path.join(root, f)
            o = os.path.join(obj, 'src_' + f[:-2] + '.o')
            cmd = ['mips64-elf-gcc', '-Wall', '-O1', '-mtune=vr4300', '-march=vr4300', '-mabi=32',
                   '-fomit-frame-pointer', '-G0', '-fno-pic', '-mno-abicalls', '-fno-builtin',
                   '-ffreestanding', '-fno-tree-loop-distribute-patterns',
                   '-DROM_VERSION=%d' % (0 if version == 'us' else 1), '-c', src, '-o', o]
            subprocess.run(cmd, check=True)
            lines.append('.importobj "obj/%s"\n' % os.path.basename(o))
            log(' - compiled %s' % os.path.relpath(src, HERE))
    with open(os.path.join(HERE, 'asm', 'objects.asm'), 'w') as fh:
        fh.writelines(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', choices=['us', 'pal'], required=True)
    ap.add_argument('--rom', required=True, help='vanilla ROM (big endian .z64)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--bps', action='store_true', help='also create a .bps patch next to --out')
    args = ap.parse_args()
    log = print

    vanilla = open(args.rom, 'rb').read()
    sha = hashlib.sha1(vanilla).hexdigest()
    if sha != VANILLA_SHA1[args.version]:
        sys.exit('Unexpected ROM (sha1 %s). Expected %s.' % (sha, VANILLA_SHA1[args.version]))

    rom = bytearray(vanilla)
    log('[1/5] Patching pointer table assets')
    patch_assets(rom, args.version, log)

    log('[2/5] Compiling C code')
    compile_c(args.version, log)

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'wb') as fh:
        fh.write(rom)

    log('[3/5] Assembling with armips')
    subprocess.run(['armips', 'asm/main.asm', '-strequ', 'ROMFILE', out,
                    '-strequ', 'VERSIONFILE', 'asm/version_%s.asm' % args.version,
                    '-sym', os.path.splitext(out)[0] + '.sym'], check=True, cwd=HERE)

    log('[4/5] Padding and fixing CRC')
    with open(out, 'r+b') as fh:
        data = fh.read()
        if len(data) % 0x10:
            fh.write(b'\0' * (0x10 - len(data) % 0x10))
    sys.path.insert(0, HERE)
    from n64crc import fixCRC
    fixCRC(out)

    final = open(out, 'rb').read()
    log('Built %s (0x%x bytes) SHA1 %s' % (out, len(final), hashlib.sha1(final).hexdigest().upper()))
    if args.bps:
        log('[5/5] Creating BPS patch')
        p = bps.create(vanilla, final)
        assert bps.apply(vanilla, p)[0] == final
        bp = os.path.splitext(out)[0] + '.bps'
        open(bp, 'wb').write(p)
        log('Wrote %s (%d bytes)' % (bp, len(p)))
    shutil.rmtree(os.path.join(HERE, 'obj'), ignore_errors=True)


if __name__ == '__main__':
    main()

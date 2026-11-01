import sys, time
sys.path.insert(0, '.')
from m64 import *
rom = sys.argv[1]; pal = sys.argv[2] == 'pal'
A = dict(CurrentMap=0x80764BC8, StorySkip=0x8073EC7C, Player=0x807FBA6C, Character=0x80748EDC, CutsceneActive=0x8073EC3C, MovesBase=0x807FC890) if pal else \
    dict(CurrentMap=0x8076A0A8, StorySkip=0x8074452C, Player=0x807FBB4C, Character=0x8074E77C, CutsceneActive=0x807444EC, MovesBase=0x807FC950)
e = Emu(rom)
st = dict(last=None, phase='boot', t=0, tags=[], ingame=0, lastchar=None)
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
def f(emu, i):
    m = emu.r32(A['CurrentMap'])
    if m != st['last']:
        print('frame %5d map %3d phase %s' % (i, m, st['phase']), flush=True); st['last'] = m
    b = 0
    if st['phase'] == 'boot':
        if m == 80:
            st['phase'] = 'menu'; st['t'] = i
        elif i % 60 < 3: b = BTN['START']
    elif st['phase'] == 'menu':
        emu.w8(A['StorySkip'], 1)  # Speed mode on
        if m != 80:
            st['phase'] = 'loading'; st['t'] = i
        else:
            k = (i - st['t']) % 50
            if k < 3: b = BTN['A']
            elif 25 <= k < 28: b = BTN['START']
    elif st['phase'] == 'loading':
        p = emu.r32(A['Player'])
        if m == 34 and p and not emu.r8(A['CutsceneActive']):
            st['ingame'] += 1
        else:
            st['ingame'] = 0
            if (i % 80) < 3: b = BTN['START']  # skip any text/cutscene
        if st['ingame'] > 150:
            st['phase'] = 'tag'; st['t'] = i
            print('in game at frame', i, 'Character', emu.r8(A['Character']), 'Player %08x' % p, 'StorySkip', emu.r8(A['StorySkip']))
            print('kong weapon/instrument bits:', [emu.r8(A['MovesBase'] + k * 0x5E + 2) for k in range(5)])
    elif st['phase'] == 'tag':
        k = (i - st['t'])
        c = emu.r8(A['Character'])
        if c != st['lastchar']:
            print('  frame %5d Character -> %d' % (i, c)); st['lastchar'] = c; st['tags'].append(c)
        seq = ['R_DPAD'] * 6 + ['L_DPAD'] * 2 + ['L'] * 2
        n = k // 90
        if n < len(seq) and k % 90 < 2:
            b = BTN[seq[n]]
        if n >= len(seq) + 1:
            print('character sequence:', st['tags']); return False
    emu.buttons(b)
    if i >= LIMIT:
        print('limit reached in phase', st['phase']); return False
e.on_frame = f
t0 = time.time(); e.run(); print('elapsed %.1fs' % (time.time() - t0))

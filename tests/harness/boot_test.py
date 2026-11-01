import sys, time
sys.path.insert(0, '.')
from m64 import *
rom = sys.argv[1]; pal = 'pal' in sys.argv[2]
A = dict(CurrentMap=0x80764BC8, DebugInfo=0x80750C44, Arcade=0x80740F3C, Hook=0x805F51E4, Heap=0x80609760, OM2=0x8062B304, Code=0x805D3E00, StorySkip=0x8073EC7C) if pal else \
    dict(CurrentMap=0x8076A0A8, DebugInfo=0x807563B4, Arcade=0x807467EC, Hook=0x805FC164, Heap=0x80610510, OM2=0x80631FE4, Code=0x805DAE00, StorySkip=0x8074452C)
e = Emu(rom)
last = [None]; t0 = time.time()
N = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
def f(emu, i):
    m = emu.r32(A['CurrentMap'])
    if m != last[0]:
        print('frame %5d map %d' % (i, m)); last[0] = m
    # press START briefly every 100 frames
    emu.buttons(BTN['START'] if (i % 100) < 3 else 0)
    if i >= N:
        for k in ('DebugInfo', 'Arcade', 'Hook', 'Heap', 'OM2', 'Code', 'StorySkip'):
            print('%-10s %08x : %08x' % (k, A[k], emu.r32(A[k] & ~3)))
        return False
e.on_frame = f
e.run()
print('elapsed %.1fs' % (time.time() - t0))

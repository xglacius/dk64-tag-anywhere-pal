import sys, os
sys.path.insert(0, '.')
from m64 import *
rom, SH = sys.argv[1], sys.argv[2]; os.makedirs(SH, exist_ok=True)
# script: list of (frame offset after reaching menu, buttons, hold)
seq = [(60,'A'),(160,'L'),(260,'A')] + [(340+50*k,'R') for k in range(5)] + [(640+60*k,'D') for k in range(3)] + [(840+60*k,'R') for k in range(2)]
e = Emu(rom, video=True); st = dict(t=None)
def f(emu, i):
    m = emu.r32(0x80764BC8); b = 0
    if st['t'] is None:
        if m == 80: st['t'] = i
        elif i % 60 < 3: b = BTN['START']
    else:
        k = i - st['t']
        for (o, btn) in seq:
            if o <= k < o + 3:
                b = stick(80, 0) if btn == 'R' else stick(-80, 0) if btn == 'L' else stick(0, -80) if btn == 'D' else BTN[btn]
        if k % 20 == 0 and k >= 40: emu.screenshot('%s/m_%04d.png' % (SH, k))
        if k > 1000: return False
    emu.buttons(b)
e.on_frame = f; e.run()

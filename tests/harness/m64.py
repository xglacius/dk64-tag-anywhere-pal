"""Headless mupen64plus harness (ctypes) with RAM access and scripted input."""
import ctypes as C, os, threading, hashlib, shutil, tempfile

E = os.path.dirname(os.path.abspath(__file__)) + '/..'
CORE = E + '/mupen64plus-core/projects/unix/libmupen64plus.so.2.0.0'
RSP = E + '/mupen64plus-rsp-hle/projects/unix/mupen64plus-rsp-hle.so'
INPUT = E + '/harness/scriptinput.so'
GFX_LLE = E + '/angrylion-rdp-plus/headless/mupen64plus-video-angrylion-headless.so'
RSP_LLE = E + '/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4-sse2.so'

DEBUGCB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_char_p)
STATECB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_int)
FRAMECB = C.CFUNCTYPE(None, C.c_uint)

BTN = dict(R_DPAD=0x0001, L_DPAD=0x0002, D_DPAD=0x0004, U_DPAD=0x0008, START=0x0010, Z=0x0020,
           B=0x0040, A=0x0080, CR=0x0100, CL=0x0200, CD=0x0400, CU=0x0800, R=0x1000, L=0x2000)


def stick(x, y):
    return ((x & 0xFF) << 16) | ((y & 0xFF) << 24)


class Emu:
    def __init__(self, rom_path, verbose=False, emumode=1, video=False):
        self.video = video
        if not video:
            os.environ['HEADLESS_DP'] = '1'
        else:
            os.environ.pop('HEADLESS_DP', None)
        self.verbose = verbose
        self.tmp = tempfile.mkdtemp(prefix='m64_')
        rom = open(rom_path, 'rb').read()
        md5 = hashlib.md5(rom).hexdigest().upper()
        ini = open(E + '/mupen64plus-core/data/mupen64plus.ini').read()
        ini += '\n[%s]\nGoodName=Test ROM\nSaveType=Eeprom 16KB\nPlayers=4\nCountPerOp=1\n' % md5
        open(self.tmp + '/mupen64plus.ini', 'w').write(ini)
        shutil.copy(E + '/mupen64plus-core/data/font.ttf', self.tmp)
        self.core = C.CDLL(CORE)
        self._dbg = DEBUGCB(self._debug)
        self._st = STATECB(lambda c, p, v: None)
        r = self.core.CoreStartup(0x020001, self.tmp.encode(), self.tmp.encode(), None, self._dbg, None, self._st)
        assert r == 0, r
        h = C.c_void_p(); self.core.ConfigOpenSection(b"Core", C.byref(h))
        m = C.c_int(emumode); self.core.ConfigSetParameter(h, b"R4300Emulator", 1, C.byref(m))
        self.romb = C.create_string_buffer(rom, len(rom))
        r = self.core.CoreDoCommand(1, len(rom), self.romb)
        assert r == 0, 'ROM_OPEN %d' % r
        self.rsp = C.CDLL(RSP_LLE if video else RSP)
        self.inp = C.CDLL(INPUT)
        libs = [(self.inp, 4), (self.rsp, 1)]
        if video:
            self.gfx = C.CDLL(GFX_LLE)
            self.gfx.ALGetFrame.restype = C.c_void_p
            libs = [(self.gfx, 2)] + libs
        for lib, t in libs:
            lib.PluginStartup(C.c_void_p(self.core._handle), None, self._dbg)
            r = self.core.CoreAttachPlugin(t, C.c_void_p(lib._handle))
            assert r == 0, ('attach', t, r)
        self.core.CoreGetRdramPtr.restype = C.c_void_p
        self.frame = 0
        self.on_frame = None
        self._fcb = FRAMECB(self._frame)
        self.core.CoreDoCommand(15, 0, self._fcb)  # SET_FRAME_CALLBACK
        self.done = threading.Event()

    def _debug(self, ctx, level, msg):
        if self.verbose or level <= 1:
            print('[m64 %d] %s' % (level, msg.decode(errors='replace')))

    def ram(self):
        if not hasattr(self, '_ram'):
            p = self.core.CoreGetRdramPtr()
            self._ram = (C.c_uint32 * (0x800000 // 4)).from_address(p)
        return self._ram

    def r32(self, a):
        return self.ram()[(a & 0x7FFFFF) >> 2]

    def r8(self, a):
        return (self.r32(a & ~3) >> (24 - 8 * (a & 3))) & 0xFF

    def r16(self, a):
        return (self.r32(a & ~3) >> (16 - 8 * (a & 2))) & 0xFFFF

    def w8(self, a, v):
        i = (a & 0x7FFFFF) >> 2
        sh = 24 - 8 * (a & 3)
        self.ram()[i] = (self.ram()[i] & ~(0xFF << sh) & 0xFFFFFFFF) | ((v & 0xFF) << sh)

    def w32(self, a, v):
        self.ram()[(a & 0x7FFFFF) >> 2] = v & 0xFFFFFFFF

    def buttons(self, v):
        self.inp.SetButtons(0, C.c_uint32(v))

    def _frame(self, idx):
        self.frame = idx
        if idx == 1:
            v = C.c_int(0)
            self.core.CoreDoCommand(17, 5, C.byref(v))  # disable speed limiter
        if self.on_frame:
            try:
                if self.on_frame(self, idx) is False:
                    self.core.CoreDoCommand(6, 0, None)  # STOP
            except Exception as ex:  # noqa
                import traceback; traceback.print_exc()
                self.core.CoreDoCommand(6, 0, None)

    def run(self):
        r = self.core.CoreDoCommand(5, 0, None)  # EXECUTE (blocks until stop)
        return r

    def screenshot(self, path):
        from PIL import Image
        w = C.c_uint32(); h = C.c_uint32(); n = C.c_uint32()
        p = self.gfx.ALGetFrame(C.byref(w), C.byref(h), C.byref(n))
        if not p:
            return False
        buf = C.string_at(p, w.value * h.value * 4)
        Image.frombuffer('RGBA', (w.value, h.value), buf, 'raw', 'RGBA', 0, 1).convert('RGB').save(path)
        return True

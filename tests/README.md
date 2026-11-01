# Automated tests (headless emulator)

Python (ctypes) harness on top of **mupen64plus-core**, with RDRAM read/write access and a scriptable controller.

Components:
- `harness/m64.py` – loads the core and plugins and exposes `r8/r16/r32/w8/w32`, `buttons()` and `screenshot()`.
- `harness/scriptinput.c` – minimal input plugin (`gcc -shared -fPIC -o scriptinput.so scriptinput.c`).
- `mupen64plus-core.patch` – adds `CoreGetRdramPtr()` and, only with `HEADLESS_DP=1`, the DP interrupt the dummy video plugin never raises.
- `angrylion_headless_vdac.c` – replaces angrylion-rdp-plus's OpenGL output with an in-memory buffer (`ALGetFrame`) for screenshots.

Modes: no video (rsp-hle + dummy video, fast) or video (rsp-cxd4 + angrylion, real screenshots).

Scripts:
- `boot_test.py` – boot and RAM markers (hook, heap, custom code running).
- `tag_test.py` – Speed Mode, new file and a D-Pad Right/Left/L tag sequence.
- `tag_test_normal.py` – normal mode (intro, DK's house, tagging blocked).
- `tag_shots.py`, `menu_shots.py` – same with screenshots.

The core/plugin paths are at the top of `m64.py`; adjust them to your build.

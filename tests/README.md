# Pruebas automáticas (emulador sin interfaz)

Arnés en Python (ctypes) sobre **mupen64plus-core**, con lectura/escritura de RDRAM y mando programable.

Componentes:
- `harness/m64.py` – carga el core, plugins y expone `r8/r16/r32/w8/w32`, `buttons()` y `screenshot()`.
- `harness/scriptinput.c` – plugin de entrada mínimo (`gcc -shared -fPIC -o scriptinput.so scriptinput.c`).
- `mupen64plus-core.patch` – añade `CoreGetRdramPtr()` y, solo con `HEADLESS_DP=1`, la interrupción DP que el vídeo dummy no genera.
- `angrylion_headless_vdac.c` – sustituye la salida OpenGL de angrylion-rdp-plus por un búfer en memoria (`ALGetFrame`) para capturas.

Modos: sin vídeo (rsp-hle + vídeo dummy, rápido) o con vídeo (rsp-cxd4 + angrylion, capturas reales).

Scripts:
- `boot_test.py` – arranque y marcadores en RAM (hook, heap, código propio en ejecución).
- `tag_test.py` – Speed Mode, partida nueva y secuencia de tags D-Pad der./izq./L.
- `tag_test_normal.py` – modo normal (intro, casa de DK, tag bloqueado).
- `tag_shots.py`, `menu_shots.py` – lo mismo con capturas.

Las rutas a core/plugins están al principio de `m64.py`; ajústalas a tu compilación.

# Donkey Kong 64 – Tag Anywhere V5 · Port a PAL (Europa En,Fr,De,Es)

Port del parche **Tag Anywhere V5** de Isotarge (https://github.com/Isotarge/dk64-tag-anywhere) a la ROM europea.
Mismo código fuente que el parche USA, recompilado con las direcciones PAL.

## Aplicar el parche

ROM base: **Donkey Kong 64 (Europe) (En,Fr,De,Es)** en formato **.z64 (big-endian)**

| | |
|---|---|
| SHA-1 ROM base (.z64) | `F96AF883845308106600D84E0618C1A066DC6676` |
| CRC32 ROM base (.z64) | `A28C71C6` |
| SHA-1 ROM resultante | `EFCC466967EA39A406B6CC12D107ABE2F96E1CC1` |

Hay dos parches, según el formato de tu ROM (aplícalos con Floating IPS, beat o https://www.marcrobledo.com/RomPatcher.js/):

| Parche | ROM base | CRC32 base | Resultado |
|---|---|---|---|
| `dk64-tag-anywhere-v5-pal.bps` | `.z64` (big-endian) | `A28C71C6` | `.z64` |
| `dk64-tag-anywhere-v5-pal-n64.bps` | `.n64` (byte-swapped, la de No-Intro) | `FC37B06A` | `.n64` |

Ambos dan exactamente la misma ROM, solo cambia el orden de bytes.

> **Consola real / flashcart: usa el `.z64`.** Probado en N64 PAL con **ED64 Plus**: la ROM `.z64` funciona perfectamente, mientras que la versión byte-swapped (la que genera el parche `-n64`) se queda en **pantalla negra**.
> Si tu ROM es `.n64`/`.v64`, conviértela primero a `.z64` (RomPatcher.js o Tool64; debe dar CRC32 `A28C71C6`) y aplica `dk64-tag-anywhere-v5-pal.bps`.
> El parche `-n64` sirve para emuladores, que aceptan cualquier orden de bytes.
>
> Nota: aunque la ROM No-Intro se llame `.n64`, en realidad está byte-swapped (empieza por `37 80 40 12`, lo que normalmente es `.v64`). El `.z64` empieza por `80 37 12 40`.

Igual que la versión USA: usa guardado **EEPROM 16K** en el emulador y, en BizHawk, activa el Expansion Slot.

## Controles y funciones
Iguales que el original: D-Pad derecha o L = siguiente kong, D-Pad izquierda = anterior (DK → Diddy → Lanky → Tiny → Chunky).
La opción **SPEED MODE** sustituye a STORY SKIP en el menú de opciones (traducida en los 4 idiomas: MODE VITESSE / SPEED-MODUS / MODO VELOCIDAD).

## Diferencias PAL encontradas (y corregidas)
- Todas las direcciones de código y datos (≈40) re-mapeadas por firma de instrucciones y cruzadas con el dk64-practice-rom.
- **Flags temporales +1** en PAL (las intros largas de jefes del Speed Mode: 104→105, etc.).
- **Acción de intercambio de kong 0x3B → 0x3C** (la lista de acciones PAL tiene una entrada extra). Sin esto el tag no cambia de kong.
- Índices de ficheros distintos: textos (12/13 y 12/37 con 4 idiomas), texturas (14/97, 14/179, 14/47).
- El código propio va en ROM `0x1FF5000` (la PAL ocupa hasta `0x1FF4E7F`) y en RAM `0x805D3E00` (heap reducido 0x20000, como en USA).
- Las parches al código global (heap, Object Model 2) se aplican en el hook de arranque en lugar de recomprimir el bloque de código, con writeback/invalidación de caché.

## Verificación hecha
Pruebas automáticas en mupen64plus (cached interpreter + angrylion RDP software):
- La ROM arranca, muestra logos/título de Tag Anywhere y llega al menú.
- Speed Mode: partida nueva directamente en DK Isles, movimientos desbloqueados; tag D-Pad der./izq./L recorre DK→Diddy→Lanky→Tiny→Chunky→DK y hacia atrás, idéntico al parche USA oficial en la misma prueba.
- Modo normal: intro completa, empieza en la casa de DK, sin tag a kongs bloqueados; las instrucciones parcheadas vuelven a sus valores originales.
- Speed Mode se conserva tras reiniciar.

Hardware real: probado en N64 PAL con ED64 Plus usando la ROM `.z64` — funciona.

No probado aún: el salto de bailes de plátano dorado en la práctica, la compresión de cutscenes de Snide/K. Lumsy y T&S.

## Opciones de diagnóstico de `build.py`
`--no-assets` (ROM de 32 MB, sin textos/logos), `--pad64` (rellena a 64 MB) y `--no-cacheops` (sin vaciado de caché en el arranque). No hacen falta para el uso normal; se añadieron para aislar problemas en hardware.

## Compilar
Requisitos: Python 3 + Pillow, `mips64-elf-gcc` y `armips` en el PATH.

    python3 build.py --version pal --rom "DK64 (Europe).z64" --out rom/dk64-tag-anywhere-v5-pal.z64 --bps

`--version us` construye la versión USA con el mismo pipeline.

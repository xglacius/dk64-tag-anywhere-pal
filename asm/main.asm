; Donkey Kong 64 - Tag Anywhere (multi-version build: USA / PAL)
; Usage: armips main.asm -strequ ROMFILE <rom> -strequ VERSIONFILE asm/version_xx.asm
.n64
.open ROMFILE, 0

.include VERSIONFILE

; ---------------------------------------------------------------
; CRC check patch (same as the original USA patch)
.headersize (crcPatchRAM - crcPatchROM)
.org crcPatchRAM
NOP

; ---------------------------------------------------------------
; Boot hook: DMA our code from ROM to RAM and run it
.headersize (bootHookRAM - bootHookROM)
.org bootHookRAM
modifiedBootCode:
	LI a0, customCodeROM                          ; Start of ROM copy
	LI a1, (customCodeROM + (customCodeEnd - customCodeRAM)) ; End of ROM copy
	LUI a2, hi(customCodeRAM)
	JAL dmaFileTransfer
	ADDIU a2, a2, lo(customCodeRAM)               ; RAM location to copy to
	J displacedVanillaBootCode
	NOP
.if org() != bootHookReturn
	.error "Boot hook size mismatch"
.endif

; ---------------------------------------------------------------
.headersize (customCodeRAM - customCodeROM)
.org customCodeRAM

displacedVanillaBootCode:
	; --- Runtime patches to the global code (done here instead of recompressing it) ---
	; Heap shrink: heap end 0x805xxE00 -> 0x805(xx-2)E00, makes room for this code
	LUI t3, hi(heapEndWriteUpper)
	LHU t4, lo(heapEndWriteUpper) (t3)
	ADDIU t4, t4, -2
	SH t4, lo(heapEndWriteUpper) (t3)
	; Increase Object Model 2 per map count (530 for every map)
	LUI t3, hi(om2CountBlock)
	ADDIU t3, t3, lo(om2CountBlock)
	ADDIU t4, r0, 0x0212
	SH t4, 0x02 (t3) ; Fungi Forest (530)
	SH t4, 0x12 (t3) ; Frantic Factory (500)
	SH t4, 0x22 (t3) ; Angry Aztec (500)
	SH t4, 0x32 (t3) ; Gloomy Galleon (485)
	SH t4, 0x42 (t3) ; Jungle Japes (465)
	SH t4, 0x52 (t3) ; All Other Maps (450)
	; Write per frame hook
	LUI t3, hi(mainASMFunctionJump)
	LW t3, lo(mainASMFunctionJump) (t3)
	LUI t4, hi(frameHookLocation)
	SW t3, lo(frameHookLocation) (t4)
	; Make sure the instruction writes reach RAM before the code runs
.if CACHEOPS == 1
	JAL osWritebackDCacheAll
	NOP
	LUI a0, hi(globalCodeStart)
	ADDIU a0, a0, lo(globalCodeStart)
	LUI a1, hi(globalCodeSize)
	JAL osInvalICache
	ADDIU a1, a1, lo(globalCodeSize)
.endif
	; --- Vanilla code displaced by the hook ---
	LUI v0, 0x8001
	ADDIU v0, v0, bootLui2
	LUI t3, 0 ; These make multiplayer not hard crash
	LUI t4, 1 ; These make multiplayer not hard crash
	LUI t5, 1 ; These make multiplayer not hard crash
	LUI t9, 0xD ; These make multiplayer not hard crash
	LUI t8, 0xD ; These make multiplayer not hard crash
	LUI t6, bootT6Upper
	J bootHookReturn
	ADDIU t4, t4, bootT4Addition

mainASMFunction:
	JAL frameLoop
	NOP
	JAL cFuncLoop
	NOP
	J frameHookReturn
	NOP

mainASMFunctionJump:
	J mainASMFunction ; Instruction copied and used as a hook
	NOP

.align 0x10

.include "asm/objects.asm"

.align 0x10
customCodeEnd:
.if customCodeEnd > (customCodeRAM + 0x20000)
	.error "Custom code does not fit in the reserved RAM area"
.endif
.close

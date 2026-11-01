; ---------------- USA ----------------
ROM_IS_PAL equ 0
; Boot hook (9 instructions overwritten, executes at the end of boot after global code is loaded)
bootHookROM equ 0x1364
bootHookRAM equ 0x80000764
bootHookReturn equ 0x80000788
bootLui2 equ 0xDCC4
bootT6Upper equ 0x000D
bootT4Addition equ 0x1320
; Custom code location
customCodeROM equ 0x01FED020
customCodeRAM equ 0x805DAE00
; Per frame hook
.definelabel frameHookLocation, 0x805FC164
.definelabel frameLoop, 0x805FC2B0
.definelabel frameHookReturn, 0x805FC16C
; CRC check patch
crcPatchROM equ 0x3154
crcPatchRAM equ 0x80002554
; Runtime patches to global code
.definelabel heapEndWriteUpper, 0x80610512 ; lui t5, 0x805F -> 0x805D
.definelabel om2CountBlock, 0x80631FE4    ; li t8, 530 / t9, 500 / t0, 500 / t1, 485 / t2, 465 / t3, 450
.definelabel globalCodeStart, 0x805FB300
.definelabel globalCodeSize, 0x00149160
; libultra
.definelabel osInvalICache, 0x80005260
.definelabel osWritebackDCacheAll, 0x800052E0
; Game functions / data
.definelabel dmaFileTransfer, 0x80000450
.definelabel setFlag, 0x8073129C
.definelabel checkFlag, 0x8073110C
.definelabel playSound, 0x80609140
.definelabel CurrentMap, 0x8076A0A8
.definelabel ParentMap, 0x8076A172
.definelabel StorySkip, 0x8074452C
.definelabel MovesBase, 0x807FC950
.definelabel CollectableBase, 0x807FCC40
.definelabel CutsceneIndex, 0x807476F4
.definelabel CutsceneTimer, 0x807476F0
.definelabel CutsceneActive, 0x807444EC
.definelabel ActorArray, 0x807FBFF0
.definelabel ActorCount, 0x807FC3F0
.definelabel LZFadeoutProgress, 0x807FD888
.definelabel TBVoidByte, 0x807FBB63
.definelabel IsAutowalking, 0x807463B8
.definelabel HUD, 0x80754280
.definelabel Player, 0x807FBB4C
.definelabel Character, 0x8074E77C
.definelabel NewlyPressedControllerInput, 0x807ECD66
.definelabel SwapObject, 0x807FC924

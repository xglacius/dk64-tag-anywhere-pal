; ---------------- PAL (Europe En,Fr,De,Es) ----------------
; All addresses below were derived by matching the USA code against the PAL code
; (masked instruction signatures) and cross-checked against the dk64-practice-rom PAL symbols.
ROM_IS_PAL equ 1
bootHookROM equ 0x1420
bootHookRAM equ 0x80000820
bootHookReturn equ 0x80000844
bootLui2 equ 0xDED4
bootT6Upper equ 0x000E
bootT4Addition equ 0x18E0
; PAL ROM data extends to 0x1FF4E7F, first free space after it
customCodeROM equ 0x01FF5000
; Heap end lowered by 0x20000 (0x805F3E00 -> 0x805D3E00), same as the USA patch
customCodeRAM equ 0x805D3E00
.definelabel frameHookLocation, 0x805F51E4
.definelabel frameLoop, 0x805F5330
.definelabel frameHookReturn, 0x805F51EC
crcPatchROM equ 0x32D4
crcPatchRAM equ 0x800026D4
.definelabel heapEndWriteUpper, 0x80609762
.definelabel om2CountBlock, 0x8062B304
.definelabel globalCodeStart, 0x805F4300
.definelabel globalCodeSize, 0x0014A8B0
.definelabel osInvalICache, 0x80005470
.definelabel osWritebackDCacheAll, 0x800054F0
.definelabel dmaFileTransfer, 0x800004CC
.definelabel setFlag, 0x8072B9E0
.definelabel checkFlag, 0x8072B850
.definelabel playSound, 0x80602210
.definelabel CurrentMap, 0x80764BC8
.definelabel ParentMap, 0x80764C92
.definelabel StorySkip, 0x8073EC7C
.definelabel MovesBase, 0x807FC890
.definelabel CollectableBase, 0x807FCB80
.definelabel CutsceneIndex, 0x80741E54
.definelabel CutsceneTimer, 0x80741E50
.definelabel CutsceneActive, 0x8073EC3C
.definelabel ActorArray, 0x807FBF10
.definelabel ActorCount, 0x807FC310
.definelabel LZFadeoutProgress, 0x807FD7C8
.definelabel TBVoidByte, 0x807FBA83
.definelabel IsAutowalking, 0x80740B08
.definelabel HUD, 0x8074E9E0
.definelabel Player, 0x807FBA6C
.definelabel Character, 0x80748EDC
.definelabel NewlyPressedControllerInput, 0x807ECC86
.definelabel SwapObject, 0x807FC864

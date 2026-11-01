#ifndef _VERSION_ADDRS_H_
#define _VERSION_ADDRS_H_

// ROM_VERSION is passed on the compiler command line: 0 = USA, 1 = PAL (Europe)
#ifndef ROM_VERSION
#error "ROM_VERSION must be defined (0 = USA, 1 = PAL)"
#endif

// Helper to build a MIPS JAL instruction word at compile time
#define JAL_INSN(addr) (0x0C000000 | (((addr) & 0x0FFFFFFF) >> 2))

#if ROM_VERSION == 0
	// ---------------- USA ----------------
	#define ADDR_DEBUG_INFO_ON      0x807563B4 // u8, enables crash debugger
	#define ADDR_DEBUG_COLUMN_LOOP  0x80731F78 // instruction NOP'd for crash debugger
	#define ADDR_ARCADE_HISCORES    0x807467EC // u32[5]
	#define ADDR_FILE_START_MAP     0x80714547 // low byte of "li a0, 0xB0"
	#define ADDR_FILE_START_EXIT    0x8071455B // low byte of "li a1, 1"
	#define ADDR_TNS_FEED_BRANCH    0x806BE3E0 // bnez t3, ... (T&S feeding)
	#define ADDR_KLUMSY_BRANCH      0x806BDC98 // bne v1, at, ... (K. Lumsy cutscene)
	#define ADDR_GB_DANCE_ANIM_JAL  0x806EFB88
	#define ADDR_GB_DANCE_MOVEMENT  0x806EFB9C
	#define ADDR_GB_DANCE_CS_PROG   0x806EFBA8
	#define ADDR_GB_DANCE_ROTATION  0x806EFC0C
	#define ADDR_GB_DANCE_CS_JAL    0x806EFC1C
	#define FUNC_GB_DANCE_ANIM      0x80614E78 // target of the animation JAL
	#define FUNC_GB_DANCE_CS        0x80627948 // target of the cutscene JAL
	// Temporary (type 2) flags are offset by one in the PAL version
	#define TEMP_FLAG(x) (x)
	// SwapObject action that performs a kong swap (tag barrel)
	#define SWAP_ACTION_TAG 0x3B
#elif ROM_VERSION == 1
	// ---------------- PAL (Europe En,Fr,De,Es) ----------------
	#define ADDR_DEBUG_INFO_ON      0x80750C44
	#define ADDR_DEBUG_COLUMN_LOOP  0x8072C6B8
	#define ADDR_ARCADE_HISCORES    0x80740F3C
	#define ADDR_FILE_START_MAP     0x8070EB93
	#define ADDR_FILE_START_EXIT    0x8070EBA7
	#define ADDR_TNS_FEED_BRANCH    0x806B81D0
	#define ADDR_KLUMSY_BRANCH      0x806B7A88
	#define ADDR_GB_DANCE_ANIM_JAL  0x806EA278
	#define ADDR_GB_DANCE_MOVEMENT  0x806EA28C
	#define ADDR_GB_DANCE_CS_PROG   0x806EA298
	#define ADDR_GB_DANCE_ROTATION  0x806EA2FC
	#define ADDR_GB_DANCE_CS_JAL    0x806EA30C
	#define FUNC_GB_DANCE_ANIM      0x8060E108
	#define FUNC_GB_DANCE_CS        0x80620C50
	#define TEMP_FLAG(x) ((x) + 1)
	// The PAL action list has one extra entry before this one (USA 0x3B -> PAL 0x3C)
	#define SWAP_ACTION_TAG 0x3C
#else
	#error "Unsupported ROM_VERSION"
#endif

// Instruction words identical in every version (verified against both ROMs)
#define INSN_GB_DANCE_MOVEMENT  0xA1EE0154 // sb t6, 0x154(t7)
#define INSN_GB_DANCE_ROTATION  0xA58200E6 // sh v0, 0xE6(t4)
#define INSN_GB_DANCE_CS_PROG   0xA3000155 // sb zero, 0x155(t8)
#define INSN_TNS_FEED_BRANCH    0x15600099
#define INSN_KLUMSY_BRANCH      0x14610012

#endif

#include "../include/common.h"

void cFuncLoop(void) {
	// Enable stack trace upon crash
	*(s8 *)(ADDR_DEBUG_INFO_ON) = 1;
	*(s32 *)(ADDR_DEBUG_COLUMN_LOOP) = 0;

	// Set Arcade High Scores
	*(u32 *)(ADDR_ARCADE_HISCORES + 0x00) = 999950;
	*(u32 *)(ADDR_ARCADE_HISCORES + 0x04) = 999950;
	*(u32 *)(ADDR_ARCADE_HISCORES + 0x08) = 999950;
	*(u32 *)(ADDR_ARCADE_HISCORES + 0x0C) = 999950;
	*(u32 *)(ADDR_ARCADE_HISCORES + 0x10) = 999950;

	// Unlock Mystery Menu
	if (!checkFlag(0, 1)) {
		for (s32 i = 0; i < 35; i++) {
			setFlag(i, 1, 1);
		}
	}

	// Fix Bone Displacement
	// Note: This will crash on console
	// Note: Only enable this if you're playing on old versions of BizHawk, mupen64(plus) or PJ64
	// (USA only) *(u32 *)(0x8061963C) = 0x00000000;

	tagAnywhere();
}

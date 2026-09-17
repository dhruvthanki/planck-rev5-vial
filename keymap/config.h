/* SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

#define VIAL_KEYBOARD_UID {0x12, 0x50, 0xF5, 0xD3, 0x5E, 0x4A, 0x53, 0x8C}
#define DYNAMIC_KEYMAP_LAYER_COUNT 4

// Unlock combo is 'Esc' (matrix 1,0) + 'Space' (matrix 3,5)
#define VIAL_UNLOCK_COMBO_ROWS { 1, 3 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 5 }

/* Home row mods.
 *
 * CHORDAL_HOLD only allows a hold when the mod-tap and the next key are on
 * opposite hands, which kills the classic misfire where a fast same-hand roll
 * like "sa" comes out as Alt+A. It requires chordal_hold_layout in keymap.c --
 * without it the array is zero-filled, every chord looks same-handed, and no
 * mod ever fires. FLOW_TAP suppresses holds entirely during fast typing.
 *
 * QUICK_TAP_TERM 0 both disables tap-then-hold key repeat and saves 172 bytes,
 * since the quick-tap logic compiles out.
 *
 * Tune TAPPING_TERM at runtime with DT_UP / DT_DOWN, then DT_PRNT the value and
 * set it here -- the runtime value lives in RAM and resets on replug.
 */
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD
#define QUICK_TAP_TERM 0
#define FLOW_TAP_TERM 150

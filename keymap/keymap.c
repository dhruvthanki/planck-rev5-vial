/* Copyright 2015-2017 Jack Humbert
 * Updated 2020 mixedfeelings
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * Planck rev5 Vial keymap.
 *
 * Derived from the planck/light Vial keymap in vial-qmk; the rev5 shares the
 * same 4x12 matrix and 1x2uC layout option.
 *
 * KC_SPC sits on both 3,5 and 3,6 so one firmware covers both the MIT (2u
 * spacebar) and grid (2x 1u) builds of the board.
 *
 * This is only a starting point -- remap in the Vial GUI, not here.
 */

#include QMK_KEYBOARD_H

/* Handedness for CHORDAL_HOLD. A hold is only permitted when the mod-tap and the
 * key that follows it are on opposite hands; '*' exempts a key from the rule.
 * The bottom row is all '*' so the layer switches always register as holds. */
const char chordal_hold_layout[MATRIX_ROWS][MATRIX_COLS] PROGMEM = {
    {'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R'},
    {'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R'},
    {'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R'},
    {'*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'},
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    /* Qwerty
    * ,-----------------------------------------------------------------------------------.
    * | Tab  |   Q  |   W  |   E  |   R  |   T  |   Y  |   U  |   I  |   O  |   P  | Bksp |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * | Esc  |  A   |  S   |  D   |  F   |   G  |   H  |  J   |  K   |  L   |  ;   |  "   |
    * |      | GUI  | Alt  | Ctrl |Shift |      |      |Shift | Ctrl | Alt  | GUI  |      |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * | Shift|   Z  |   X  |   C  |   V  |   B  |   N  |   M  |   ,  |   .  |   /  |Enter |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |Adjust| Ctrl | Alt  | GUI  |Lower |    Space    |Raise | Left | Down |  Up  |Right |
    * `-----------------------------------------------------------------------------------'
    */
    [0] =  LAYOUT_ortho_4x12 (
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,  KC_T,   KC_Y,   KC_U,  KC_I,    KC_O,    KC_P,    KC_BSPC,
        KC_ESC,  LGUI_T(KC_A), LALT_T(KC_S), LCTL_T(KC_D), LSFT_T(KC_F), KC_G,
        KC_H,    RSFT_T(KC_J), RCTL_T(KC_K), RALT_T(KC_L), RGUI_T(KC_SCLN), KC_QUOT,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,  KC_B,   KC_N,   KC_M,  KC_COMM, KC_DOT,  KC_SLSH, KC_ENT,
        MO(3),   KC_LCTL, KC_LALT, LM(1, MOD_LGUI), MO(1), KC_SPC, KC_SPC, MO(2), KC_LEFT, KC_DOWN, KC_UP, KC_RGHT
    ),

    /* Lower
    * ,-----------------------------------------------------------------------------------.
    * |   ~  |   !  |   @  |   #  |   $  |   %  |   ^  |   &  |   *  |   (  |   )  | Bksp |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * | Del  |  F1  |  F2  |  F3  |  F4  |  F5  | Left | Down |  Up  |Right |   }  |  |   |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      |  F7  |  F8  |  F9  |  F10 |  F11 |  F12 |ISO ~ |ISO | | Home | End  |      |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      |      |      |      |      |             |Adjust| Next | Vol- | Vol+ | Play |
    * `-----------------------------------------------------------------------------------'
    */
    [1] = LAYOUT_ortho_4x12 (
        KC_TILD, KC_EXLM, KC_AT,   KC_HASH, KC_DLR,  KC_PERC, KC_CIRC, KC_AMPR,    KC_ASTR,    KC_LPRN, KC_RPRN, KC_BSPC,
        KC_DEL,  KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_LEFT, KC_DOWN,    KC_UP,      KC_RGHT, KC_RCBR, KC_PIPE,
        KC_TRNS, KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,  S(KC_NUHS), S(KC_NUBS), KC_HOME, KC_END,  KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, MO(3),      KC_MNXT,    KC_VOLD, KC_VOLU, KC_MPLY
    ),

    /* Raise
    * ,-----------------------------------------------------------------------------------.
    * |   `  |   1  |   2  |   3  |   4  |   5  |   6  |   7  |   8  |   9  |   0  | Bksp |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * | Del  |  F1  |  F2  |  F3  |  F4  |  F5  |  F6  |   -  |   =  |   [  |   ]  |  \   |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      |  F7  |  F8  |  F9  |  F10 |  F11 |  F12 |ISO # |ISO / |Pg Up |Pg Dn |      |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      |      |      |      |Adjust|             |      | Next | Vol- | Vol+ | Play |
    * `-----------------------------------------------------------------------------------'
    */
    [2] = LAYOUT_ortho_4x12 (
        KC_GRV,  KC_1,    KC_2,    KC_3,    KC_4,   KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_BSPC,
        KC_DEL,  KC_F1,   KC_F2,   KC_F3,   KC_F4,  KC_F5,   KC_F6,   KC_MINS, KC_EQL,  KC_LBRC, KC_RBRC, KC_BSLS,
        KC_TRNS, KC_F7,   KC_F8,   KC_F9,   KC_F10, KC_F11,  KC_F12,  KC_NUHS, KC_NUBS, KC_PGUP, KC_PGDN, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, MO(3),  KC_TRNS, KC_TRNS, KC_TRNS, KC_MNXT, KC_VOLD, KC_VOLU, KC_MPLY
    ),

    /* Utility
    *
    * DT_DOWN / DT_UP nudge TAPPING_TERM by 10ms while you type; DT_PRNT types the
    * current value out. The runtime value is RAM-only and resets on replug, so put
    * the number you settle on into config.h.
    *
    * ,-----------------------------------------------------------------------------------.
    * |      |Boot  |      |      |      |      |Whl < |Whl v |Whl ^ |Whl > |      |Del   |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      | TT-  | TT+  |TT prn|      |      |Mouse<|Mouse v|Mouse ^|Mouse>|     |      |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      |Slow  |Med   |Fast  |      |      | LMB  | RMB  | MMB  |      |      |      |
    * |------+------+------+------+------+------+------+------+------+------+------+------|
    * |      |      |      |      |      |     LMB     |      |      |      |      |      |
    * `-----------------------------------------------------------------------------------'
    */
    [3] = LAYOUT_ortho_4x12 (
        KC_TRNS, QK_BOOT, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, MS_WHLL, MS_WHLD, MS_WHLU, MS_WHLR, KC_TRNS, KC_DEL,
        KC_TRNS, DT_DOWN, DT_UP,   DT_PRNT, KC_TRNS, KC_TRNS, MS_LEFT, MS_DOWN, MS_UP,   MS_RGHT, KC_TRNS, KC_TRNS,
        KC_TRNS, MS_ACL0, MS_ACL1, MS_ACL2, KC_TRNS, KC_TRNS, MS_BTN1, MS_BTN2, MS_BTN3, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, MS_BTN1, MS_BTN1, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS
    )

};

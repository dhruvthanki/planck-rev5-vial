# The ATmega32U4 budget

The rev5 is an 8-bit AVR: **28672 bytes of usable flash** (32 KB minus the bootloader)
and **1 KB of EEPROM**. Vial is designed around boards with considerably more of both.
Two separate ceilings get hit, and they fail in different ways.

## EEPROM: the layer count

Dynamic keymaps live in EEPROM, because they must survive a power cycle:

```
layers x rows x cols x 2 bytes
```

At 8 layers that is `8 x 4 x 12 x 2 = 768` bytes of the 1024 available, before Vial's
tap-dance, combo, key-override and macro storage. The build fails at compile time:

```
error: static assertion failed: "Dynamic keymaps are configured to use more EEPROM
than is available."
```

**Fix:** `DYNAMIC_KEYMAP_LAYER_COUNT 4` in `keymap/config.h` → 384 bytes, leaving room
for everything else. Four layers matches the stock Planck arrangement
(base / lower / raise / adjust).

This is a hard limit. There is no external EEPROM on the rev5 to move it to.

## Flash: the feature set

With 4 layers the build links, then fails the size check:

```
* The firmware is too large! 30798/28672 (2126 bytes over)
```

`QMK_SETTINGS = no` is what buys the room back. It is the Vial feature that exposes
QMK's tuning knobs (tapping term, auto shift timing, one-shot behaviour) for runtime
editing, and carrying that table is expensive. Turning it off does not remove the
features — it means their timings are fixed at compile time and the Settings tab
disappears from the GUI.

Combined with `MAGIC`, `SPACE_CADET`, `GRAVE_ESC` and `MUSIC` off, plus audio,
backlight, RGB and console off:

```
* The firmware size is fine - 24716/28672 (86%, 3956 bytes free)
```

Tap dance, combos and key overrides all survive — verified by checking that
`process_tap_dance.o`, `process_combo.o` and `process_key_override.o` were compiled
into the build.

## If you need more room

In rough order of bytes-per-regret:

1. `EXTRAKEY_ENABLE = no` — loses media and volume keys
2. `NKRO_ENABLE = no` — 6KRO is fine for most people
3. `BOOTMAGIC_ENABLE = no` — you still have the physical reset button
4. `TAP_DANCE_ENABLE = no` / `COMBO_ENABLE = no` — these are the reason to run Vial,
   so cut them last

`LTO_ENABLE = yes` is already on and is doing a lot of work; do not turn it off.

## Checking your own build

```bash
./scripts/build.sh 2>&1 | tail -3
```

The size line is the answer. Anything under 28672 flashes.

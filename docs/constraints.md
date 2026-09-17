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

## Measured costs

Every number here came from an actual build, not an estimate:

| Feature | Flash | Verdict |
| --- | --- | --- |
| `GRAVE_ESC` | +64 | enabled |
| `DYNAMIC_TAPPING_TERM` | +270 | enabled |
| `MOUSEKEY` | +1482 | enabled |
| `AUTO_SHIFT` | +1494 | skipped, collides with tap-dance tuning |
| `QMK_SETTINGS` | +5236 | impossible -- 1280 bytes past the ceiling on its own |

With the three enabled features the firmware is **26530/28672 (92%, 2142 free)**.

`DYNAMIC_TAPPING_TERM` is the one to notice. It gives `DT_UP`, `DT_DOWN` and
`DT_PRNT`: tune hold-vs-tap by feel while typing, then print the value to paste
into `keymap/config.h`. That is most of what `QMK_SETTINGS` would have bought,
for 5% of the flash.

## Keycodes that silently do nothing

Disabling a feature does not remove keycodes that depend on it -- it removes the
*handler*. The keycode still exists, Vial still renders it with a normal-looking
label, and pressing the key does nothing whatsoever.

This bit twice on the first build:

* `SC_SENT` on the Enter key. Space Cadet right-shift/enter, inherited from the
  `planck/light` keymap, with `SPACE_CADET_ENABLE = no`. Vial displayed it as
  "RS Enter" and the key was dead. (The stock Planck default uses plain `KC_ENT`;
  the Space Cadet version was `planck/light`'s deviation.)
* `KC_NO` at matrix `(3,0)`, a real switch in `LAYOUT_ortho_4x12` mapped to
  nothing at all.

`scripts/dump-keymap.py` exists to catch exactly this. It reads the live keymap
off the keyboard over raw HID and flags both failure modes. Run it after any
firmware change that turns a feature off:

```bash
./scripts/dump-keymap.py          # audit
./scripts/dump-keymap.py --all    # audit plus the full keymap
```

The diagnostic split, when a key does nothing: if Vial's **matrix tester** lights
up but nothing is emitted, it is a keymap problem. If the matrix does not light
up either, it is hardware.

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

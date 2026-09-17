# Layout backups

`.vil` files exported from the Vial GUI (**File -> Save current layout**).

## Why these exist

`../keymap/keymap.c` is only the layout the firmware was *flashed* with. Everything
you change in the Vial GUI is written to the keyboard's EEPROM, and from that moment
the two disagree. The board is the only authority, and nothing backs it up.

EEPROM is erased by `EE_CLR`, by bootmagic, and by some firmware changes. Without an
export here, recovering means rebuilding the layout from memory.

## Restoring

Vial GUI -> **File -> Load saved layout**, pick the `.vil`. It writes straight to
EEPROM; no reflash needed.

## Checking what is actually on the board

```bash
../scripts/dump-keymap.py --all
```

Reads the live keymap over raw HID, so it reflects the keyboard rather than any file.

## Notes on this export

* **Pretty-printed on commit.** Vial writes `.vil` as a single minified line, which
  makes every git diff look like the whole file changed. Reformatting is safe --- it
  is plain JSON and Vial loads it back unchanged --- and it means a diff shows exactly
  which keys moved.
* **`uid` identifies the firmware.** The value here is the little-endian form of
  `VIAL_KEYBOARD_UID` in `../keymap/config.h`. If they ever disagree, the export
  belongs to a different build and Vial will refuse it.
* **`layout_options`** selects MIT (one 2u spacebar) vs grid (two 1u keys). This
  board is **MIT**, confirmed against the physical keyboard, so `0` is correct.
  `render-layout.py` reads this value and picks `LAYOUT_planck_1x2uC` accordingly;
  on the MIT build matrix `(3,6)` has no switch behind it, since the 2u spacebar is
  a single switch at `(3,5)`.

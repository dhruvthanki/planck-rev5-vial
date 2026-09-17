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
* **`layout_options`** selects MIT (one 2u spacebar) vs grid (two 1u keys). `0` is
  MIT. If your board is the grid build this must be `1`, or the GUI will show the
  wrong physical layout.

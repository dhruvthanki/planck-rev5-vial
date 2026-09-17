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

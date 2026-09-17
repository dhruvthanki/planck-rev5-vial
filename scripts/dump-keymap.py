#!/usr/bin/env python3
"""Read the live keymap out of the keyboard and audit it.

The firmware's compiled keymap.c is only a seed: once you edit anything in the
Vial GUI the real layout lives in the keyboard's EEPROM, and the two diverge
silently. This talks to the board directly over VIA's raw HID protocol, so it
reports what is actually on the keyboard right now.

It flags two failure modes that are invisible in the GUI:

  * KC_NO          -- a physical switch mapped to nothing
  * dead keycodes  -- keycodes whose feature is not compiled into the firmware.
                      These render normally in Vial (e.g. SC_SENT shows as
                      "RS Enter") but the firmware has no handler, so the key
                      does nothing at all when pressed.

Usage:
    ./scripts/dump-keymap.py            # audit, print problems
    ./scripts/dump-keymap.py --all      # also print the full keymap
"""
import os, sys, glob, struct, select, re

VID, PID = "03A8", "AE01"
GET_KEYCODE = 0x04          # VIA: id_dynamic_keymap_get_keycode
GET_LAYER_COUNT = 0x11      # VIA: id_dynamic_keymap_get_layer_count
ROWS, COLS = 4, 12
RAW_USAGE_PAGE = "0660ff0961"   # 0xFF60 / 0x61 -- the VIA/Vial raw HID interface

# Keycode prefixes whose features this firmware deliberately does not compile in.
# Keep in sync with keymap/rules.mk.
DISABLED = ("QK_SPACE_CADET", "QK_MAGIC", "QK_MUSIC", "QK_AUDIO", "QK_MIDI",
            "QK_BACKLIGHT", "QK_UNDERGLOW", "QK_AUTO_SHIFT",
            "RGB_", "BL_", "AU_", "MU_", "MI_", "AG_", "CG_")


def find_raw_hid():
    """Locate the raw HID node; it is not always the same hidrawN across replugs."""
    for path in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        dev = os.path.realpath(os.path.join(path, "device"))
        try:
            with open(os.path.join(dev, "report_descriptor"), "rb") as fh:
                if fh.read(5).hex() != RAW_USAGE_PAGE:
                    continue
            uevent = open(os.path.join(dev, "uevent")).read()
        except OSError:
            continue
        # HID_ID looks like 0003:000003A8:0000AE01, so match the padded form.
        if re.search(rf"HID_ID=[0-9A-F]+:0*{VID}:0*{PID}", uevent.upper()):
            return "/dev/" + os.path.basename(path)
    return None


def load_keycode_names():
    """Map keycode values to names using the vial-qmk source, if available."""
    for cand in (os.environ.get("VIAL_QMK"), os.path.expanduser("~/vial-qmk")):
        if not cand:
            continue
        header = os.path.join(cand, "quantum", "keycodes.h")
        if os.path.exists(header):
            src = open(header).read()
            out = {}
            for name, val in re.findall(r"(\w+)\s*=\s*(0x[0-9A-Fa-f]{4})", src):
                out.setdefault(int(val, 16), name)
            return out
    return {}


def main():
    dev = find_raw_hid()
    if not dev:
        sys.exit("No Vial raw HID interface found. Is the keyboard plugged in?")

    names = load_keycode_names()

    MODS = [(0x0100, "LCTL"), (0x0200, "LSFT"), (0x0400, "LALT"), (0x0800, "LGUI"),
            (0x1100, "RCTL"), (0x1200, "RSFT"), (0x1400, "RALT"), (0x1800, "RGUI")]

    def pretty(kc):
        if kc in names:
            return names[kc]
        if 0x5220 <= kc <= 0x522F:
            return f"MO({kc - 0x5220})"
        # Modified basic keycodes, e.g. LSFT(KC_3) for '#'.
        if 0x0100 <= kc < 0x2000:
            base, mod = kc & 0xFF, kc & 0x1F00
            for bit, label in MODS:
                if mod == bit and base in names:
                    return f"{label}({names[base]})"
        return f"0x{kc:04X}"

    try:
        fd = os.open(dev, os.O_RDWR | os.O_NONBLOCK)
    except PermissionError:
        sys.exit(f"Permission denied on {dev}. Install the udev rules (scripts/setup.sh) "
                 "and replug the keyboard.")

    def get(layer, row, col):
        os.write(fd, bytes([0x00, GET_KEYCODE, layer, row, col]) + b"\x00" * 27)
        ready, _, _ = select.select([fd], [], [], 2.0)
        if not ready:
            return None
        return struct.unpack(">H", os.read(fd, 32)[4:6])[0]

    # Ask the firmware how many layers it actually has. Reading past that count
    # returns zeros rather than failing, which looks like a keymap full of dead keys.
    os.write(fd, bytes([0x00, GET_LAYER_COUNT]) + b"\x00" * 30)
    ready, _, _ = select.select([fd], [], [], 2.0)
    if not ready:
        os.close(fd)
        sys.exit("Keyboard did not respond to the layer-count query.")
    layer_count = os.read(fd, 32)[1]

    layers, problems = [], []
    for layer in range(layer_count):
        layers.append([[get(layer, r, c) for c in range(COLS)] for r in range(ROWS)])
    os.close(fd)

    for li, layer in enumerate(layers):
        for r, row in enumerate(layer):
            for c, kc in enumerate(row):
                name = pretty(kc)
                if kc == 0x0000:
                    problems.append((li, r, c, "KC_NO", "dead key -- switch mapped to nothing"))
                elif any(name.startswith(p) for p in DISABLED):
                    problems.append((li, r, c, name, "feature not compiled in -- key does nothing"))

    if "--all" in sys.argv:
        for li, layer in enumerate(layers):
            print(f"\n--- layer {li} ---")
            for row in layer:
                print("  " + " ".join(f"{pretty(kc):<12}" for kc in row))
        print()

    print(f"Read {len(layers)} layers from {dev}\n")
    if not problems:
        print("No problems found.")
        return
    print("Problems:")
    for li, r, c, name, why in problems:
        print(f"  L{li} ({r:>2},{c:>2})  {name:<28} {why}")
    sys.exit(1)


if __name__ == "__main__":
    main()

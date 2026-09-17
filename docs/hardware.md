# Identifying the board from a running system

Useful if you buy a Planck second hand and do not know what you have.

## Which revision?

```bash
lsusb | grep -i olkb
# Bus 007 Device 006: ID 03a8:ae01 OLKB Planck

# Or with the device version, which encodes the revision:
for f in /sys/bus/usb/devices/*/product; do
    grep -q Planck "$f" 2>/dev/null || continue
    d=$(dirname "$f")
    for k in idVendor idProduct bcdDevice manufacturer product; do
        printf "%-12s %s\n" "$k" "$(cat "$d/$k")"
    done
done
# idVendor  03a8   idProduct  ae01   bcdDevice  0005
```

`bcdDevice 0005` is `device_version 0.0.5` from `keyboards/planck/rev5/keyboard.json`.
Each revision uses a different PID, so this identifies the board unambiguously.

## Is the existing firmware VIA/Vial capable?

Check the raw HID usage page on the keyboard's interfaces:

```bash
for p in /sys/bus/usb/devices/*:1.*/0003:03A8:AE01.*/report_descriptor; do
    echo "== $p"; xxd -l 32 "$p"
done
```

- `06 60 ff  09 61` — usage page `0xFF60`, usage `0x61` → **VIA/Vial raw HID**
- `06 31 ff  09 74` — usage page `0xFF31`, usage `0x74` → **QMK debug console**, not VIA

Stock firmware on a used board often has only the console interface, which means the
keymap is compiled in and **cannot be read back from the host**. There is no host-side
protocol to dump it. If you did not build the firmware, the keymap is not recoverable —
reflash and start over.

## What does the current keymap do?

Without VIA/Vial you can still map it empirically, which is worth doing before you
overwrite a layout you might want to keep:

```bash
sudo evtest "$(ls /dev/input/by-id/*OLKB_Planck*-event-kbd | head -1)"
```

Note the by-id path changes once Vial firmware is flashed: the node gains the
Vial serial, e.g. `usb-OLKB_Planck_vial:f64c2b3c-event-kbd`. The glob above
handles either. The board also presents two keyboard nodes -- boot protocol and
NKRO -- plus a Consumer Control node for media keys, so if a key seems missing,
check the others.

Press each key and read the keycodes. Hold a layer key and sweep again for that layer.
This reveals the base layer and any layer you can find by holding things; it will not
reveal tap dance or combo logic.

## Is audio or backlight populated?

Neither is reported over USB — the `leds` handler on the evdev node is just the standard
Caps/Num/Scroll Lock indicator protocol that every keyboard has.

- **Audio**: replug the board. A startup jingle means a piezo is installed and
  `AUDIO_ENABLE` is on. Silence means no piezo, `AUDIO_ENABLE = no`, or audio muted
  in EEPROM via `AU_OFF` (QMK remembers that across reboots).
- **Backlight / underglow**: look at the board in a dark room. The rev5 PCB has
  footprints for in-switch LEDs (pin B7) and a WS2812 underglow strip, but neither is
  populated by default — both require soldering.

Firmware can have `BACKLIGHT_ENABLE` compiled in with no LEDs installed, wasting flash
for nothing. On a 32U4 that matters.

## Entering the bootloader

On a board whose keymap you do not know, do not hunt for a `QK_BOOT` key. Press the
**physical reset button on the underside of the PCB**; the rev5 uses the `qmk-dfu`
bootloader, so `dfu-programmer` picks it up from there.

## Reading the live keymap

Once you edit anything in Vial, the real layout lives in the keyboard's EEPROM and
`keymap.c` is only the seed it was flashed with. To see what is actually on the
board:

```bash
./scripts/dump-keymap.py --all
```

This speaks VIA's raw HID protocol directly (`id_dynamic_keymap_get_keycode`),
finds the `0xFF60` interface itself, and asks the firmware for its layer count
rather than assuming -- reading past the configured count returns zeros, which
looks convincingly like a keymap full of dead keys.

Keymap *writes* are not gated behind the Vial unlock combo; only matrix-state
reads are (`via.c:253`). Reads of the keymap work whether the board is locked or not.

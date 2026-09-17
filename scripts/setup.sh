#!/usr/bin/env bash
# Sets up a build environment for this keymap:
#   1. installs the AVR toolchain and DFU flashing tools (Debian/Ubuntu)
#   2. installs the qmk CLI in an isolated tool environment
#   3. clones vial-qmk and initialises the LUFA submodule
#   4. symlinks this repo's keymap/ into the vial-qmk tree
#
# Safe to re-run; every step is idempotent.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VIAL_QMK="${VIAL_QMK:-$HOME/vial-qmk}"
KEYMAP_DEST="$VIAL_QMK/keyboards/planck/rev5/keymaps/vial"

echo "==> Repo:     $REPO_DIR"
echo "==> vial-qmk: $VIAL_QMK"

# --- 1. system packages -------------------------------------------------------
missing=()
for c in avr-gcc dfu-programmer dfu-util git make; do
    command -v "$c" >/dev/null 2>&1 || missing+=("$c")
done
if [ ${#missing[@]} -gt 0 ]; then
    echo "==> Installing AVR toolchain (missing: ${missing[*]})"
    sudo apt-get update
    sudo apt-get install -y gcc-avr avr-libc binutils-avr dfu-programmer dfu-util git make
else
    echo "==> AVR toolchain already present"
fi

# --- 2. qmk CLI ---------------------------------------------------------------
# Installed as an isolated tool so it cannot disturb a managed Python install
# (conda / uv / PEP 668 "externally managed" environments).
if ! command -v qmk >/dev/null 2>&1; then
    echo "==> Installing qmk CLI"
    if command -v uv >/dev/null 2>&1; then
        uv tool install qmk
    elif command -v pipx >/dev/null 2>&1; then
        pipx install qmk
    else
        python3 -m pip install --user qmk
    fi
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "==> qmk CLI already present ($(command -v qmk))"
fi

# --- 3. vial-qmk --------------------------------------------------------------
if [ ! -d "$VIAL_QMK/.git" ]; then
    echo "==> Cloning vial-qmk"
    git clone --depth 1 -b vial https://github.com/vial-kb/vial-qmk.git "$VIAL_QMK"
else
    echo "==> vial-qmk already cloned"
fi

# LUFA is the USB stack for AVR targets; the build fails without it.
if [ ! -f "$VIAL_QMK/lib/lufa/LUFA/Version.h" ]; then
    echo "==> Initialising LUFA submodule"
    git -C "$VIAL_QMK" submodule update --init --recursive --depth 1 lib/lufa
fi

# --- 4. link the keymap -------------------------------------------------------
# A symlink keeps this repo the single source of truth: edit here, build there.
if [ -L "$KEYMAP_DEST" ]; then
    echo "==> Keymap already linked"
elif [ -e "$KEYMAP_DEST" ]; then
    echo "!! $KEYMAP_DEST exists and is not a symlink; move it aside first." >&2
    exit 1
else
    mkdir -p "$(dirname "$KEYMAP_DEST")"
    ln -s "$REPO_DIR/keymap" "$KEYMAP_DEST"
    echo "==> Linked $KEYMAP_DEST -> $REPO_DIR/keymap"
fi

# --- 5. udev rules ------------------------------------------------------------
# Needed so flashing and the Vial GUI work without root.
if [ ! -f /etc/udev/rules.d/50-qmk.rules ]; then
    echo "==> Installing udev rules"
    sudo install -m 644 "$VIAL_QMK/util/udev/50-qmk.rules" /etc/udev/rules.d/50-qmk.rules
    printf '# Vial GUI: raw HID access to OLKB devices\nKERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="03a8", MODE="0660", TAG+="uaccess"\n' \
        | sudo tee /etc/udev/rules.d/99-vial.rules >/dev/null
    sudo udevadm control --reload-rules && sudo udevadm trigger
    echo "   (takes effect when the keyboard is next replugged)"
fi

echo
echo "Setup complete. Next: ./scripts/build.sh"

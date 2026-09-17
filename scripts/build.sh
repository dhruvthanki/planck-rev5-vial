#!/usr/bin/env bash
# Builds the firmware. Output: $VIAL_QMK/planck_rev5_vial.hex
set -euo pipefail

VIAL_QMK="${VIAL_QMK:-$HOME/vial-qmk}"
export PATH="$HOME/.local/bin:$PATH"

[ -d "$VIAL_QMK" ] || { echo "vial-qmk not found at $VIAL_QMK -- run ./scripts/setup.sh" >&2; exit 1; }

cd "$VIAL_QMK"
make planck/rev5:vial "$@"

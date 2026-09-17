#!/usr/bin/env bash
# Builds and flashes. The board must be in bootloader (DFU) mode:
#   press the physical reset button on the underside of the PCB.
# The make target polls for the DFU device, so you can start this first
# and press reset afterwards.
set -euo pipefail

VIAL_QMK="${VIAL_QMK:-$HOME/vial-qmk}"
export PATH="$HOME/.local/bin:$PATH"

[ -d "$VIAL_QMK" ] || { echo "vial-qmk not found at $VIAL_QMK -- run ./scripts/setup.sh" >&2; exit 1; }

echo "Waiting for the Planck in DFU mode -- press the reset button on the back of the PCB."
cd "$VIAL_QMK"
make planck/rev5:vial:flash "$@"

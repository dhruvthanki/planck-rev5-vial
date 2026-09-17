#!/usr/bin/env python3
"""Render a Vial .vil export to SVG diagrams via keymap-drawer.

keymap-drawer parses QMK json, not .vil, so this converts between them. A .vil
stores layers as [layer][row][col] arrays of keycode names; QMK json wants one
flat list per layer in LAYOUT order, which for LAYOUT_ortho_4x12 is row-major.

Usage:
    ./scripts/render-layout.py [layouts/planck-rev5.vil] [-o layouts/]

Requires: uv tool install keymap-drawer
"""
import json, subprocess, sys, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LAYER_NAMES = ["Base", "Lower", "Raise", "Adjust"]

# The .vil's layout_options selects the physical build of the board.
# 0 = MIT: one 2u spacebar, matrix (3,6) has no switch behind it.
# 1 = grid: two 1u keys.
LAYOUT_FOR_OPTION = {0: "LAYOUT_planck_1x2uC", 1: "LAYOUT_ortho_4x12"}
INFO_JSON = "layouts/planck-rev5.info.json"

# Vial exports QMK's long-form aliases. keymap-drawer recognises the modern short
# names and renders them as proper glyphs, so normalise on the way through.
ALIASES = {
    "KC_BSPACE": "KC_BSPC", "KC_SCOLON": "KC_SCLN", "KC_LSHIFT": "KC_LSFT",
    "KC_LCTRL": "KC_LCTL", "KC_ENTER": "KC_ENT", "KC_ESCAPE": "KC_ESC",
    "KC_DELETE": "KC_DEL", "KC_QUOTE": "KC_QUOT", "KC_COMMA": "KC_COMM",
    "KC_SLASH": "KC_SLSH", "KC_GRAVE": "KC_GRV", "KC_MINUS": "KC_MINS",
    "KC_EQUAL": "KC_EQL", "KC_LBRACKET": "KC_LBRC", "KC_RBRACKET": "KC_RBRC",
    "KC_BSLASH": "KC_BSLS", "KC_PGDOWN": "KC_PGDN",
    "KC_NONUS_BSLASH": "KC_NUBS", "KC_NONUS_HASH": "KC_NUHS",
    "KC_MEDIA_NEXT_TRACK": "KC_MNXT", "KC_MEDIA_PLAY_PAUSE": "KC_MPLY",
    "KC_AUDIO_VOL_DOWN": "KC_VOLD", "KC_AUDIO_VOL_UP": "KC_VOLU",
    # Vial has no symbolic name for the dynamic tapping term keycodes, so it
    # exports them as raw hex. Give them readable labels in the diagram.
    "0x7C70": "DT_PRNT", "0x7C71": "DT_UP", "0x7C72": "DT_DOWN",
    # Mouse keys: Vial exports the old KC_ spellings. Give them labels that read
    # as a diagram rather than as keycodes.
    "KC_MS_L": "Mouse ←", "KC_MS_D": "Mouse ↓", "KC_MS_U": "Mouse ↑", "KC_MS_R": "Mouse →",
    "KC_WH_L": "Whl ←", "KC_WH_D": "Whl ↓", "KC_WH_U": "Whl ↑", "KC_WH_R": "Whl →",
    "KC_BTN1": "LMB", "KC_BTN2": "RMB", "KC_BTN3": "MMB",
    "KC_ACL0": "Slow", "KC_ACL1": "Med", "KC_ACL2": "Fast",
    # LM(1, MOD_LGUI): holds Super and switches to Lower, where HJKL are arrows.
    # Vial has no symbolic name for layer-mod keycodes either.
    "0x5028": "Super+Nav",
}


def normalise(kc: str) -> str:
    """Rewrite long-form aliases, including inside wrappers like LSFT(...)."""
    if kc.lower().startswith("0x"):
        kc = "0x" + kc[2:].upper()
    for old, new in ALIASES.items():
        if kc == old:
            return new
        kc = kc.replace(f"({old})", f"({new})")
    return kc


def vil_to_qmk(vil: dict, layout_name: str, order: list) -> dict:
    """Convert to QMK json, emitting keys in the physical layout's own order.

    Ordering by the layout definition rather than assuming row-major matters for
    the MIT build, where matrix (3,6) is absent because the 2u spacebar occupies
    a single switch at (3,5).
    """
    layers = []
    for layer in vil["layout"]:
        layers.append([normalise(layer[r][c]) for r, c in order])
    return {
        "version": 1,
        "keyboard": "planck/rev5",
        "keymap": "vial",
        "layout": layout_name,
        "layers": layers,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    src = Path(args[0]) if args else REPO / "layouts" / "planck-rev5.vil"
    out_dir = REPO / "layouts"

    if not shutil.which("keymap"):
        sys.exit("keymap-drawer not found. Install with: uv tool install keymap-drawer")

    vil = json.loads(src.read_text())

    # Vial always writes .vil as one minified line, which makes every diff look
    # like the whole file changed. Reformat in place; it is plain JSON and Vial
    # loads it back unchanged.
    pretty = json.dumps(vil, indent=2) + "\n"
    if src.read_text() != pretty:
        src.write_text(pretty)
        print(f"reformatted {src.name} for readable diffs")

    option = vil.get("layout_options", 0)
    layout_name = LAYOUT_FOR_OPTION.get(option)
    if layout_name is None:
        sys.exit(f"Unknown layout_options value {option!r} in {src}")
    info = json.loads((REPO / INFO_JSON).read_text())
    order = [tuple(k["matrix"]) for k in info["layouts"][layout_name]["layout"]]
    print(f"layout_options={option} -> {layout_name} ({len(order)} keys)")

    qmk = vil_to_qmk(vil, layout_name, order)
    names = LAYER_NAMES[: len(qmk["layers"])]

    qmk_json = out_dir / (src.stem + ".qmk.json")
    qmk_json.write_text(json.dumps(qmk, indent=2) + "\n")

    yaml_path = out_dir / (src.stem + ".yaml")
    parsed = subprocess.run(
        ["keymap", "parse", "-c", "12", "-q", str(qmk_json), "--layer-names", *names],
        capture_output=True, text=True,
    )
    if parsed.returncode:
        sys.exit("keymap parse failed:\n" + parsed.stderr)
    yaml_path.write_text(parsed.stdout)

    svg_path = out_dir / (src.stem + ".svg")
    drawn = subprocess.run(
        ["keymap", "draw", str(yaml_path),
         "-j", str(REPO / INFO_JSON), "-l", layout_name],
        capture_output=True, text=True,
    )
    if drawn.returncode:
        sys.exit("keymap draw failed:\n" + drawn.stderr)
    svg_path.write_text(drawn.stdout)

    print(f"wrote {yaml_path.relative_to(REPO)}")
    print(f"wrote {svg_path.relative_to(REPO)}  ({len(drawn.stdout)} bytes)")


if __name__ == "__main__":
    main()

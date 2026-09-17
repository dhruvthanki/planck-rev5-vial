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
}


def normalise(kc: str) -> str:
    """Rewrite long-form aliases, including inside wrappers like LSFT(...)."""
    for old, new in ALIASES.items():
        if kc == old:
            return new
        kc = kc.replace(f"({old})", f"({new})")
    return kc


def vil_to_qmk(vil: dict) -> dict:
    """Flatten [layer][row][col] into QMK json's per-layer flat lists."""
    return {
        "version": 1,
        "keyboard": "planck/rev5",
        "keymap": "vial",
        "layout": "LAYOUT_ortho_4x12",
        "layers": [[normalise(kc) for row in layer for kc in row]
                   for layer in vil["layout"]],
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    src = Path(args[0]) if args else REPO / "layouts" / "planck-rev5.vil"
    out_dir = REPO / "layouts"

    if not shutil.which("keymap"):
        sys.exit("keymap-drawer not found. Install with: uv tool install keymap-drawer")

    vil = json.loads(src.read_text())
    qmk = vil_to_qmk(vil)
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
    drawn = subprocess.run(["keymap", "draw", str(yaml_path)],
                           capture_output=True, text=True)
    if drawn.returncode:
        sys.exit("keymap draw failed:\n" + drawn.stderr)
    svg_path.write_text(drawn.stdout)

    print(f"wrote {yaml_path.relative_to(REPO)}")
    print(f"wrote {svg_path.relative_to(REPO)}  ({len(drawn.stdout)} bytes)")


if __name__ == "__main__":
    main()

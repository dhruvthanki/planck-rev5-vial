VIA_ENABLE = yes
VIAL_ENABLE = yes
LTO_ENABLE = yes

# Not enough USB endpoints alongside raw HID
CONSOLE_ENABLE = no

# No piezo / LEDs populated on this board -- reclaim the flash
AUDIO_ENABLE = no
BACKLIGHT_ENABLE = no
RGBLIGHT_ENABLE = no

# 32U4 flash budget: drop runtime-tweakable QMK settings and unused quantum features
QMK_SETTINGS = no
MAGIC_ENABLE = no
SPACE_CADET_ENABLE = no
MUSIC_ENABLE = no

# Enabled deliberately; measured costs against the 28672-byte ceiling:
#   MOUSEKEY             +1482   cursor layer
#   DYNAMIC_TAPPING_TERM  +270   DT_UP/DT_DOWN/DT_PRNT, runtime hold-vs-tap tuning
#   GRAVE_ESC              +64   shifted Esc produces a backtick
MOUSEKEY_ENABLE = yes
DYNAMIC_TAPPING_TERM_ENABLE = yes
GRAVE_ESC_ENABLE = yes

# Unused (no QK_REP/QK_AREP bound, all alt_repeat_key slots empty) and worth
# 1368 bytes, which is what the home row mod options cost.
REPEAT_KEY_ENABLE = no

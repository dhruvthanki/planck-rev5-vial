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
GRAVE_ESC_ENABLE = no
MUSIC_ENABLE = no

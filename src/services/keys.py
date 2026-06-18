"""Keyboard special key definitions with platform-specific support."""

from __future__ import annotations

import sys


# ============================================================================
# Common Special Keys (All Platforms)
# ============================================================================

SPECIAL_KEYS_COMMON = frozenset(
    {
        "esc", "enter", "space", "backspace", "tab", "caps_lock",
        "shift", "shift_l", "shift_r",
        "ctrl", "ctrl_l", "ctrl_r",
        "alt", "alt_l", "alt_r",
        "meta", "meta_l", "meta_r",
        "fn",
        "up", "down", "left", "right",
        "insert", "delete", "home", "end", "page_up", "page_down",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "`", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "/",
        "num_lock", "numpad_0", "numpad_1", "numpad_2", "numpad_3", "numpad_4", "numpad_5", "numpad_6", "numpad_7", "numpad_8", "numpad_9",
        "numpad_add", "numpad_subtract", "numpad_multiply", "numpad_divide", "numpad_decimal", "numpad_enter",
        "audio_volume_mute", "audio_volume_down", "audio_volume_up",
        "media_play_pause", "media_track_next", "media_track_previous",
    }
)


# ============================================================================
# Numpad Normalization
# ============================================================================

NUMPAD_NAME_ALIASES = {
    **{f"num_{digit}": str(digit) for digit in range(10)},
    **{f"numpad_{digit}": str(digit) for digit in range(10)},
    "decimal": ".",
    "num_decimal": ".",
    "numpad_decimal": ".",
}

NUMPAD_VK_CODES_WINDOWS = {
    96: "0",
    97: "1",
    98: "2",
    99: "3",
    100: "4",
    101: "5",
    102: "6",
    103: "7",
    104: "8",
    105: "9",
    110: ".",
}

NUMPAD_VK_CODES_MAC = {
    65: ".",
    82: "0",
    83: "1",
    84: "2",
    85: "3",
    86: "4",
    87: "5",
    88: "6",
    89: "7",
    91: "8",
    92: "9",
}

NUMPAD_VK_CODES_BY_PLATFORM = {
    "darwin": NUMPAD_VK_CODES_MAC,
    "win32": NUMPAD_VK_CODES_WINDOWS,
}


# ============================================================================
# Windows-Specific Special Keys
# ============================================================================

SPECIAL_KEYS_WINDOWS = frozenset(
    {
        "context_menu",
        "print_screen",
        "scroll_lock",
        "pause",
        "hangul",
        "hanja",
    }
)


# ============================================================================
# macOS-Specific Special Keys
# ============================================================================

SPECIAL_KEYS_MAC = frozenset(
    {
        "clear",
        "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20",
        "eject",
        "lang1",
        "lang2",
    }
)


# ============================================================================
# Platform-Specific Key Set Selection
# ============================================================================

if sys.platform == "darwin":  # macOS
    SPECIAL_KEYS = SPECIAL_KEYS_COMMON | SPECIAL_KEYS_MAC
elif sys.platform == "win32":  # Windows
    SPECIAL_KEYS = SPECIAL_KEYS_COMMON | SPECIAL_KEYS_WINDOWS
else:  # Linux and other platforms
    SPECIAL_KEYS = SPECIAL_KEYS_COMMON


__all__ = [
    "SPECIAL_KEYS_COMMON",
    "SPECIAL_KEYS_WINDOWS",
    "SPECIAL_KEYS_MAC",
    "SPECIAL_KEYS",
    "NUMPAD_NAME_ALIASES",
    "NUMPAD_VK_CODES_WINDOWS",
    "NUMPAD_VK_CODES_MAC",
    "NUMPAD_VK_CODES_BY_PLATFORM",
]

"""Keyboard event to image mapping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

# Timing constants (milliseconds)
SPECIAL_CHAR_FLASH_MS = 500
KEY_HOLD_MS = 700
DEFAULT_FLASH_MS = 200

# Special keys mapping
SPECIAL_KEYS = {
    "?": "special_punct",
    "!": "special_punct",
    ".": "comma",
    "enter": "enter",
    "esc": "esc",
    "backspace": "backspace",
}


@dataclass(frozen=True)
class SpecialCharRule:
    image_name: str
    flash_ms: int

@dataclass(frozen=True)
class KeyboardImageNames:
    default: str
    stroke: str
    special_punct: str
    comma: str
    enter: str
    esc: str
    backspace: str

@dataclass(frozen=True)
class KeyboardMapper:
    image_names: KeyboardImageNames
    special_char_rules: Mapping[str, SpecialCharRule]
    key_hold_ms_rules: Mapping[str, int]
    key_press_count_limit: int
    default_flash_ms: int

def create_keyboard_mapper(
    special_flash_ms: int = SPECIAL_CHAR_FLASH_MS,
    hold_ms: int = KEY_HOLD_MS,
    default_flash_ms: int = DEFAULT_FLASH_MS,
) -> KeyboardMapper:
    """Create default keyboard mapper with standard configuration.
    
    Args:
        special_flash_ms: Flash duration for special characters (ms)
        hold_ms: Hold duration for blocking repeated presses (ms)
        default_flash_ms: Default flash duration for regular keys (ms)
    """
    image_names = KeyboardImageNames(
        default="k_default",
        stroke="k_stroke",
        special_punct="k_special_punct",
        comma="k_comma",
        enter="k_enter",
        esc="k_esc",
        backspace="k_backspace",
    )
    
    special_char_rules = {}
    key_hold_ms_rules = {}
    
    for key, image_attr in SPECIAL_KEYS.items():
        image_name = getattr(image_names, image_attr)
        special_char_rules[key] = SpecialCharRule(image_name=image_name, flash_ms=special_flash_ms)
        key_hold_ms_rules[key] = hold_ms
    
    return KeyboardMapper(
        image_names=image_names,
        special_char_rules=special_char_rules,
        key_hold_ms_rules=key_hold_ms_rules,
        key_press_count_limit=1,
        default_flash_ms=default_flash_ms,
    )

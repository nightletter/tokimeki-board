from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from src.core.models import KeyHoldState, KeyToggleState
from core.events import ScrollDirection, ScrollEvent
from mappers.keyboard_mapper import KeyboardMapper
from mappers.scroll_mapper import ScrollMapper


class ImageCommandType(str, Enum):
    SHOW_NAMED = "show_named"
    SHOW_CYCLE_CURRENT = "show_cycle_current"
    SHOW_CYCLE_NEXT = "show_cycle_next"


@dataclass(frozen=True)
class ImageCommand:
    command_type: ImageCommandType
    name: str | None = None


@dataclass(frozen=True)
class KeyImageResult:
    command: ImageCommand | None
    flash_ms: int


class ImageController:
    def __init__(
        self,
        keyboard_mapper: KeyboardMapper,
        scroll_mapper: ScrollMapper,
        key_toggle_mode: bool,
    ):
        self._keyboard_mapper = keyboard_mapper
        self._scroll_mapper = scroll_mapper
        self._key_toggle_mode = key_toggle_mode
        self._toggle_state = KeyToggleState()
        self._hold_state = KeyHoldState()

    @property
    def key_toggle_mode(self) -> bool:
        return self._key_toggle_mode

    def initial_command(self) -> ImageCommand:
        if self._key_toggle_mode:
            return ImageCommand(ImageCommandType.SHOW_NAMED, self._keyboard_mapper.image_names.default)
        return ImageCommand(ImageCommandType.SHOW_CYCLE_CURRENT)

    def on_key_pressed(self, value: str, now: float | None = None) -> KeyImageResult | None:
        if not self._key_toggle_mode:
            return None
        timestamp = time.monotonic() if now is None else now
        if self._is_hold_active(value, timestamp):
            return None
        hold_ms = self._keyboard_mapper.key_hold_ms_rules.get(value, 0)
        if hold_ms > 0:
            self._start_hold(value, timestamp, hold_ms)
        command = self._next_image_for_key(value)
        flash_ms = self._flash_ms_for_key(value)
        if hold_ms > 0:
            flash_ms = max(flash_ms, hold_ms)
        return KeyImageResult(command=command, flash_ms=flash_ms)

    def on_key_idle(self) -> ImageCommand:
        self._clear_hold()
        self._toggle_state.stroke_visible = False
        self._toggle_state.key_press_count = 0
        return ImageCommand(ImageCommandType.SHOW_NAMED, self._keyboard_mapper.image_names.default)

    def on_scroll_event(self, event: ScrollEvent) -> ImageCommand | None:
        _ = event.phase
        scroll_names = self._scroll_mapper.image_names
        if event.direction == ScrollDirection.UP:
            return ImageCommand(ImageCommandType.SHOW_NAMED, scroll_names.up)
        if event.direction == ScrollDirection.DOWN:
            return ImageCommand(ImageCommandType.SHOW_NAMED, scroll_names.down)
        return None

    def on_scroll_idle(self) -> ImageCommand:
        if self._key_toggle_mode:
            return ImageCommand(ImageCommandType.SHOW_NAMED, self._keyboard_mapper.image_names.default)
        return ImageCommand(ImageCommandType.SHOW_CYCLE_CURRENT)

    def on_cycle_tick(self) -> ImageCommand | None:
        if self._key_toggle_mode:
            return None
        return ImageCommand(ImageCommandType.SHOW_CYCLE_NEXT)

    def _flash_ms_for_key(self, value: str) -> int:
        rule = self._keyboard_mapper.special_char_rules.get(value)
        if rule is None:
            return self._keyboard_mapper.default_flash_ms
        return rule.flash_ms

    def _next_image_for_key(self, value: str) -> ImageCommand | None:
        rule = self._keyboard_mapper.special_char_rules.get(value)
        if rule is not None:
            self._toggle_state.key_press_count = 0
            return ImageCommand(ImageCommandType.SHOW_NAMED, rule.image_name)
        self._toggle_state.key_press_count += 1
        if self._toggle_state.key_press_count < self._keyboard_mapper.key_press_count_limit:
            return None
        self._toggle_state.key_press_count = 0
        kb_names = self._keyboard_mapper.image_names
        if self._toggle_state.stroke_visible:
            self._toggle_state.stroke_visible = False
            return ImageCommand(ImageCommandType.SHOW_NAMED, kb_names.default)
        self._toggle_state.stroke_visible = True
        return ImageCommand(ImageCommandType.SHOW_NAMED, kb_names.stroke)

    def _is_hold_active(self, value: str, now: float) -> bool:
        if self._hold_state.hold_until <= 0.0:
            return False
        if now >= self._hold_state.hold_until:
            self._clear_hold()
            return False
        return value != self._hold_state.hold_key

    def _start_hold(self, value: str, now: float, hold_ms: int) -> None:
        self._hold_state.hold_key = value
        self._hold_state.hold_until = now + (hold_ms / 1000.0)

    def _clear_hold(self) -> None:
        self._hold_state.hold_key = None
        self._hold_state.hold_until = 0.0

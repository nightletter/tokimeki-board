from __future__ import annotations

from collections.abc import Callable
from threading import Lock, Timer
from typing import Any

from core.events import KeyEvent, ScrollDirection, ScrollEvent, ScrollPhase
from src.services.keys import (
    NUMPAD_NAME_ALIASES,
    NUMPAD_VK_CODES_BY_PLATFORM,
    SPECIAL_KEYS,
)


# ============================================================================
# Keyboard Input
# ============================================================================

def import_keyboard_backend():
    try:
        from pynput import keyboard
    except ImportError:
        return None
    return keyboard


def extract_typed_key(key: Any) -> str | None:
    value = getattr(key, "char", None)

    if isinstance(value, str) and value:
        if value == " ":
            return "space"
        return value

    name = getattr(key, "name", None)
    if isinstance(name, str):
        normalized_name = NUMPAD_NAME_ALIASES.get(name)
        if normalized_name is not None:
            return normalized_name

        if name in SPECIAL_KEYS:
            return name

    vk = getattr(key, "vk", None)
    if isinstance(vk, int):
        for platform_vk_codes in NUMPAD_VK_CODES_BY_PLATFORM.values():
            normalized_vk = platform_vk_codes.get(vk)
            if normalized_vk is not None:
                return normalized_vk

    # Fall back to special key name
    return None


def create_keypress_listener(
    keyboard_backend: Any,
    on_event: Callable[[KeyEvent], None],
):
    def on_press(key: Any):
        value = extract_typed_key(key)
        if value is None:
            return
        on_event(KeyEvent(value=value))

    listener = keyboard_backend.Listener(on_press=on_press)
    listener.daemon = True
    return listener


# ============================================================================
# Mouse/Scroll Input
# ============================================================================


def import_mouse_backend():
    try:
        from pynput import mouse
    except ImportError:
        return None
    return mouse


def extract_scroll_direction(dy: int | float) -> ScrollDirection | None:
    if dy > 0:
        return ScrollDirection.UP
    if dy < 0:
        return ScrollDirection.DOWN
    return None


def create_scroll_listener(
    mouse_backend: Any,
    on_event: Callable[[ScrollEvent], None],
    idle_ms: int,
):
    lock = Lock()
    active_direction: ScrollDirection | None = None
    idle_timer: Timer | None = None

    def _cancel_idle_timer():
        nonlocal idle_timer
        if idle_timer is None:
            return
        idle_timer.cancel()
        idle_timer = None

    def _emit_scroll_end(expected_direction: ScrollDirection):
        nonlocal active_direction, idle_timer
        should_emit = False
        with lock:
            if active_direction == expected_direction:
                active_direction = None
                idle_timer = None
                should_emit = True
        if should_emit:
            on_event(ScrollEvent(phase=ScrollPhase.END, direction=expected_direction))

    def _restart_idle_timer(direction: ScrollDirection):
        nonlocal idle_timer
        _cancel_idle_timer()
        idle_timer = Timer(idle_ms / 1000.0, _emit_scroll_end, args=(direction,))
        idle_timer.daemon = True
        idle_timer.start()

    def on_scroll(_x: int, _y: int, _dx: int, dy: int):
        nonlocal active_direction
        direction = extract_scroll_direction(dy)
        if direction is None:
            return
        emit_start = False
        emit_end: ScrollDirection | None = None
        with lock:
            if active_direction is None:
                active_direction = direction
                emit_start = True
            elif active_direction != direction:
                emit_end = active_direction
                active_direction = direction
                emit_start = True
            _restart_idle_timer(direction)
        if emit_end is not None:
            on_event(ScrollEvent(phase=ScrollPhase.END, direction=emit_end))
        if emit_start:
            on_event(ScrollEvent(phase=ScrollPhase.START, direction=direction))

    listener = mouse_backend.Listener(on_scroll=on_scroll)
    listener_stop = getattr(listener, "stop", None)

    def stop():
        _cancel_idle_timer()
        if callable(listener_stop):
            return listener_stop()
        return None

    listener.stop = stop
    listener.daemon = True
    return listener

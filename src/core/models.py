from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CursorState:
    fx: float
    fy: float
    last_position: tuple[int, int] | None = None


@dataclass
class KeyToggleState:
    stroke_visible: bool = False
    key_press_count: int = 0


@dataclass
class KeyHoldState:
    hold_until: float = 0.0
    hold_key: str | None = None

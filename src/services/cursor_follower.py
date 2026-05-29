from __future__ import annotations

from core.config import MotionConfig
from src.core.models import CursorState


class CursorFollower:
    def __init__(self, motion: MotionConfig, initial_pos: tuple[int, int]):
        self._motion = motion
        self._state = CursorState(
            fx=float(initial_pos[0] + motion.offset_x),
            fy=float(initial_pos[1] + motion.offset_y),
        )

    def update(self, cursor_pos: tuple[int, int]) -> tuple[int, int] | None:
        tx = float(cursor_pos[0] + self._motion.offset_x)
        ty = float(cursor_pos[1] + self._motion.offset_y)

        dx = tx - self._state.fx
        dy = ty - self._state.fy

        if abs(dx) < self._motion.snap_threshold and abs(dy) < self._motion.snap_threshold:
            self._state.fx = tx
            self._state.fy = ty
        else:
            alpha = 1.0 - self._motion.smooth
            self._state.fx += dx * alpha
            self._state.fy += dy * alpha

        ix, iy = int(self._state.fx), int(self._state.fy)
        new_pos = (ix, iy)
        if new_pos == self._state.last_position:
            return None
        self._state.last_position = new_pos
        return new_pos

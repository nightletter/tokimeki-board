from __future__ import annotations

from PyQt6.QtWidgets import QLabel

from src.services.image_storage import ScaledImageStore


class QtImageRenderer:
    def __init__(self, label: QLabel, store: ScaledImageStore):
        self._label = label
        self._store = store
        self._current_index = 0

    def set_store(self, store: ScaledImageStore) -> None:
        self._store = store
        self._current_index = 0

    def show_named(self, name: str) -> bool:
        frame = self._store.frame_of(name)
        if frame is None:
            return False
        self._label.setPixmap(frame)
        return True

    def show_cycle_current(self) -> bool:
        if not self._store.cycle_frames:
            return False
        self._label.setPixmap(self._store.cycle_frames[self._current_index])
        return True

    def show_cycle_next(self) -> bool:
        if len(self._store.cycle_frames) <= 1:
            return False
        self._current_index = (self._current_index + 1) % len(self._store.cycle_frames)
        self._label.setPixmap(self._store.cycle_frames[self._current_index])
        return True

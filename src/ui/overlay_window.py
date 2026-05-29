from __future__ import annotations

import sys

from dataclasses import replace

from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

from core.config import AppConfig
from src.services.input_handler import create_keypress_listener, create_scroll_listener
from core.events import KeyEvent, ScrollEvent
from src.services.image_storage import ImageStoreCache
from src.ui.qt_renderer import QtImageRenderer
from src.ui.system_tray import SystemTrayController
from src.services.cursor_follower import CursorFollower
from src.services.image_controller import ImageCommand, ImageCommandType, ImageController, KeyImageResult


class OverlayWindow(QWidget):
    key_pressed = pyqtSignal(object)
    mouse_scrolled = pyqtSignal(object)

    def __init__(
        self,
        config: AppConfig,
        image_store,
        cursor_follower: CursorFollower,
        image_controller: ImageController,
        icon_path: str,
        keyboard_backend,
        mouse_backend,
        base_dir: str,
        key_image_stems: frozenset[str],
    ):
        super().__init__()
        self._config = config
        self._base_dir = base_dir
        self._key_image_stems = key_image_stems
        self._cursor_follower = cursor_follower
        self._image_controller = image_controller
        self._keyboard_backend = keyboard_backend
        self._mouse_backend = mouse_backend
        self._keyboard_listener = None
        self._mouse_listener = None
        self._tray: SystemTrayController | None = None
        self._last_command: ImageCommand | None = None

        self._setup_window()
        self._setup_label()
        self._renderer = QtImageRenderer(self.label, image_store)

        self._setup_timers()
        self.key_pressed.connect(self._on_key_event)
        self.mouse_scrolled.connect(self._on_scroll_event)

        self._apply_command(self._image_controller.initial_command())
        self._setup_keyboard_listener()
        self._setup_mouse_listener()

        if sys.platform in ("win32", "darwin"):
            self._tray = SystemTrayController(
                parent=self,
                icon_path=icon_path,
                on_toggle=self._toggle_visibility,
                on_quit=QApplication.instance().quit,
                on_resize=self.update_default_size,
            )

    def update_default_size(self, new_size: int) -> None:
        if new_size <= 0:
            raise ValueError("default_size must be a positive integer")
        if new_size == self._config.size:
            return
        self._config = replace(self._config, size=new_size)
        self.resize(new_size, new_size)
        self.label.resize(new_size, new_size)
        image_store = ImageStoreCache.instance().get_or_build(
            self._base_dir,
            new_size,
            self._config.assets,
            self._key_image_stems,
        )
        self._renderer.set_store(image_store)
        if self._last_command is None:
            self._apply_command(self._image_controller.initial_command())
        else:
            self._apply_command(self._last_command)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resize(self._config.size, self._config.size)

    def _setup_label(self):
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.resize(self._config.size, self._config.size)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setup_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self._config.timing.poll_ms)

        if self._image_controller.key_toggle_mode:
            self.keystroke_timer = QTimer(self)
            self.keystroke_timer.setSingleShot(True)
            self.keystroke_timer.timeout.connect(self._reset_to_default_when_idle)
        else:
            self.image_timer = QTimer(self)
            self.image_timer.timeout.connect(self._on_cycle_tick)
            self.image_timer.start(self._config.timing.image_change_ms)

        self.scroll_timer = QTimer(self)
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self._reset_scroll_image_when_idle)

    def _setup_keyboard_listener(self):
        if self._keyboard_backend is None:
            return
        self._keyboard_listener = create_keypress_listener(
            self._keyboard_backend,
            lambda event: self.key_pressed.emit(event),
        )
        self._keyboard_listener.start()

    def _setup_mouse_listener(self):
        if self._mouse_backend is None:
            return
        self._mouse_listener = create_scroll_listener(
            self._mouse_backend,
            lambda event: self.mouse_scrolled.emit(event),
            idle_ms=self._config.input.scroll_idle_ms,
        )
        self._mouse_listener.start()

    def _toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
        if self._tray is not None:
            self._tray.sync_toggle_label(self.isVisible())

    def _on_key_event(self, event: KeyEvent):
        result = self._image_controller.on_key_pressed(event.value)
        if result is None:
            return
        self._apply_key_result(result)

    def _apply_key_result(self, result: KeyImageResult):
        self._apply_command(result.command)
        if result.flash_ms > 0:
            self.keystroke_timer.start(result.flash_ms)

    def _reset_to_default_when_idle(self):
        self._apply_command(self._image_controller.on_key_idle())

    def _on_scroll_event(self, event: ScrollEvent):
        command = self._image_controller.on_scroll_event(event)
        if command is None:
            return
        self._apply_command(command)
        self.scroll_timer.start(self._config.timing.scroll_flash_ms)

    def _reset_scroll_image_when_idle(self):
        self._apply_command(self._image_controller.on_scroll_idle())

    def _on_cycle_tick(self):
        self._apply_command(self._image_controller.on_cycle_tick())

    def _apply_command(self, command: ImageCommand | None):
        if command is None:
            return
        self._last_command = command
        if command.command_type == ImageCommandType.SHOW_NAMED:
            if command.name is not None:
                self._renderer.show_named(command.name)
            return
        if command.command_type == ImageCommandType.SHOW_CYCLE_CURRENT:
            self._renderer.show_cycle_current()
            return
        if command.command_type == ImageCommandType.SHOW_CYCLE_NEXT:
            self._renderer.show_cycle_next()

    def _tick(self):
        cursor = QCursor.pos()
        next_pos = self._cursor_follower.update((cursor.x(), cursor.y()))
        if next_pos is None:
            return
        ix, iy = next_pos
        self.move(QPoint(ix, iy))

    def closeEvent(self, event):
        if (
            sys.platform in ("win32", "darwin")
            and self._tray is not None
            and self._tray.is_visible()
        ):
            event.ignore()
            self.hide()
            self._tray.sync_toggle_label(False)
            return

        if self._keyboard_listener is not None:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None
        super().closeEvent(event)

    def keyPressEvent(self, event):
        event.accept()

    def keyReleaseEvent(self, event):
        event.accept()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)

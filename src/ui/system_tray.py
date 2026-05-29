from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from core import display_sizes


class SystemTrayController:
    def __init__(
        self,
        parent: QWidget,
        icon_path: str,
        on_toggle: Callable[[], None],
        on_quit: Callable[[], None],
        on_resize: Callable[[int], None] | None = None,
    ):
        self._tray_icon = QSystemTrayIcon(parent)
        if icon_path:
            icon = QIcon(icon_path)
            if not icon.isNull():
                self._tray_icon.setIcon(icon)
            else:
                self._tray_icon.setIcon(parent.style().standardIcon(parent.style().SP_ComputerIcon))
        else:
            self._tray_icon.setIcon(parent.style().standardIcon(parent.style().SP_ComputerIcon))

        tray_menu = QMenu()
        self._toggle_action = QAction("숨기기", parent)
        self._toggle_action.triggered.connect(on_toggle)
        tray_menu.addAction(self._toggle_action)

        tray_menu.addSeparator()

        large_action = QAction("크게", parent)
        large_action.triggered.connect(lambda: on_resize(display_sizes.l_size))
        tray_menu.addAction(large_action)

        medium_action = QAction("기본", parent)
        medium_action.triggered.connect(lambda: on_resize(display_sizes.m_size))
        tray_menu.addAction(medium_action)

        small_action = QAction("작게", parent)
        small_action.triggered.connect(lambda: on_resize(display_sizes.s_size))
        tray_menu.addAction(small_action)

        tray_menu.addSeparator()

        quit_action = QAction("종료", parent)
        quit_action.triggered.connect(on_quit)
        tray_menu.addAction(quit_action)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_activated(on_toggle))
        self._tray_icon.show()

    def _on_activated(self, on_toggle: Callable[[], None]):
        def handler(reason):
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                on_toggle()

        return handler

    def sync_toggle_label(self, is_visible: bool) -> None:
        self._toggle_action.setText("숨기기" if is_visible else "보이기")

    def is_visible(self) -> bool:
        return self._tray_icon.isVisible()

from __future__ import annotations

import signal
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCursor, QIcon
from PyQt6.QtWidgets import QApplication

from core import display_sizes
from core.config import default_config
from src.services.asset_loader import get_base_dir, get_icon_path
from src.services.image_storage import ImageStoreCache, build_key_image_stems, has_key_toggle_images
from src.services.image_controller import ImageController
from src.services.input_handler import (
    import_keyboard_backend,
    import_mouse_backend,
)
from src.services.cursor_follower import CursorFollower
from src.ui.overlay_window import OverlayWindow
from src.ui.permissions import prompt_for_permissions


def main() -> int:
    config = default_config()
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    app.setApplicationDisplayName(config.app_name)

    if sys.platform != "win32":
        prompt_for_permissions()

    base_dir = get_base_dir(__file__, config.assets)
    icon_path = get_icon_path(base_dir, config.assets)
    icon = QIcon(icon_path)
    if not icon.isNull():
        app.setWindowIcon(icon)

    if sys.platform in ("win32", "darwin"):
        app.setQuitOnLastWindowClosed(False)
    else:
        app.setQuitOnLastWindowClosed(True)

    signal.signal(signal.SIGINT, lambda *_: app.quit())

    signal_tick = QTimer()
    signal_tick.timeout.connect(lambda: None)
    signal_tick.start(200)

    key_image_stems = build_key_image_stems(config.keyboard_mapper, config.scroll_mapper)
    image_store = ImageStoreCache.instance().get_or_build(
        base_dir,
        display_sizes.m_size,
        config.assets,
        key_image_stems,
    )
    if not image_store.cycle_frames:
        return 0

    key_toggle_mode = has_key_toggle_images(image_store, config.keyboard_mapper)
    pos = QCursor.pos()
    cursor_follower = CursorFollower(config.motion, (pos.x(), pos.y()))
    image_controller = ImageController(config.keyboard_mapper, config.scroll_mapper, key_toggle_mode)

    window = OverlayWindow(
        config=config,
        image_store=image_store,
        cursor_follower=cursor_follower,
        image_controller=image_controller,
        icon_path=icon_path,
        keyboard_backend=import_keyboard_backend(),
        mouse_backend=import_mouse_backend(),
        base_dir=base_dir,
        key_image_stems=key_image_stems,
    )
    window.show()
    return app.exec()

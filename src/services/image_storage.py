from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import ClassVar

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QGuiApplication

from core.config import AssetsConfig
from src.services.asset_loader import get_assets_images_dir, list_image_names
from mappers.keyboard_mapper import KeyboardMapper
from mappers.scroll_mapper import ScrollMapper


def _prescale(path: str, size: int) -> QPixmap:

    image = QImage(path)
    if image.isNull():
        return QPixmap()

    screen = QGuiApplication.primaryScreen()
    dpr = screen.devicePixelRatio() if screen else 1.0

    scaled_size = int(size * dpr)

    scaled_image = image.scaled(
        scaled_size,
        scaled_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    pm = QPixmap.fromImage(scaled_image)
    pm.setDevicePixelRatio(dpr)

    return pm


def build_key_image_stems(keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper) -> frozenset[str]:
    kb_names = keyboard_mapper.image_names
    scroll_names = scroll_mapper.image_names
    rule_names = {rule.image_name for rule in keyboard_mapper.special_char_rules.values()}
    return frozenset(
        {
            kb_names.default,
            kb_names.stroke,
            scroll_names.up,
            scroll_names.down,
            *rule_names,
        }
    )


@dataclass(frozen=True)
class ScaledImageStore:
    cycle_frames: list[QPixmap]
    named_indexes: dict[str, int] = field(default_factory=dict)

    def has_named(self, image_name: str) -> bool:
        return image_name in self.named_indexes

    def index_of(self, image_name: str) -> int | None:
        return self.named_indexes.get(image_name)

    def frame_of(self, image_name: str) -> QPixmap | None:
        index = self.index_of(image_name)
        if index is None:
            return None
        if index < 0 or index >= len(self.cycle_frames):
            return None
        return self.cycle_frames[index]


def has_key_toggle_images(store: ScaledImageStore, keyboard_mapper: KeyboardMapper) -> bool:
    kb_names = keyboard_mapper.image_names
    return store.has_named(kb_names.default) and store.has_named(kb_names.stroke)


def build_scaled_image_store(
        base_dir: str,
        display_size: int,
        assets: AssetsConfig,
        key_image_stems: frozenset[str],
) -> ScaledImageStore:
    images_dir = get_assets_images_dir(base_dir, assets)
    image_names = list_image_names(images_dir, assets)

    cycle_frames: list[QPixmap] = []
    named_indexes: dict[str, int] = {}

    for name in image_names:
        path = os.path.join(images_dir, name)

        scaled = _prescale(path, display_size)

        if scaled.isNull():
            continue

        frame_index = len(cycle_frames)
        cycle_frames.append(scaled)

        stem, _ = os.path.splitext(name)
        lowered = stem.lower()
        if lowered in key_image_stems and lowered not in named_indexes:
            named_indexes[lowered] = frame_index

    return ScaledImageStore(cycle_frames=cycle_frames, named_indexes=named_indexes)


class ImageStoreCache:
    _instance: ClassVar[ImageStoreCache | None] = None

    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], ScaledImageStore] = {}

    @classmethod
    def instance(cls) -> ImageStoreCache:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_or_build(
            self,
            base_dir: str,
            display_size: int,
            assets: AssetsConfig,
            key_image_stems: frozenset[str],
    ) -> ScaledImageStore:
        key = (base_dir, display_size)
        store = self._cache.get(key)
        if store is None:
            store = build_scaled_image_store(base_dir, display_size, assets, key_image_stems)
            self._cache[key] = store
        return store
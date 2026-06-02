from __future__ import annotations

from dataclasses import dataclass

from core import display_sizes
from mappers.keyboard_mapper import KeyboardMapper, create_keyboard_mapper
from mappers.scroll_mapper import ScrollMapper, create_scroll_mapper


@dataclass(frozen=True)
class MotionConfig:
    offset_x: int
    offset_y: int
    smooth: float
    snap_threshold: float


@dataclass(frozen=True)
class TimingConfig:
    poll_ms: int
    image_change_ms: int
    scroll_flash_ms: int


@dataclass(frozen=True)
class KeyboardConfig:
    mapper: KeyboardMapper


@dataclass(frozen=True)
class InputConfig:
    scroll_idle_ms: int


@dataclass(frozen=True)
class AssetsConfig:
    assets_dirname: str
    assets_images_dirname: str
    icon_filename: str
    image_exts: frozenset[str]


@dataclass(frozen=True)
class AppConfig:
    app_name: str
    version: str
    size: int
    motion: MotionConfig
    timing: TimingConfig
    keyboard: KeyboardConfig
    input: InputConfig
    assets: AssetsConfig
    keyboard_mapper: KeyboardMapper
    scroll_mapper: ScrollMapper


def default_config() -> AppConfig:
    keyboard_mapper = create_keyboard_mapper()
    scroll_mapper = create_scroll_mapper()
    
    return AppConfig(
        app_name="TOKIMEKI BOARD",
        version="0.0.1",
        size=display_sizes.m_size,
        motion=MotionConfig(
            offset_x=10,
            offset_y=20,
            smooth=0.15,
            snap_threshold=0.3,
        ),
        timing=TimingConfig(
            poll_ms=8,
            image_change_ms=5000,
            scroll_flash_ms=500,
        ),
        keyboard=KeyboardConfig(mapper=keyboard_mapper),
        input=InputConfig(scroll_idle_ms=120),
        assets=AssetsConfig(
            assets_dirname="assets",
            assets_images_dirname="images",
            icon_filename="icon.png",
            image_exts=frozenset({".png"}),
        ),
        keyboard_mapper=keyboard_mapper,
        scroll_mapper=scroll_mapper,
    )

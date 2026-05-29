from __future__ import annotations

import os
import sys

from core.config import AssetsConfig


def get_base_dir(anchor_file: str | None, assets: AssetsConfig) -> str:
    if getattr(sys, "frozen", False):
        executable_dir = os.path.dirname(sys.executable)
        resources_dir = os.path.abspath(os.path.join(executable_dir, "../tokimeki_board", "Resources"))
        if os.path.isdir(os.path.join(resources_dir, assets.assets_dirname)):
            return resources_dir
        bundled_dir = getattr(sys, "_MEIPASS", None)
        if isinstance(bundled_dir, str):
            assets_dir = os.path.join(bundled_dir, assets.assets_dirname)
            if os.path.isdir(assets_dir):
                return bundled_dir
        return executable_dir
    if anchor_file is None:
        anchor_file = __file__
    anchor_dir = os.path.dirname(os.path.abspath(anchor_file))
    candidate = anchor_dir
    while True:
        if os.path.isdir(os.path.join(candidate, assets.assets_dirname)):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return anchor_dir


def get_assets_dir(base_dir: str, assets: AssetsConfig) -> str:
    return os.path.join(base_dir, assets.assets_dirname)


def get_assets_images_dir(base_dir: str, assets: AssetsConfig) -> str:
    return os.path.join(get_assets_dir(base_dir, assets), assets.assets_images_dirname)


def get_icon_path(base_dir: str, assets: AssetsConfig) -> str:
    return os.path.join(get_assets_dir(base_dir, assets), assets.icon_filename)


def is_image_file(name: str, assets: AssetsConfig) -> bool:
    return os.path.splitext(name)[1].lower() in assets.image_exts


def list_image_names(directory: str, assets: AssetsConfig) -> list[str]:
    if not os.path.isdir(directory):
        return []
    return sorted(
        entry.name
        for entry in os.scandir(directory)
        if entry.is_file() and is_image_file(entry.name, assets)
    )


def collect_runtime_image_paths(base_dir: str, assets: AssetsConfig) -> list[str]:
    directory = get_assets_images_dir(base_dir, assets)
    names = list_image_names(directory, assets)
    return [os.path.join(directory, name) for name in names]


def find_named_image_paths(
    base_dir: str,
    stems: set[str] | frozenset[str],
    assets: AssetsConfig,
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    target_stems = {stem.lower() for stem in stems}
    directory = get_assets_images_dir(base_dir, assets)
    if not os.path.isdir(directory):
        return mapping
    for entry in os.scandir(directory):
        if not entry.is_file() or not is_image_file(entry.name, assets):
            continue
        stem, _ = os.path.splitext(entry.name)
        lowered = stem.lower()
        if lowered in target_stems and lowered not in mapping:
            mapping[lowered] = entry.path
    return mapping

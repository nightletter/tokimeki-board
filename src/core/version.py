from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
VERSION_PATH = ROOT_DIR / "version.json"


def _candidate_version_paths() -> list[Path]:
    paths: list[Path] = []
    bundled_root = getattr(sys, "_MEIPASS", None) if getattr(sys, "frozen", False) else None
    if isinstance(bundled_root, str):
        paths.append(Path(bundled_root) / "version.json")
    paths.append(VERSION_PATH)
    return paths


@lru_cache(maxsize=1)
def load_current_version() -> str:
    for version_path in _candidate_version_paths():
        try:
            with version_path.open(encoding="utf-8") as version_file:
                data = json.load(version_file)
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
            continue

        version = data.get("version")
        if isinstance(version, str) and version:
            return version

    return "0.0.0"

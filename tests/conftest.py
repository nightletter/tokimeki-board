"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src directory to path so imports work correctly in tests
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


@pytest.fixture
def sample_cursor_position() -> tuple[int, int]:
    """Provide a sample cursor position."""
    return (500, 500)


@pytest.fixture
def sample_cursor_offset() -> tuple[int, int]:
    """Provide a sample cursor offset."""
    return (10, 20)


@pytest.fixture
def test_assets_dir(tmp_path) -> str:
    """Create a temporary directory for test assets."""
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "images").mkdir()
    return str(assets_dir)

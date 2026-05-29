"""Scroll event to image mapping."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScrollImageNames:
    """Image names for scroll events."""
    up: str
    down: str


@dataclass(frozen=True)
class ScrollMapper:
    """Scroll event to image mapper."""
    image_names: ScrollImageNames


def create_scroll_mapper() -> ScrollMapper:
    """Create default scroll mapper with standard configuration."""
    image_names = ScrollImageNames(
        up="m_scroll_up",
        down="m_scroll_down",
    )
    
    return ScrollMapper(image_names=image_names)

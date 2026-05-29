from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ScrollPhase(str, Enum):
    START = "start"
    END = "end"


class ScrollDirection(str, Enum):
    UP = "up"
    DOWN = "down"


@dataclass(frozen=True)
class ScrollEvent:
    phase: ScrollPhase
    direction: ScrollDirection


@dataclass(frozen=True)
class KeyEvent:
    value: str

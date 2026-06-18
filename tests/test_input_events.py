"""Tests for interfaces and input events."""

from __future__ import annotations

import pytest

from core.events import KeyEvent, ScrollDirection, ScrollEvent, ScrollPhase
from src.services.keys import NUMPAD_VK_CODES_MAC, NUMPAD_VK_CODES_WINDOWS
from src.services.input_handler import extract_typed_key


class DummyKey:
    def __init__(self, char=None, name=None, vk=None):
        self.char = char
        self.name = name
        self.vk = vk


class TestScrollPhase:
    """Test ScrollPhase enum."""

    def test_scroll_phase_values(self):
        """Test ScrollPhase enum values."""
        assert ScrollPhase.START.value == "start"
        assert ScrollPhase.END.value == "end"

    def test_scroll_phase_comparison(self):
        """Test ScrollPhase comparison."""
        assert ScrollPhase.START == ScrollPhase.START
        assert ScrollPhase.START != ScrollPhase.END

    def test_scroll_phase_is_string(self):
        """Test that ScrollPhase is a string enum."""
        assert isinstance(ScrollPhase.START, str)
        assert isinstance(ScrollPhase.END, str)


class TestScrollDirection:
    """Test ScrollDirection enum."""

    def test_scroll_direction_values(self):
        """Test ScrollDirection enum values."""
        assert ScrollDirection.UP.value == "up"
        assert ScrollDirection.DOWN.value == "down"

    def test_scroll_direction_comparison(self):
        """Test ScrollDirection comparison."""
        assert ScrollDirection.UP == ScrollDirection.UP
        assert ScrollDirection.UP != ScrollDirection.DOWN

    def test_scroll_direction_is_string(self):
        """Test that ScrollDirection is a string enum."""
        assert isinstance(ScrollDirection.UP, str)
        assert isinstance(ScrollDirection.DOWN, str)


class TestScrollEvent:
    """Test ScrollEvent dataclass."""

    def test_scroll_event_creation(self):
        """Test creating a ScrollEvent."""
        event = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
        assert event.phase == ScrollPhase.START
        assert event.direction == ScrollDirection.UP

    def test_scroll_event_frozen(self):
        """Test that ScrollEvent is frozen (immutable)."""
        event = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
        with pytest.raises(AttributeError):
            event.phase = ScrollPhase.END

    def test_scroll_event_all_combinations(self):
        """Test all combinations of phase and direction."""
        combinations = [
            (ScrollPhase.START, ScrollDirection.UP),
            (ScrollPhase.START, ScrollDirection.DOWN),
            (ScrollPhase.END, ScrollDirection.UP),
            (ScrollPhase.END, ScrollDirection.DOWN),
        ]
        for phase, direction in combinations:
            event = ScrollEvent(phase=phase, direction=direction)
            assert event.phase == phase
            assert event.direction == direction

    def test_scroll_event_equality(self):
        """Test ScrollEvent equality."""
        event1 = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
        event2 = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
        assert event1 == event2

    def test_scroll_event_inequality(self):
        """Test ScrollEvent inequality."""
        event1 = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
        event2 = ScrollEvent(phase=ScrollPhase.END, direction=ScrollDirection.DOWN)
        assert event1 != event2


class TestKeyEvent:
    """Test KeyEvent dataclass."""

    def test_key_event_creation(self):
        """Test creating a KeyEvent."""
        event = KeyEvent(value="a")
        assert event.value == "a"

    def test_key_event_special_keys(self):
        """Test KeyEvent with special key values."""
        special_keys = ["enter", "escape", "backspace", "shift", "control", "alt"]
        for key in special_keys:
            event = KeyEvent(value=key)
            assert event.value == key

    def test_key_event_frozen(self):
        """Test that KeyEvent is frozen (immutable)."""
        event = KeyEvent(value="a")
        with pytest.raises(AttributeError):
            event.value = "b"

    def test_key_event_equality(self):
        """Test KeyEvent equality."""
        event1 = KeyEvent(value="a")
        event2 = KeyEvent(value="a")
        assert event1 == event2

    def test_key_event_inequality(self):
        """Test KeyEvent inequality."""
        event1 = KeyEvent(value="a")
        event2 = KeyEvent(value="b")
        assert event1 != event2

    def test_key_event_unicode_characters(self):
        """Test KeyEvent with unicode characters."""
        unicode_keys = ["?", "!", ".", "한", "가"]
        for key in unicode_keys:
            event = KeyEvent(value=key)
            assert event.value == key


class TestExtractTypedKey:
    """Test key extraction and normalization."""

    @pytest.mark.parametrize(
        ("key", "expected"),
        [
            (DummyKey(char="0", name="num_0"), "0"),
            (DummyKey(char="5", name="numpad_5"), "5"),
            (DummyKey(char=".", name="num_decimal"), "."),
            (DummyKey(char=None, name="decimal"), "."),
            (DummyKey(char=None, name="num_9"), "9"),
            (DummyKey(char=None, name="numpad_3"), "3"),
            (DummyKey(char=None, name="numpad_decimal"), "."),
            *[
                (DummyKey(char=None, vk=vk), expected)
                for vk, expected in NUMPAD_VK_CODES_WINDOWS.items()
            ],
            *[
                (DummyKey(char=None, vk=vk), expected)
                for vk, expected in NUMPAD_VK_CODES_MAC.items()
            ],
        ],
    )
    def test_extract_typed_key_normalizes_numpad_input(self, key, expected):
        assert extract_typed_key(key) == expected

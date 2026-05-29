"""Tests for domain models."""

from __future__ import annotations

import pytest

from src.core.models import CursorState, KeyHoldState, KeyToggleState


class TestCursorState:
    """Test CursorState model."""

    def test_cursor_state_creation(self):
        """Test creating CursorState with initial values."""
        state = CursorState(fx=100.5, fy=200.5)
        assert state.fx == 100.5
        assert state.fy == 200.5
        assert state.last_position is None

    def test_cursor_state_with_last_position(self):
        """Test creating CursorState with last position."""
        state = CursorState(fx=100.5, fy=200.5, last_position=(100, 200))
        assert state.fx == 100.5
        assert state.fy == 200.5
        assert state.last_position == (100, 200)

    def test_cursor_state_mutable(self):
        """Test that CursorState is mutable (not frozen)."""
        state = CursorState(fx=100.0, fy=200.0)
        state.fx = 150.0
        assert state.fx == 150.0

    def test_cursor_state_last_position_update(self):
        """Test updating last_position."""
        state = CursorState(fx=100.0, fy=200.0, last_position=(100, 200))
        state.last_position = (150, 250)
        assert state.last_position == (150, 250)


class TestKeyToggleState:
    """Test KeyToggleState model."""

    def test_key_toggle_state_default(self):
        """Test default values for KeyToggleState."""
        state = KeyToggleState()
        assert state.stroke_visible is False
        assert state.key_press_count == 0

    def test_key_toggle_state_with_values(self):
        """Test creating KeyToggleState with custom values."""
        state = KeyToggleState(stroke_visible=True, key_press_count=5)
        assert state.stroke_visible is True
        assert state.key_press_count == 5

    def test_key_toggle_state_mutable(self):
        """Test that KeyToggleState is mutable."""
        state = KeyToggleState()
        state.stroke_visible = True
        state.key_press_count = 3
        assert state.stroke_visible is True
        assert state.key_press_count == 3

    def test_key_toggle_state_stroke_visibility_toggle(self):
        """Test toggling stroke visibility."""
        state = KeyToggleState()
        assert state.stroke_visible is False
        state.stroke_visible = True
        assert state.stroke_visible is True
        state.stroke_visible = False
        assert state.stroke_visible is False

    def test_key_toggle_state_press_count_increment(self):
        """Test incrementing press count."""
        state = KeyToggleState()
        for i in range(10):
            state.key_press_count = i
            assert state.key_press_count == i


class TestKeyHoldState:
    """Test KeyHoldState model."""

    def test_key_hold_state_default(self):
        """Test default values for KeyHoldState."""
        state = KeyHoldState()
        assert state.hold_until == 0.0
        assert state.hold_key is None

    def test_key_hold_state_with_values(self):
        """Test creating KeyHoldState with custom values."""
        state = KeyHoldState(hold_until=1.5, hold_key="enter")
        assert state.hold_until == 1.5
        assert state.hold_key == "enter"

    def test_key_hold_state_mutable(self):
        """Test that KeyHoldState is mutable."""
        state = KeyHoldState()
        state.hold_until = 2.0
        state.hold_key = "escape"
        assert state.hold_until == 2.0
        assert state.hold_key == "escape"

    def test_key_hold_state_clear(self):
        """Test clearing hold state."""
        state = KeyHoldState(hold_until=1.5, hold_key="enter")
        state.hold_until = 0.0
        state.hold_key = None
        assert state.hold_until == 0.0
        assert state.hold_key is None

    def test_key_hold_state_different_keys(self):
        """Test holding different keys."""
        state = KeyHoldState()
        keys = ["enter", "escape", "backspace", "shift"]
        for key in keys:
            state.hold_key = key
            state.hold_until = 1.0
            assert state.hold_key == key
            assert state.hold_until == 1.0

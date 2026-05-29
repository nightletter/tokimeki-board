"""Tests for CursorFollower use case."""

from __future__ import annotations

import pytest

from core.config import MotionConfig
from src.services.cursor_follower import CursorFollower


class TestCursorFollower:
    """Test CursorFollower movement and position tracking."""

    @pytest.fixture
    def motion_config(self) -> MotionConfig:
        """Create a default motion config for testing."""
        return MotionConfig(
            offset_x=10,
            offset_y=20,
            smooth=0.15,
            snap_threshold=0.3,
        )

    @pytest.fixture
    def follower(self, motion_config: MotionConfig) -> CursorFollower:
        """Create a CursorFollower instance."""
        return CursorFollower(motion_config, initial_pos=(100, 100))

    def test_initialization(self, follower: CursorFollower, motion_config: MotionConfig):
        """Test that CursorFollower initializes with correct position."""
        # Initial position should be cursor pos + offset
        expected_x = 100 + motion_config.offset_x
        expected_y = 100 + motion_config.offset_y
        assert follower._state.fx == float(expected_x)
        assert follower._state.fy == float(expected_y)

    def test_snap_threshold(self, motion_config: MotionConfig):
        """Test snap behavior when within threshold."""
        follower = CursorFollower(motion_config, initial_pos=(100, 100))
        target_x = 100 + 0.1  # Within snap threshold (0.3)
        target_y = 100 + 0.1

        result = follower.update((int(target_x), int(target_y)))

        # Should snap to exact position
        assert follower._state.fx == float(int(target_x) + motion_config.offset_x)
        assert follower._state.fy == float(int(target_y) + motion_config.offset_y)

    def test_smooth_movement(self, motion_config: MotionConfig):
        """Test smooth interpolation when outside threshold."""
        follower = CursorFollower(motion_config, initial_pos=(100, 100))

        # Move cursor far away (will trigger smooth movement)
        result1 = follower.update((200, 200))
        assert result1 is not None

        # Position should have moved toward target but not reached it
        alpha = 1.0 - motion_config.smooth
        assert follower._state.fx > (100 + motion_config.offset_x)
        assert follower._state.fy > (100 + motion_config.offset_y)

    def test_no_movement_returns_none(self, follower: CursorFollower):
        """Test that update returns None when position doesn't change."""
        # First update at same position
        result1 = follower.update((100, 100))
        assert result1 is not None

        # Second update at same position should return None
        result2 = follower.update((100, 100))
        assert result2 is None

    def test_position_change_returns_coords(self, follower: CursorFollower):
        """Test that update returns coordinates when position changes."""
        result = follower.update((150, 150))
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_offset_applied(self, motion_config: MotionConfig):
        """Test that offset is properly applied to cursor position."""
        follower = CursorFollower(motion_config, initial_pos=(0, 0))
        # Move cursor far enough to avoid snap threshold
        follower.update((500, 500))

        # Position should include offset
        assert follower._state.fx > motion_config.offset_x
        assert follower._state.fy > motion_config.offset_y

    def test_smooth_factor_zero(self):
        """Test instant movement with smooth=0."""
        motion_config = MotionConfig(
            offset_x=0,
            offset_y=0,
            smooth=0.0,  # No smoothing
            snap_threshold=0.0,  # No snap threshold
        )
        follower = CursorFollower(motion_config, initial_pos=(0, 0))

        # Should move to target instantly
        result = follower.update((100, 100))
        assert follower._state.fx == 100.0
        assert follower._state.fy == 100.0

    def test_smooth_factor_max(self):
        """Test minimal movement with smooth=1 (maximum smoothing)."""
        motion_config = MotionConfig(
            offset_x=0,
            offset_y=0,
            smooth=1.0,  # Maximum smoothing
            snap_threshold=0.0,
        )
        follower = CursorFollower(motion_config, initial_pos=(0, 0))

        result = follower.update((100, 100))
        # With smooth=1, alpha=0, so no movement - returns initial position
        assert follower._state.fx == 0.0
        assert follower._state.fy == 0.0
        # Position returns as (0, 0) since no interpolation happens
        assert result == (0, 0)

    def test_consecutive_movements(self, follower: CursorFollower):
        """Test multiple consecutive cursor movements."""
        positions = [(150, 150), (200, 200), (175, 175), (100, 100)]
        results = []

        for pos in positions:
            result = follower.update(pos)
            if result is not None:
                results.append(result)

        # Should have recorded movement at least once
        assert len(results) > 0

    def test_integer_position_output(self, follower: CursorFollower):
        """Test that output positions are integers."""
        result = follower.update((123, 456))
        if result is not None:
            assert isinstance(result[0], int)
            assert isinstance(result[1], int)

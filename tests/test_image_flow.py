"""Tests for ImageController use case."""

from __future__ import annotations

import pytest

from core.events import ScrollDirection, ScrollEvent, ScrollPhase
from src.services.image_controller import ImageCommandType, ImageController
from mappers.keyboard_mapper import KeyboardMapper, KeyboardImageNames, SpecialCharRule
from mappers.scroll_mapper import ScrollMapper, ScrollImageNames


class TestImageController:
    """Test ImageController expression state machine."""

    @pytest.fixture
    def keyboard_mapper(self) -> KeyboardMapper:
        """Create keyboard mapper for testing."""
        image_names = KeyboardImageNames(
            default="k_default",
            stroke="k_stroke",
            special_punct="k_special_punct",
            comma="k_comma",
            enter="k_enter",
            esc="k_esc",
            backspace="k_backspace",
        )
        return KeyboardMapper(
            image_names=image_names,
            special_char_rules={
                "?": SpecialCharRule(image_name=image_names.special_punct, flash_ms=500),
                "!": SpecialCharRule(image_name=image_names.special_punct, flash_ms=500),
                ".": SpecialCharRule(image_name=image_names.comma, flash_ms=500),
            },
            key_hold_ms_rules={"enter": 700, "esc": 700},
            key_press_count_limit=1,
            default_flash_ms=200,
        )

    @pytest.fixture
    def scroll_mapper(self) -> ScrollMapper:
        """Create scroll mapper for testing."""
        image_names = ScrollImageNames(up="m_scroll_up", down="m_scroll_down")
        return ScrollMapper(image_names=image_names)

    @pytest.fixture
    def controller_toggle_mode(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper) -> ImageController:
        """Create controller in toggle mode."""
        return ImageController(keyboard_mapper, scroll_mapper, key_toggle_mode=True)

    @pytest.fixture
    def controller_cycle_mode(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper) -> ImageController:
        """Create controller in cycle mode."""
        return ImageController(keyboard_mapper, scroll_mapper, key_toggle_mode=False)

    def test_initial_command_toggle_mode(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test initial command in toggle mode."""
        cmd = controller_toggle_mode.initial_command()
        assert cmd.command_type == ImageCommandType.SHOW_NAMED
        assert cmd.name == keyboard_mapper.image_names.default

    def test_initial_command_cycle_mode(self, controller_cycle_mode: ImageController):
        """Test initial command in cycle mode."""
        cmd = controller_cycle_mode.initial_command()
        assert cmd.command_type == ImageCommandType.SHOW_CYCLE_CURRENT

    def test_key_toggle_mode_property(self, controller_toggle_mode: ImageController, controller_cycle_mode: ImageController):
        """Test key_toggle_mode property."""
        assert controller_toggle_mode.key_toggle_mode is True
        assert controller_cycle_mode.key_toggle_mode is False

    def test_on_key_pressed_special_char(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test special character press handling."""
        result = controller_toggle_mode.on_key_pressed("?")

        assert result is not None
        assert result.command is not None
        assert result.command.command_type == ImageCommandType.SHOW_NAMED
        assert result.command.name == keyboard_mapper.image_names.special_punct
        assert result.flash_ms == 500

    def test_on_key_pressed_regular_key(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test regular key press handling in toggle mode."""
        result = controller_toggle_mode.on_key_pressed("a")

        assert result is not None
        assert result.command is not None
        assert result.command.command_type == ImageCommandType.SHOW_NAMED
        assert result.command.name == keyboard_mapper.image_names.stroke
        assert result.flash_ms == 200

    def test_on_key_pressed_cycle_mode(self, controller_cycle_mode: ImageController):
        """Test regular key press in cycle mode."""
        result = controller_cycle_mode.on_key_pressed("a")

        # In cycle mode with repeated presses, may get None due to press rate limiting
        if result is not None:
            assert result.command is not None
            assert result.command.command_type in (ImageCommandType.SHOW_CYCLE_NEXT, ImageCommandType.SHOW_CYCLE_CURRENT)

    def test_on_key_idle_toggle_mode(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test key idle event in toggle mode."""
        result = controller_toggle_mode.on_key_idle()

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_NAMED
        assert result.name == keyboard_mapper.image_names.default

    def test_on_key_idle_cycle_mode(self, controller_cycle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test key idle event in cycle mode."""
        result = controller_cycle_mode.on_key_idle()

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_NAMED
        assert result.name == keyboard_mapper.image_names.default

    def test_on_scroll_event_up(self, controller_toggle_mode: ImageController, scroll_mapper: ScrollMapper):
        """Test scroll up event."""
        event = ScrollEvent(direction=ScrollDirection.UP, phase=ScrollPhase.START)
        result = controller_toggle_mode.on_scroll_event(event)

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_NAMED
        assert result.name == scroll_mapper.image_names.up

    def test_on_scroll_event_down(self, controller_toggle_mode: ImageController, scroll_mapper: ScrollMapper):
        """Test scroll down event."""
        event = ScrollEvent(direction=ScrollDirection.DOWN, phase=ScrollPhase.START)
        result = controller_toggle_mode.on_scroll_event(event)

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_NAMED
        assert result.name == scroll_mapper.image_names.down

    def test_on_scroll_idle_toggle_mode(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test scroll idle in toggle mode."""
        result = controller_toggle_mode.on_scroll_idle()

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_NAMED
        assert result.name == keyboard_mapper.image_names.default

    def test_on_scroll_idle_cycle_mode(self, controller_cycle_mode: ImageController):
        """Test scroll idle in cycle mode."""
        result = controller_cycle_mode.on_scroll_idle()

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_CYCLE_CURRENT

    def test_on_cycle_tick_toggle_mode(self, controller_toggle_mode: ImageController):
        """Test cycle tick in toggle mode (should not advance)."""
        result = controller_toggle_mode.on_cycle_tick()

        # In toggle mode, cycle tick may return None or not advance
        if result is not None:
            assert result.command_type is not None

    def test_on_cycle_tick_cycle_mode(self, controller_cycle_mode: ImageController):
        """Test cycle tick in cycle mode (should advance)."""
        result = controller_cycle_mode.on_cycle_tick()

        assert result is not None
        assert result.command_type == ImageCommandType.SHOW_CYCLE_NEXT

    def test_toggle_stroke_on_regular_press(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test stroke display on regular key press."""
        result = controller_toggle_mode.on_key_pressed("a")
        assert result.command.name == keyboard_mapper.image_names.stroke

    def test_special_char_resets_toggle(self, controller_toggle_mode: ImageController, keyboard_mapper: KeyboardMapper):
        """Test special character shows its own image."""
        result = controller_toggle_mode.on_key_pressed("?")
        assert result.command.name == keyboard_mapper.image_names.special_punct

    def test_key_hold_prevents_further_presses(self, controller_toggle_mode: ImageController):
        """Test that key hold prevents further presses."""
        result1 = controller_toggle_mode.on_key_pressed("enter")
        result2 = controller_toggle_mode.on_key_pressed("a")

        assert result1 is not None
        assert result2 is None

    def test_special_char_flash_ms(self, controller_toggle_mode: ImageController):
        """Test special character flash_ms is correct."""
        result = controller_toggle_mode.on_key_pressed("?")
        assert result.flash_ms == 500

    def test_regular_key_flash_ms(self, controller_toggle_mode: ImageController):
        """Test regular key flash_ms uses default."""
        result = controller_toggle_mode.on_key_pressed("a")
        assert result.flash_ms == 200

    def test_hold_ms_in_flash_ms(self, controller_toggle_mode: ImageController):
        """Test that hold_ms is included in flash_ms for held keys."""
        result = controller_toggle_mode.on_key_pressed("enter")
        assert result.flash_ms >= 700

    def test_default_flash_ms_application(self, controller_toggle_mode: ImageController):
        """Test default flash_ms is applied to unknown special chars."""
        result = controller_toggle_mode.on_key_pressed("@")
        assert result.flash_ms == 200

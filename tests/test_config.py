"""Tests for config module."""

from __future__ import annotations

import pytest

from core.config import (
    AppConfig,
    AssetsConfig,
    InputConfig,
    KeyboardConfig,
    MotionConfig,
    TimingConfig,
    default_config,
)
from mappers.keyboard_mapper import create_keyboard_mapper
from mappers.scroll_mapper import create_scroll_mapper


class TestKeyboardMapper:
    """Test keyboard mapper."""

    def test_keyboard_mapper_creation(self):
        """Test KeyboardMapper creation."""
        mapper = create_keyboard_mapper()
        assert mapper.key_press_count_limit == 1
        assert mapper.default_flash_ms == 200

    def test_keyboard_mapper_frozen(self):
        """Test that KeyboardMapper is frozen."""
        mapper = create_keyboard_mapper()
        with pytest.raises(AttributeError):
            mapper.key_press_count_limit = 2

    def test_keyboard_mapper_special_char_rules(self):
        """Test special character rules in keyboard mapper."""
        mapper = create_keyboard_mapper()
        assert "?" in mapper.special_char_rules
        assert "!" in mapper.special_char_rules
        assert "." in mapper.special_char_rules
        assert mapper.special_char_rules["?"].flash_ms == 500

    def test_keyboard_mapper_key_hold_rules(self):
        """Test key hold rules in keyboard mapper."""
        mapper = create_keyboard_mapper()
        assert "enter" in mapper.key_hold_ms_rules
        assert "esc" in mapper.key_hold_ms_rules
        assert mapper.key_hold_ms_rules["enter"] == 700

    def test_keyboard_image_names_frozen(self):
        """Test that keyboard image names are frozen."""
        mapper = create_keyboard_mapper()
        with pytest.raises(AttributeError):
            mapper.image_names.default = "new_value"


class TestScrollMapper:
    """Test scroll mapper."""

    def test_scroll_mapper_creation(self):
        """Test ScrollMapper creation."""
        mapper = create_scroll_mapper()
        assert mapper.image_names.up == "m_scroll_up"
        assert mapper.image_names.down == "m_scroll_down"

    def test_scroll_mapper_frozen(self):
        """Test that ScrollMapper is frozen."""
        mapper = create_scroll_mapper()
        with pytest.raises(AttributeError):
            mapper.image_names.up = "new_value"


class TestMotionConfig:
    """Test motion configuration."""

    def test_motion_config_creation(self):
        """Test MotionConfig creation."""
        config = MotionConfig(
            offset_x=10,
            offset_y=20,
            smooth=0.15,
            snap_threshold=0.3,
        )
        assert config.offset_x == 10
        assert config.offset_y == 20
        assert config.smooth == 0.15
        assert config.snap_threshold == 0.3

    def test_motion_config_frozen(self):
        """Test that MotionConfig is frozen."""
        config = MotionConfig(offset_x=10, offset_y=20, smooth=0.15, snap_threshold=0.3)
        with pytest.raises(AttributeError):
            config.offset_x = 20


class TestTimingConfig:
    """Test timing configuration."""

    def test_timing_config_creation(self):
        """Test TimingConfig creation."""
        config = TimingConfig(
            poll_ms=8,
            image_change_ms=5000,
            scroll_flash_ms=500,
        )
        assert config.poll_ms == 8
        assert config.image_change_ms == 5000
        assert config.scroll_flash_ms == 500

    def test_timing_config_frozen(self):
        """Test that TimingConfig is frozen."""
        config = TimingConfig(poll_ms=8, image_change_ms=5000, scroll_flash_ms=500)
        with pytest.raises(AttributeError):
            config.poll_ms = 10


class TestKeyboardConfig:
    """Test keyboard configuration."""

    def test_keyboard_config_creation(self):
        """Test KeyboardConfig creation."""
        mapper = create_keyboard_mapper()
        config = KeyboardConfig(mapper=mapper)
        assert config.mapper is not None
        assert config.mapper.key_press_count_limit == 1

    def test_keyboard_config_frozen(self):
        """Test that KeyboardConfig is frozen."""
        mapper = create_keyboard_mapper()
        config = KeyboardConfig(mapper=mapper)
        with pytest.raises(AttributeError):
            config.mapper = None


class TestAssetsConfig:
    """Test assets configuration."""

    def test_assets_config_creation(self):
        """Test AssetsConfig creation."""
        config = AssetsConfig(
            assets_dirname="assets",
            assets_images_dirname="images",
            icon_filename="icon.png",
            image_exts=frozenset({".png", ".jpg", ".jpeg"}),
        )
        assert config.assets_dirname == "assets"
        assert config.assets_images_dirname == "images"
        assert ".png" in config.image_exts

    def test_assets_config_frozen(self):
        """Test that AssetsConfig is frozen."""
        config = AssetsConfig(
            assets_dirname="assets",
            assets_images_dirname="images",
            icon_filename="icon.png",
            image_exts=frozenset(),
        )
        with pytest.raises(AttributeError):
            config.assets_dirname = "new_dir"


class TestInputConfig:
    """Test input configuration."""

    def test_input_config_creation(self):
        """Test InputConfig creation."""
        config = InputConfig(scroll_idle_ms=120)
        assert config.scroll_idle_ms == 120

    def test_input_config_frozen(self):
        """Test that InputConfig is frozen."""
        config = InputConfig(scroll_idle_ms=120)
        with pytest.raises(AttributeError):
            config.scroll_idle_ms = 200


class TestAppConfig:
    """Test application configuration."""

    @pytest.fixture
    def minimal_config(self) -> AppConfig:
        """Create minimal AppConfig for testing."""
        keyboard_mapper = create_keyboard_mapper()
        scroll_mapper = create_scroll_mapper()
        return AppConfig(
            app_name="Test App",
            version="0.1.0",
            size=180,
            motion=MotionConfig(offset_x=0, offset_y=0, smooth=0.15, snap_threshold=0.3),
            timing=TimingConfig(poll_ms=8, image_change_ms=5000, scroll_flash_ms=500),
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

    def test_app_config_creation(self, minimal_config: AppConfig):
        """Test AppConfig creation."""
        assert minimal_config.app_name == "Test App"
        assert minimal_config.size == 180

    def test_app_config_frozen(self, minimal_config: AppConfig):
        """Test that AppConfig is frozen."""
        with pytest.raises(AttributeError):
            minimal_config.app_name = "New App"


class TestDefaultConfig:
    """Test default_config function."""

    def test_default_config_returns_valid_config(self):
        """Test that default_config returns a valid AppConfig."""
        config = default_config()
        assert isinstance(config, AppConfig)

    def test_default_config_has_required_fields(self):
        """Test that default_config includes all required fields."""
        config = default_config()
        assert config.app_name == "TOKIMEKI BOARD"
        assert config.size > 0
        assert config.motion is not None
        assert config.timing is not None
        assert config.keyboard is not None
        assert config.input is not None
        assert config.assets is not None
        assert config.keyboard_mapper is not None
        assert config.scroll_mapper is not None

    def test_default_config_motion_values(self):
        """Test default motion configuration values."""
        config = default_config()
        assert config.motion.offset_x == 10
        assert config.motion.offset_y == 20
        assert config.motion.smooth == 0.15
        assert config.motion.snap_threshold == 0.3

    def test_default_config_timing_values(self):
        """Test default timing configuration values."""
        config = default_config()
        assert config.timing.poll_ms == 8
        assert config.timing.image_change_ms == 5000
        assert config.timing.scroll_flash_ms == 500

    def test_default_config_keyboard_values(self):
        """Test default keyboard configuration values."""
        config = default_config()
        assert config.keyboard_mapper.key_press_count_limit == 1
        assert config.keyboard_mapper.default_flash_ms == 200

    def test_default_config_special_char_rules(self):
        """Test special character rules in default config."""
        config = default_config()
        assert "?" in config.keyboard_mapper.special_char_rules
        assert "!" in config.keyboard_mapper.special_char_rules
        assert "." in config.keyboard_mapper.special_char_rules
        assert config.keyboard_mapper.special_char_rules["?"].flash_ms == 500

    def test_default_config_key_hold_rules(self):
        """Test key hold rules in default config."""
        config = default_config()
        assert "enter" in config.keyboard_mapper.key_hold_ms_rules
        assert "esc" in config.keyboard_mapper.key_hold_ms_rules
        assert config.keyboard_mapper.key_hold_ms_rules["enter"] == 700

    def test_default_config_image_extensions(self):
        """Test supported image extensions."""
        config = default_config()
        assert ".png" in config.assets.image_exts

    def test_default_config_immutability(self):
        """Test that default config is immutable."""
        config = default_config()
        with pytest.raises(AttributeError):
            config.app_name = "Modified"

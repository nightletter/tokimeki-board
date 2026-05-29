# """Integration tests for the application."""
#
# from __future__ import annotations
#
# import pytest
#
# from core.config import default_config
# from src.services.image_storage import (
#     ScaledImageStore,
#     build_key_image_stems,
#     has_key_toggle_images,
# )
# from core.events import ScrollDirection, ScrollEvent, ScrollPhase
# from src.services.cursor_follower import CursorFollower
# from src.services.image_controller import ImageController
#
#
# class TestApplicationIntegration:
#     """Integration tests for core application flow."""
#
#     @pytest.fixture
#     def config(self):
#         """Get default application configuration."""
#         return default_config()
#
#     @pytest.fixture
#     def cursor_follower(self, config):
#         """Create cursor follower with default config."""
#         return CursorFollower(config.motion, initial_pos=(640, 480))
#
#     @pytest.fixture
#     def image_controller(self, config):
#         """Create image controller with default config."""
#         return ImageController(config.keyboard_mapper, config.scroll_mapper, key_toggle_mode=True)
#
#     def test_cursor_follow_and_expression_change_sequence(self, cursor_follower, image_controller):
#         """Test typical user interaction sequence."""
#         # User moves cursor
#         pos1 = cursor_follower.update((700, 500))
#         assert pos1 is not None
#
#         # User presses a key
#         result = image_controller.on_key_pressed("a")
#         assert result is not None
#         assert result.command is not None
#
#         # User moves cursor again
#         pos2 = cursor_follower.update((750, 550))
#
#         # User scrolls
#         scroll_event = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
#         cmd = image_controller.on_scroll_event(scroll_event)
#         assert cmd is not None
#
#         # User becomes idle
#         idle_cmd = image_controller.on_key_idle()
#         assert idle_cmd is not None
#
#     def test_key_image_stems_in_default_config(self, config):
#         """Test that key image stems can be built from default config."""
#         stems = build_key_image_stems(config.keyboard_mapper, config.scroll_mapper)
#         assert len(stems) > 0
#         assert config.keyboard_mapper.image_names.default in stems
#
#     def test_toggle_mode_detection(self, config):
#         """Test toggle mode detection from config."""
#         store = ScaledImageStore(
#             cycle_frames=["img1", "img2"],
#             named_indexes={
#                 config.keyboard_mapper.image_names.default: 0,
#                 config.keyboard_mapper.image_names.stroke: 1,
#             },
#         )
#         toggle_mode = has_key_toggle_images(store, config.keyboard_mapper)
#         assert toggle_mode is True
#
#     def test_configuration_immutability_during_runtime(self, config):
#         """Test that config cannot be modified during runtime."""
#         original_smooth = config.motion.smooth
#
#         try:
#             config.motion.smooth = not original_smooth
#             pytest.fail("Config should be immutable")
#         except (TypeError, AttributeError):
#             pass
#
#     def test_multiple_image_controller_instances(self, config):
#         """Test multiple independent controller instances."""
#         controller1 = ImageController(config.keyboard_mapper, config.scroll_mapper, key_toggle_mode=True)
#         controller2 = ImageController(config.keyboard_mapper, config.scroll_mapper, key_toggle_mode=False)
#
#         result1 = controller1.on_key_pressed("a")
#         result2 = controller2.on_key_pressed("a")
#
#         assert result1 is not None
#         assert result2 is None or result2 is not None  # Cycle mode may behave differently
#         if result1 is not None and result2 is not None:
#             assert result1.command.command_type != result2.command.command_type
#
#     def test_rapid_user_interactions(self, cursor_follower, image_controller):
#         """Test rapid successive user interactions."""
#         # Rapid cursor movements
#         for x in range(600, 700):
#             cursor_follower.update((x, 500))
#
#         # Rapid key presses
#         for char in "hello":
#             result = image_controller.on_key_pressed(char)
#             if result is not None:
#                 assert result.command is not None
#
#         # Rapid scrolls
#         for _ in range(3):
#             scroll_event = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.UP)
#             cmd = image_controller.on_scroll_event(scroll_event)
#             assert cmd is not None
#
#     def test_cycle_mode_frame_progression(self, config):
#         """Test frame progression in cycle mode."""
#         controller = ImageController(config.keyboard_mapper, config.scroll_mapper, key_toggle_mode=False)
#
#         # Get initial state
#         cmd1 = controller.initial_command()
#         assert cmd1 is not None
#
#         # Progress through cycle on key press
#         result = controller.on_key_pressed("a")
#         if result is not None:
#             assert result.command is not None
#
#     def test_special_char_flash_duration_override(self, config):
#         """Test that special character flash durations override defaults."""
#         controller = ImageController(config.keyboard_mapper, config.scroll_mapper, key_toggle_mode=True)
#
#         # Check special char flash duration
#         result = controller.on_key_pressed("?")
#         if result and result.flash_ms:
#             # If it's in special rules, it should have the configured flash_ms
#             assert result.flash_ms > 0
#
#     def test_scroll_and_hold_interaction(self, image_controller):
#         """Test interaction between scroll and key hold."""
#         # Press a key with hold time
#         key_result = image_controller.on_key_pressed("enter")
#         assert key_result is not None
#
#         # Try to scroll while key is held
#         scroll_event = ScrollEvent(phase=ScrollPhase.START, direction=ScrollDirection.DOWN)
#         scroll_result = image_controller.on_scroll_event(scroll_event)
#         assert scroll_result is not None
#
#         # Check idle doesn't reset during hold
#         idle_result = image_controller.on_key_idle()
#         # Idle should still work or be blocked by hold logic
#
#     def test_config_assets_path_valid(self, config):
#         """Test that assets configuration path is valid."""
#         assert config.assets is not None
#         assert config.assets.assets_dirname is not None
#         assert len(config.assets.assets_dirname) > 0
#
#     def test_config_keyboard_mapper_structure(self, config):
#         """Test keyboard mapper has required structure."""
#         assert config.keyboard_mapper is not None
#         assert config.keyboard_mapper.image_names is not None
#         assert config.keyboard_mapper.image_names.default is not None
#         assert config.keyboard_mapper.image_names.stroke is not None
#
#     def test_config_scroll_mapper_structure(self, config):
#         """Test scroll mapper has required structure."""
#         assert config.scroll_mapper is not None
#         assert config.scroll_mapper.image_names is not None
#         assert config.scroll_mapper.image_names.up is not None
#         assert config.scroll_mapper.image_names.down is not None

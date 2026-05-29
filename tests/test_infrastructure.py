# """Tests for infrastructure modules."""
#
# from __future__ import annotations
#
# import pytest
#
# from src.services.image_storage import (
#     ScaledImageStore,
#     build_key_image_stems,
#     has_key_toggle_images,
# )
# from mappers.keyboard_mapper import KeyboardMapper, KeyboardImageNames, SpecialCharRule
# from mappers.scroll_mapper import ScrollMapper, ScrollImageNames
#
#
# class TestBuildKeyImageStems:
#     """Test build_key_image_stems function."""
#
#     @pytest.fixture
#     def keyboard_mapper(self) -> KeyboardMapper:
#         """Create keyboard mapper for testing."""
#         image_names = KeyboardImageNames(
#             default="k_default",
#             stroke="k_stroke",
#             special_punct="k_special_punct",
#             comma="k_comma",
#             enter="k_enter",
#             esc="k_esc",
#             backspace="k_backspace",
#         )
#         return KeyboardMapper(
#             image_names=image_names,
#             special_char_rules={
#                 "?": SpecialCharRule(image_name=image_names.special_punct, flash_ms=500),
#                 "!": SpecialCharRule(image_name=image_names.special_punct, flash_ms=500),
#                 ".": SpecialCharRule(image_name=image_names.comma, flash_ms=500),
#             },
#             key_hold_ms_rules={"enter": 700},
#             key_press_count_limit=1,
#             default_flash_ms=200,
#         )
#
#     @pytest.fixture
#     def scroll_mapper(self) -> ScrollMapper:
#         """Create scroll mapper for testing."""
#         image_names = ScrollImageNames(up="m_scroll_up", down="m_scroll_down")
#         return ScrollMapper(image_names=image_names)
#
#     def test_includes_default_and_stroke(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper):
#         """Test that default and stroke are included."""
#         stems = build_key_image_stems(keyboard_mapper, scroll_mapper)
#         assert keyboard_mapper.image_names.default in stems
#         assert keyboard_mapper.image_names.stroke in stems
#
#     def test_includes_scroll_images(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper):
#         """Test that scroll images are included."""
#         stems = build_key_image_stems(keyboard_mapper, scroll_mapper)
#         assert scroll_mapper.image_names.up in stems
#         assert scroll_mapper.image_names.down in stems
#
#     def test_includes_special_char_rules(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper):
#         """Test that special character rule images are included."""
#         stems = build_key_image_stems(keyboard_mapper, scroll_mapper)
#         assert keyboard_mapper.image_names.special_punct in stems
#         assert keyboard_mapper.image_names.comma in stems
#
#     def test_returns_frozenset(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper):
#         """Test that returns immutable frozenset."""
#         stems = build_key_image_stems(keyboard_mapper, scroll_mapper)
#         assert isinstance(stems, frozenset)
#
#     def test_no_duplicates(self, keyboard_mapper: KeyboardMapper, scroll_mapper: ScrollMapper):
#         """Test that result has no duplicates."""
#         stems = build_key_image_stems(keyboard_mapper, scroll_mapper)
#         stems_list = list(stems)
#         assert len(stems_list) == len(set(stems_list))
#
#
# class TestScaledImageStore:
#     """Test ScaledImageStore dataclass."""
#
#     def test_scaled_image_store_creation(self):
#         """Test creating ScaledImageStore."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={})
#         assert store.cycle_frames == []
#         assert store.named_indexes == {}
#
#     def test_has_named_empty_store(self):
#         """Test has_named on empty store."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={})
#         assert store.has_named("k_default") is False
#
#     def test_has_named_existing(self):
#         """Test has_named with existing name."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={"k_default": 0})
#         assert store.has_named("k_default") is True
#
#     def test_index_of_empty_store(self):
#         """Test index_of on empty store."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={})
#         assert store.index_of("k_default") is None
#
#     def test_index_of_existing(self):
#         """Test index_of with existing name."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={"k_default": 5})
#         assert store.index_of("k_default") == 5
#
#     def test_frame_of_empty_store(self):
#         """Test frame_of on empty store."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={})
#         assert store.frame_of("k_default") is None
#
#     def test_frame_of_missing_name(self):
#         """Test frame_of with name not in named_indexes."""
#         store = ScaledImageStore(cycle_frames=["frame1", "frame2"], named_indexes={})
#         assert store.frame_of("k_default") is None
#
#     def test_scaled_image_store_frozen(self):
#         """Test that ScaledImageStore is frozen."""
#         store = ScaledImageStore(cycle_frames=[], named_indexes={})
#         with pytest.raises(AttributeError):
#             store.cycle_frames = ["frame"]
#
#
# class TestHasKeyToggleImages:
#     """Test has_key_toggle_images function."""
#
#     @pytest.fixture
#     def keyboard_mapper(self) -> KeyboardMapper:
#         """Create keyboard mapper for testing."""
#         image_names = KeyboardImageNames(
#             default="k_default",
#             stroke="k_stroke",
#             special_punct="k_punct",
#             comma="k_comma",
#             enter="k_enter",
#             esc="k_esc",
#             backspace="k_backspace",
#         )
#         return KeyboardMapper(
#             image_names=image_names,
#             special_char_rules={},
#             key_hold_ms_rules={},
#             key_press_count_limit=1,
#             default_flash_ms=200,
#         )
#
#     def test_has_both_required_images(self, keyboard_mapper: KeyboardMapper):
#         """Test when both default and stroke images exist."""
#         store = ScaledImageStore(
#             cycle_frames=["default", "stroke"],
#             named_indexes={"k_default": 0, "k_stroke": 1},
#         )
#         assert has_key_toggle_images(store, keyboard_mapper) is True
#
#     def test_missing_default_image(self, keyboard_mapper: KeyboardMapper):
#         """Test when default image is missing."""
#         store = ScaledImageStore(
#             cycle_frames=["stroke"],
#             named_indexes={"k_stroke": 0},
#         )
#         assert has_key_toggle_images(store, keyboard_mapper) is False
#
#     def test_missing_stroke_image(self, keyboard_mapper: KeyboardMapper):
#         """Test when stroke image is missing."""
#         store = ScaledImageStore(
#             cycle_frames=["default"],
#             named_indexes={"k_default": 0},
#         )
#         assert has_key_toggle_images(store, keyboard_mapper) is False
#
#     def test_missing_both_images(self, keyboard_mapper: KeyboardMapper):
#         """Test when both images are missing."""
#         store = ScaledImageStore(
#             cycle_frames=[],
#             named_indexes={},
#         )
#         assert has_key_toggle_images(store, keyboard_mapper) is False

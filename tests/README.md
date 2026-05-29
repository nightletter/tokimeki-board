"""Test suite for TOKIMEKI BOARD."""

# Tests Directory

This directory contains comprehensive unit and integration tests for the TOKIMEKI BOARD application.

## Running Tests

### Run all tests
```bash
uv run pytest tests/ -v
```

### Run tests with coverage report
```bash
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Run specific test file
```bash
uv run pytest tests/test_cursor_follow.py -v
```

### Run specific test class or function
```bash
uv run pytest tests/test_cursor_follow.py::TestCursorFollower::test_initialization -v
```

### Run tests matching a pattern
```bash
uv run pytest tests/ -k "image" -v
```

## Test Structure

### `test_config.py`
Tests for configuration module:
- ImageNames, MotionConfig, TimingConfig, KeyboardConfig, etc.
- Configuration immutability
- Default configuration values

### `test_cursor_follow.py`
Tests for cursor following logic:
- Smooth movement interpolation
- Snap threshold behavior
- Offset application
- Position tracking and change detection

### `test_image_flow.py`
Tests for character expression state machine:
- Toggle mode and cycle mode
- Key press handling and special characters
- Scroll event handling
- State transitions

### `test_domain_models.py`
Tests for domain models:
- CursorState, KeyToggleState, KeyHoldState
- State mutability and property updates

### `test_input_events.py`
Tests for input event interfaces:
- ScrollPhase and ScrollDirection enums
- ScrollEvent and KeyEvent dataclasses
- Event equality and immutability

### `test_infrastructure.py`
Tests for infrastructure modules:
- Image stem building
- ScaledImageStore functionality
- Key toggle image detection

### `test_integration.py`
Integration tests for core application flow:
- Cursor following with expression changes
- Key presses and scroll events
- State management across components
- Configuration-driven behavior

## Test Fixtures

Shared fixtures are defined in `conftest.py`:
- `sample_cursor_position` - Default cursor position for tests
- `sample_cursor_offset` - Default cursor offset for tests
- `test_assets_dir` - Temporary directory for test assets

## Coverage

Current test coverage: **112 tests**, covering:
- Configuration and constants (23 tests)
- Cursor following logic (10 tests)
- Image expression control (20 tests)
- Domain models (13 tests)
- Input events (17 tests)
- Infrastructure modules (14 tests)
- Integration scenarios (15 tests)

## Writing New Tests

When adding new functionality, follow these conventions:

1. **Test file naming**: `test_<module_name>.py`
2. **Test class naming**: `Test<ComponentName>`
3. **Test method naming**: `test_<specific_behavior>`
4. **Use fixtures**: Define reusable test data in fixtures
5. **Test organization**: Group related tests in classes
6. **Assertions**: Be specific about what you're testing

### Example test structure:
```python
class TestMyComponent:
    @pytest.fixture
    def my_component(self):
        """Create component for testing."""
        return MyComponent(config)

    def test_specific_behavior(self, my_component):
        """Test that component behaves correctly."""
        result = my_component.do_something()
        assert result == expected_value
```

## CI/CD

Tests can be run in CI/CD pipelines with:
```bash
uv run pytest tests/ -v --tb=short --junit-xml=test-results.xml
```

The `--junit-xml` flag generates a test report compatible with most CI systems.

# Copilot Instructions for TOKIMEKI BOARD

## Project Overview

TOKIMEKI BOARD is a desktop application featuring an anime character that follows your mouse cursor and reacts to keyboard input. Built with Python, PyQt6, and pynput, it creates a delightful overlay window experience on Windows and macOS.

## Getting Started

### Install Dependencies
```bash
uv sync
```

### Run in Development
```bash
uv run main.py
```

### Run Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=src --cov-report=term

# Run specific test
uv run pytest tests/test_cursor_follow.py -v
```

### Build for macOS
```bash
chmod +x scripts/build_macos.sh
TARGET_ARCH=arm64 ./scripts/build_macos.sh  # for Apple Silicon
# or
TARGET_ARCH=x64 ./scripts/build_macos.sh    # for Intel
```

### Build for Windows
```bash
scripts\build_windows.ps1  # Run from PowerShell
```

## Architecture

The application follows a **3-layer modular architecture** for simplicity and clarity:

### Layer Structure

1. **Core** (`src/core/`) - Data models and state management
   - `models.py`: Mutable state objects (`CursorState`, `KeyToggleState`, `KeyHoldState`) for runtime state management
   
2. **Services** (`src/services/`) - Business logic and application features
   - `cursor_follower.py`: Smooth cursor tracking with configurable motion physics
   - `image_controller.py`: State machine for character expression changes based on user input
   - `image_storage.py`: Cached image loading and asset management
   - `asset_loader.py`: Asset discovery and path resolution
   - `input_handler.py`: Input event handling (keyboard and mouse listeners)
   
3. **UI** (`src/ui/`) - Presentation and user interface
   - `overlay_window.py`: Main Qt widget that coordinates all systems
   - `qt_renderer.py`: Image rendering via PyQt6
   - `system_tray.py`: System tray integration for app control
   - `permissions.py`: Platform-specific permission handling (macOS accessibility)

4. **Events** (`src/events.py`) - Shared event definitions
   - `KeyEvent`, `ScrollEvent`: Immutable frozen dataclasses for event data integrity

### Data Flow
1. **Input Detection**: Keyboard and mouse listeners (via pynput) capture global input and emit events
2. **Event Processing**: Events are converted to `KeyEvent`/`ScrollEvent` and processed by services
3. **State Update**: Input triggers state changes in `ImageController` and `CursorFollower`
4. **Rendering**: Qt timer-based animation loop updates the overlay window based on current state

### Key Components

**OverlayWindow** - Orchestrates all systems:
- Manages cursor following (smooth tracking with physics)
- Coordinates character expression changes
- Handles input events (keyboard presses, mouse scrolling)
- Integrates system tray for app control

**ImageController** - Expression state machine:
- Maps user input to character expressions (animations/static images)
- Handles timing (flash durations, hold durations, image change intervals)
- Special rules for punctuation (?, !, .), enter, esc, backspace

**CursorFollower** - Smooth motion physics:
- Interpolates character position toward cursor with configurable smoothing
- Snaps to cursor position when distance exceeds threshold

## Configuration

Modify behavior in `src/config.py` - all configurable values are in `default_config()`:

- **Motion**: Cursor following offset, smoothing factor, snap threshold (in `MotionConfig`)
- **Timing**: Poll interval (8ms), image change duration (5s), scroll flash duration (500ms) (in `TimingConfig`)
- **Keyboard**: Key press limits, flash durations, special character rules, hold durations (in `KeyboardConfig`)
- **Assets**: Image directory structure, supported image formats (PNG, JPG, GIF, WebP, BMP) (in `AssetsConfig`)
- **Image Names**: Maps expression types to image file stem names (in `ImageNames`)

All configs use frozen dataclasses for immutability and safety.

## Key Conventions

### Module Organization
- **`src/core/`**: Data models only - no business logic
- **`src/services/`**: Pure business logic, decoupled from UI
- **`src/ui/`**: Qt-specific code, presentation layer only
- **`src/events.py`**: Shared event types used across layers

### Platform Handling
- **macOS**: Requires accessibility permissions (prompted at startup if needed)
- **Windows**: No special permissions required
- Platform-specific code is clearly marked with `sys.platform` checks

### Asset Loading
- Images are discovered by **stem name** (prefix before file extension)
- Supports animation sequences by frame naming: `k_stroke_0.png`, `k_stroke_1.png`, etc.
- Fallback to static images if animation sequence incomplete

### Input Backend Selection
- Dynamically imported from `src.services.input_handler` (keyboard and mouse functions)
- Allows swapping implementations without modifying core logic

### Frozen vs Mutable Dataclasses
- **Frozen**: Configuration objects (`ImageNames`, `AppConfig`, sub-configs, `KeyEvent`, `ScrollEvent`)
  - Immutability ensures runtime safety
  - Cannot be accidentally modified
- **Mutable**: State objects (`CursorState`, `KeyToggleState`, `KeyHoldState`)
  - Updated during runtime as events occur
  - Facilitate efficient state management

## Common Tasks

### Add a New Character Expression
1. Add image stem name to `ImageNames` in `config.py` (e.g., `happy="k_happy"`)
2. Add corresponding images to `assets/images/` with that stem (e.g., `k_happy.png` or `k_happy_0.png`, `k_happy_1.png`, etc.)
3. Update `ImageController` logic to reference the new expression via `image_names` or add special input rule in `KeyboardConfig`

### Adjust Character Motion
- Modify `MotionConfig` in `default_config()`:
  - `smooth`: 0.0 (instant) to 1.0 (very smooth) - lower values = faster movement
  - `offset_x`, `offset_y`: Pixel offset from cursor position
  - `snap_threshold`: Distance before position snaps to cursor

### Add Input Reaction
- Add input mapping in `ImageController._next_image_for_key()` or special rules
- Define timing rules in `KeyboardConfig.special_char_rules` for punctuation or `key_hold_ms_rules` for key holds
- Test with `test_image_flow.py` to verify state machine behavior

### Write and Run Tests
1. Create test file in `tests/` following naming convention: `test_<module>.py`
2. Use pytest fixtures for reusable test data (shared fixtures in `tests/conftest.py`)
3. Import from new paths: `from src.core.models import ...`, `from src.services import ...`, `from src.events import ...`
4. Run tests with `uv run pytest tests/ -v`
5. Check coverage with `uv run pytest tests/ --cov=src --cov-report=term`

Test structure:
- Unit tests for individual services (models, utilities, business logic)
- Integration tests for component interactions
- Fixtures in `tests/conftest.py` for shared test data
- 112 tests covering core functionality with ~90% code coverage

## Dependencies

- **PyQt6**: Desktop UI framework
- **pynput**: Global input listening (keyboard/mouse)
- **Pillow**: Image processing
- **PyInstaller**: Building standalone executables
- **pyobjc-\***: macOS-specific system integration (installed conditionally)

## Building and Releasing

- Builds use **PyInstaller** to create standalone executables
- Platform-specific build scripts handle icon conversion, app bundling
- CI/CD via GitHub Actions for automated Windows builds
- macOS builds currently manual (scripts available for local building)
- Releases generated with tagged version (see `APP_VERSION` in workflow)

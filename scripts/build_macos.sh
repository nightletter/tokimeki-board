#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

APP_NAME="TOKIMEKI BOARD"
BUNDLE_NAME="$APP_NAME"
BUNDLE_ID="com.nightletter.tokimeki-board"
CURRENT_ARCH=$(uname -m)

rm -rf build dist .venv
mkdir -p build dist

python3 -m pip install --upgrade pip >/dev/null
python3 -m pip install -e ".[dev]" 2>/dev/null || python3 -m pip install -e . >/dev/null || true

ICON_PNG="${ROOT_DIR}/assets/icon.png"
ICON_ICNS="${ROOT_DIR}/build/${BUNDLE_NAME}.icns"
ICON_ARGS=()

if [[ -f "$ICON_PNG" ]]; then
  ICONSET_DIR="${ROOT_DIR}/build/icon.iconset"
  rm -rf "$ICONSET_DIR" && mkdir -p "$ICONSET_DIR"
  for size in 16 32 128 256 512; do
    sips -z "$size" "$size" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
    sips -z "$((size * 2))" "$((size * 2))" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
  done
  iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"
  ICON_ARGS=(--icon "$ICON_ICNS")
fi

VENV_DIR="${ROOT_DIR}/.venv"
python3 -m venv "$VENV_DIR"
PY_BIN="${VENV_DIR}/bin/python"

"$PY_BIN" -m pip install --upgrade pip
"$PY_BIN" -m pip install pyinstaller pyinstaller-hooks-contrib pillow
"$PY_BIN" -m pip install -e ".[dev]" 2>/dev/null || "$PY_BIN" -m pip install -e . || true

"$PY_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --specpath "${ROOT_DIR}/build/spec" \
  --workpath "${ROOT_DIR}/build/work" \
  --distpath "${ROOT_DIR}/dist" \
  --windowed \
  --name "$BUNDLE_NAME" \
  --osx-bundle-identifier "$BUNDLE_ID" \
  "${ICON_ARGS[@]:-}" \
  --add-data "${ROOT_DIR}/assets:assets" \
  --add-data "${ROOT_DIR}/version.json:." \
  main.py

APP_BUNDLE_PATH="${ROOT_DIR}/dist/${BUNDLE_NAME}.app"

INFO_PLIST="${APP_BUNDLE_PATH}/Contents/Info.plist"
if [[ -f "$INFO_PLIST" ]]; then
  plutil -replace CFBundleDisplayName -string "$APP_NAME" "$INFO_PLIST"
  plutil -replace CFBundleName        -string "$APP_NAME" "$INFO_PLIST"
  plutil -replace CFBundleIdentifier  -string "$BUNDLE_ID" "$INFO_PLIST"
  plutil -replace LSUIElement         -string "1"         "$INFO_PLIST"
fi

MAIN_BIN="${APP_BUNDLE_PATH}/Contents/MacOS/${BUNDLE_NAME}"
[[ -f "$MAIN_BIN" ]] && lipo -info "$MAIN_BIN"

rm -rf "${ROOT_DIR}/build" "${ROOT_DIR}/.venv"

echo '✅ build success ✅'

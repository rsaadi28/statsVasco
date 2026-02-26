#!/usr/bin/env bash
set -euo pipefail

APP_FULL="StatsVasco.app"
APP_DEMO="StatsVascoDemo.app"
VOL_FULL="StatsVasco Full Installer"
VOL_DEMO="StatsVasco Demo Installer"
DMG_FULL="StatsVasco-Full.dmg"
DMG_DEMO="StatsVasco-Demo.dmg"

TARGET_ARCH="${TARGET_ARCH:-native}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SIGN_APP="${SIGN_APP:-0}"
SIGN_DMG="${SIGN_DMG:-0}"
NOTARIZE="${NOTARIZE:-0}"
CODESIGN_IDENTITY="${CODESIGN_IDENTITY:-}"
ENTITLEMENTS_FILE="${ENTITLEMENTS_FILE:-}"
NOTARYTOOL_PROFILE="${NOTARYTOOL_PROFILE:-}"
APPLE_ID="${APPLE_ID:-}"
APPLE_TEAM_ID="${APPLE_TEAM_ID:-}"
APPLE_APP_PASSWORD="${APPLE_APP_PASSWORD:-}"

TARGET_ARCH_PYI=""
case "$TARGET_ARCH" in
  native|"")
    TARGET_ARCH_PYI=""
    ;;
  x86_64|arm64|universal2)
    TARGET_ARCH_PYI="$TARGET_ARCH"
    ;;
  *)
    echo "TARGET_ARCH inválido: $TARGET_ARCH (use: native, x86_64, arm64, universal2)" >&2
    exit 1
    ;;
esac

require_cmd() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Comando obrigatório não encontrado: $cmd" >&2
    exit 1
  }
}

codesign_app() {
  local app_path="$1"

  [ "$SIGN_APP" = "1" ] || return 0
  [ -n "$CODESIGN_IDENTITY" ] || {
    echo "SIGN_APP=1 exige CODESIGN_IDENTITY." >&2
    exit 1
  }

  require_cmd codesign
  echo "Assinando app: $app_path"
  if [ -n "$ENTITLEMENTS_FILE" ]; then
    codesign \
      --force \
      --deep \
      --options runtime \
      --timestamp \
      --entitlements "$ENTITLEMENTS_FILE" \
      --sign "$CODESIGN_IDENTITY" \
      "$app_path"
  else
    codesign \
      --force \
      --deep \
      --options runtime \
      --timestamp \
      --sign "$CODESIGN_IDENTITY" \
      "$app_path"
  fi
  codesign --verify --deep --strict --verbose=2 "$app_path"
}

codesign_dmg() {
  local dmg_path="$1"

  [ "$SIGN_DMG" = "1" ] || return 0
  [ -n "$CODESIGN_IDENTITY" ] || {
    echo "SIGN_DMG=1 exige CODESIGN_IDENTITY." >&2
    exit 1
  }

  require_cmd codesign
  echo "Assinando DMG: $dmg_path"
  codesign --force --timestamp --sign "$CODESIGN_IDENTITY" "$dmg_path"
  codesign --verify --verbose=2 "$dmg_path"
}

notarize_file() {
  local file_path="$1"

  [ "$NOTARIZE" = "1" ] || return 0
  require_cmd xcrun

  echo "Notarizando: $file_path"
  if [ -n "$NOTARYTOOL_PROFILE" ]; then
    xcrun notarytool submit "$file_path" --keychain-profile "$NOTARYTOOL_PROFILE" --wait
  else
    [ -n "$APPLE_ID" ] || { echo "NOTARIZE=1 exige NOTARYTOOL_PROFILE ou APPLE_ID." >&2; exit 1; }
    [ -n "$APPLE_TEAM_ID" ] || { echo "NOTARIZE=1 exige APPLE_TEAM_ID." >&2; exit 1; }
    [ -n "$APPLE_APP_PASSWORD" ] || { echo "NOTARIZE=1 exige APPLE_APP_PASSWORD." >&2; exit 1; }
    xcrun notarytool submit "$file_path" \
      --apple-id "$APPLE_ID" \
      --team-id "$APPLE_TEAM_ID" \
      --password "$APPLE_APP_PASSWORD" \
      --wait
  fi

  xcrun stapler staple "$file_path"
  xcrun stapler validate "$file_path"
}

create_dmg_with_layout() {
  local app_name="$1"
  local vol_name="$2"
  local out_dmg="$3"
  local stage_dir
  local temp_dmg

  stage_dir="$(mktemp -d "/tmp/statsvasco-dmg-stage.XXXXXX")"
  temp_dmg="$(mktemp "/tmp/statsvasco-dmg-temp.XXXXXX.dmg")"

  cp -R "dist/$app_name" "$stage_dir/"
  ln -s /Applications "$stage_dir/Applications"

  hdiutil create \
    -srcfolder "$stage_dir" \
    -volname "$vol_name" \
    -fs HFS+ \
    -format UDRW \
    -ov \
    "$temp_dmg" >/dev/null

  if [ -d "/Volumes/$vol_name" ]; then
    hdiutil detach "/Volumes/$vol_name" -quiet || true
  fi

  hdiutil attach "$temp_dmg" -readwrite -noverify -noautoopen -quiet

  if command -v osascript >/dev/null 2>&1; then
    osascript <<EOF || true
tell application "Finder"
  tell disk "$vol_name"
    open
    tell container window
      set current view to icon view
      set toolbar visible to false
      set statusbar visible to false
      set bounds to {110, 90, 760, 500}
    end tell
    tell icon view options of container window
      -- Keep icons fixed on first click by pre-aligning to Finder grid.
      set arrangement to snap to grid
      set icon size to 144
      set text size to 13
    end tell
    set position of item "$app_name" of container window to {215, 205}
    set position of item "Applications" of container window to {515, 205}
    update
    delay 2
    close
    open
    delay 2
  end tell
end tell
EOF
  fi

  sync
  hdiutil detach "/Volumes/$vol_name" -quiet

  hdiutil convert "$temp_dmg" -format UDZO -imagekey zlib-level=9 -o "$out_dmg" -ov >/dev/null

  rm -rf "$stage_dir"
  rm -f "$temp_dmg"
}

echo "[1/4] Limpando builds antigas..."
rm -rf build dist
rm -f "$DMG_FULL" "$DMG_DEMO"

echo "[2/4] Gerando apps (Full e Demo)..."
require_cmd "$PYTHON_BIN"
"$PYTHON_BIN" -m PyInstaller --version >/dev/null

if [ -n "$TARGET_ARCH_PYI" ]; then
  export PYI_TARGET_ARCH="$TARGET_ARCH_PYI"
  echo "Arquitetura PyInstaller: $PYI_TARGET_ARCH"
fi

if [ "$SIGN_APP" = "1" ] && [ -n "$CODESIGN_IDENTITY" ]; then
  export PYI_CODESIGN_IDENTITY="$CODESIGN_IDENTITY"
fi

if [ -n "$ENTITLEMENTS_FILE" ]; then
  export PYI_ENTITLEMENTS_FILE="$ENTITLEMENTS_FILE"
fi

"$PYTHON_BIN" -m PyInstaller StatsVascoFull.spec
"$PYTHON_BIN" -m PyInstaller StatsVascoDemo.spec

codesign_app "dist/$APP_FULL"
codesign_app "dist/$APP_DEMO"

echo "[3/4] Gerando DMG da versão Full (layout customizado)..."
create_dmg_with_layout "$APP_FULL" "$VOL_FULL" "$DMG_FULL"
codesign_dmg "$DMG_FULL"
notarize_file "$DMG_FULL"

echo "[4/4] Gerando DMG da versão Demo (layout customizado)..."
create_dmg_with_layout "$APP_DEMO" "$VOL_DEMO" "$DMG_DEMO"
codesign_dmg "$DMG_DEMO"
notarize_file "$DMG_DEMO"

echo "Concluído."
echo "Apps:"
echo " - dist/$APP_FULL"
echo " - dist/$APP_DEMO"
echo "Instaladores:"
echo " - $DMG_FULL"
echo " - $DMG_DEMO"
echo "Config usada:"
echo " - TARGET_ARCH=${TARGET_ARCH}"
echo " - SIGN_APP=${SIGN_APP}"
echo " - SIGN_DMG=${SIGN_DMG}"
echo " - NOTARIZE=${NOTARIZE}"

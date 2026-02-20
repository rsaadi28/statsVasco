#!/usr/bin/env bash
set -euo pipefail

APP_FULL="StatsVasco.app"
APP_DEMO="StatsVascoDemo.app"
VOL_FULL="StatsVasco Full Installer"
VOL_DEMO="StatsVasco Demo Installer"
DMG_FULL="StatsVasco-Full.dmg"
DMG_DEMO="StatsVasco-Demo.dmg"

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
pyinstaller StatsVascoFull.spec
pyinstaller StatsVascoDemo.spec

echo "[3/4] Gerando DMG da versão Full (layout customizado)..."
create_dmg_with_layout "$APP_FULL" "$VOL_FULL" "$DMG_FULL"

echo "[4/4] Gerando DMG da versão Demo (layout customizado)..."
create_dmg_with_layout "$APP_DEMO" "$VOL_DEMO" "$DMG_DEMO"

echo "Concluído."
echo "Apps:"
echo " - dist/$APP_FULL"
echo " - dist/$APP_DEMO"
echo "Instaladores:"
echo " - $DMG_FULL"
echo " - $DMG_DEMO"

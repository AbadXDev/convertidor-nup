#!/bin/bash
# Compila Convertidor NUP.app y lo deja en el Escritorio (y en /Applications si se puede).
set -u
cd "$(dirname "$0")"
LOG="$HOME/Desktop/nup-app-build.log"
exec > >(tee -a "$LOG") 2>&1
echo "=== Build Convertidor NUP — $(date) ==="

APP="$HOME/Desktop/Convertidor NUP.app"
BIN="ConvertidorNUP"
SDK="$(xcrun --show-sdk-path)"
echo "SDK: $SDK"

rm -rf "$APP" /tmp/nupapp-build
mkdir -p /tmp/nupapp-build "$APP/Contents/MacOS" "$APP/Contents/Resources"

echo "Compilando…"
if ! swiftc -O -parse-as-library -sdk "$SDK" -target arm64-apple-macos13.0 main.swift -o "/tmp/nupapp-build/$BIN"; then
  echo "BUILD_FAILED (swiftc)"
  exit 1
fi
cp "/tmp/nupapp-build/$BIN" "$APP/Contents/MacOS/$BIN"
chmod +x "$APP/Contents/MacOS/$BIN"

# Icono (opcional: si falla, la app usa el icono generico)
ICON_KEY=""
if swift makeicon.swift /tmp/nupapp-build/icon-1024.png >>"$LOG" 2>&1; then
  ICONSET=/tmp/nupapp-build/AppIcon.iconset
  mkdir -p "$ICONSET"
  ok=1
  for spec in "16:icon_16x16" "32:icon_16x16@2x" "32:icon_32x32" "64:icon_32x32@2x" "128:icon_128x128" "256:icon_128x128@2x" "256:icon_256x256" "512:icon_256x256@2x" "512:icon_512x512" "1024:icon_512x512@2x"; do
    px="${spec%%:*}"; nm="${spec##*:}"
    sips -z "$px" "$px" /tmp/nupapp-build/icon-1024.png --out "$ICONSET/$nm.png" >/dev/null 2>&1 || ok=0
  done
  if [ "$ok" = 1 ] && iconutil -c icns "$ICONSET" -o "$APP/Contents/Resources/AppIcon.icns" 2>/dev/null; then
    ICON_KEY="<key>CFBundleIconFile</key><string>AppIcon</string>"
    echo "Icono OK"
  else
    echo "Icono omitido (iconutil fallo)"
  fi
else
  echo "Icono omitido (makeicon fallo)"
fi

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>CFBundleName</key><string>Convertidor NUP</string>
<key>CFBundleDisplayName</key><string>Convertidor NUP</string>
<key>CFBundleIdentifier</key><string>com.leonel.convertidornup</string>
<key>CFBundleVersion</key><string>1.0</string>
<key>CFBundleShortVersionString</key><string>1.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>$BIN</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
$ICON_KEY
<key>NSHumanReadableCopyright</key><string>By AbadXDev</string>
<key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

echo "Firmando (ad hoc)…"
codesign --force --deep --sign - "$APP"
codesign --verify --verbose=2 "$APP" && echo "Firma OK"

if cp -R "$APP" "/Applications/Convertidor NUP.app.tmp" 2>/dev/null; then
  rm -rf "/Applications/Convertidor NUP.app"
  mv "/Applications/Convertidor NUP.app.tmp" "/Applications/Convertidor NUP.app"
  echo "Tambien instalado en /Applications"
else
  rm -rf "/Applications/Convertidor NUP.app.tmp" 2>/dev/null
  echo "No se pudo copiar a /Applications (queda en el Escritorio)"
fi

echo "BUILD_OK: $APP"
du -sh "$APP"

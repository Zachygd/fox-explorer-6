#!/usr/bin/env bash
# Installs an unpacked Fox Explorer 6 tarball system-wide (any distro).
#   sudo ./foxexplorer6/foxexplorer/install.sh            -> /opt/foxexplorer6, /usr/local/bin
#   sudo ./foxexplorer6/foxexplorer/install.sh --uninstall
set -euo pipefail
APP_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${FE6_DEST:-/opt/foxexplorer6}"
PREFIX="${FE6_PREFIX:-/usr/local}"
if [ "${1:-}" = "--uninstall" ]; then
  rm -rf "$DEST" "$PREFIX/bin/foxexplorer6" "$PREFIX/share/applications/foxexplorer6.desktop" \
         "$PREFIX/share/metainfo/foxexplorer6.metainfo.xml"
  find "$PREFIX/share/icons/hicolor" -name 'foxexplorer6.*' -delete 2>/dev/null || true
  echo "Fox Explorer 6 removed. Your profile is left in ~/.mozilla/foxexplorer6."
  exit 0
fi
[ "$(id -u)" = 0 ] || { echo "Run with sudo to install into $DEST" >&2; exit 1; }
rm -rf "$DEST"
cp -a "$APP_SRC" "$DEST"
BIN=firefox; [ -x "$DEST/foxexplorer6" ] && BIN=foxexplorer6
install -d "$PREFIX/bin"
sed -e "s|@LIBDIR@|$DEST|" -e "s|@BINARY@|$BIN|" "$DEST/foxexplorer/foxexplorer6.sh.in" > "$PREFIX/bin/foxexplorer6"
chmod 0755 "$PREFIX/bin/foxexplorer6"
install -D -m 0644 "$DEST/foxexplorer/foxexplorer6.desktop" "$PREFIX/share/applications/foxexplorer6.desktop"
install -D -m 0644 "$DEST/foxexplorer/foxexplorer6.metainfo.xml" "$PREFIX/share/metainfo/foxexplorer6.metainfo.xml"
for s in 16 22 24 32 48 64 128 256; do
  install -D -m 0644 "$DEST/foxexplorer/appicons/foxexplorer6-$s.png" "$PREFIX/share/icons/hicolor/${s}x${s}/apps/foxexplorer6.png"
done
install -D -m 0644 "$DEST/foxexplorer/appicons/foxexplorer6.svg" "$PREFIX/share/icons/hicolor/scalable/apps/foxexplorer6.svg"
touch "$PREFIX/share/icons/hicolor" 2>/dev/null || true
command -v update-desktop-database >/dev/null && update-desktop-database -q "$PREFIX/share/applications" || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -t "$PREFIX/share/icons/hicolor" || true
echo "Fox Explorer 6 installed. Start it from your app menu or run: foxexplorer6"

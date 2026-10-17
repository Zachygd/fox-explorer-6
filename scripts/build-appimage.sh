#!/usr/bin/env bash
# Builds a portable Fox Explorer 6 AppImage from a packaged tarball.
#   scripts/build-appimage.sh dist/foxexplorer6-VERSION-ARCH.tar.xz
# (scripts/build-repack.sh --appimage runs this for you.)
#
# The AppImage runs on any recent x86_64/aarch64 Linux without installing anything. It uses the
# same profile as the installed version (~/.mozilla/foxexplorer6), so you can switch between them.
# appimagetool is downloaded from the AppImage project's GitHub releases the first time (or set
# APPIMAGETOOL=/path/to/appimagetool).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARBALL="$(realpath "${1:?usage: build-appimage.sh dist/foxexplorer6-VERSION-ARCH.tar.xz}")"
base="$(basename "$TARBALL" .tar.xz)"          # foxexplorer6-VERSION-ARCH
ARCH="${base##*-}"
VERSION="${base#foxexplorer6-}"; VERSION="${VERSION%-"$ARCH"}"

WORK="$HERE/work/appimage"
rm -rf "$WORK"; mkdir -p "$WORK"
APPDIR="$WORK/FoxExplorer6.AppDir"
mkdir -p "$APPDIR"
echo "==> unpacking $TARBALL"
tar -C "$APPDIR" -xf "$TARBALL"                 # -> $APPDIR/foxexplorer6/
APP="$APPDIR/foxexplorer6"
BIN=firefox; [ -x "$APP/foxexplorer6" ] && BIN=foxexplorer6

# the regular launcher (own profile, window class, square GTK frame), pointed inside the AppImage
sed -e 's|@LIBDIR@|$APPDIR/foxexplorer6|' -e "s|@BINARY@|$BIN|" \
    "$APP/foxexplorer/foxexplorer6.sh.in" > "$APPDIR/foxexplorer6-launcher"
chmod 0755 "$APPDIR/foxexplorer6-launcher"

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
# Fox Explorer 6 AppImage entry point
APPDIR="${APPDIR:-$(dirname "$(readlink -f "$0")")}"
export APPDIR
exec "$APPDIR/foxexplorer6-launcher" "$@"
EOF
chmod 0755 "$APPDIR/AppRun"

# desktop entry + icon at the top level, as the AppImage format expects
sed -e 's|^Exec=foxexplorer6|Exec=AppRun|' "$APP/foxexplorer/foxexplorer6.desktop" > "$APPDIR/foxexplorer6.desktop"
cp "$APP/foxexplorer/appicons/foxexplorer6-256.png" "$APPDIR/foxexplorer6.png"
ln -sf foxexplorer6.png "$APPDIR/.DirIcon"
mkdir -p "$APPDIR/usr/share/metainfo"
cp "$APP/foxexplorer/foxexplorer6.metainfo.xml" "$APPDIR/usr/share/metainfo/foxexplorer6.appdata.xml"

# appimagetool
TOOL="${APPIMAGETOOL:-}"
if [ -z "$TOOL" ]; then
  TOOL="$HERE/work/appimagetool-$ARCH.AppImage"
  if [ ! -x "$TOOL" ]; then
    echo "==> downloading appimagetool"
    curl -fL --progress-bar -o "$TOOL" \
      "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage"
    chmod +x "$TOOL"
  fi
fi

mkdir -p "$HERE/dist"
OUT="$HERE/dist/FoxExplorer6-$VERSION-$ARCH.AppImage"
rm -f "$HERE/dist"/FoxExplorer6-*-"$ARCH".AppImage
echo "==> building $(basename "$OUT")"
# --appimage-extract-and-run: works even where FUSE isn't available (containers, CI)
ARCH="$ARCH" "$TOOL" --appimage-extract-and-run --no-appstream "$APPDIR" "$OUT" >/dev/null
chmod +x "$OUT"
echo "$OUT"

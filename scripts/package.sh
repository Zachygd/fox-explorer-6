#!/usr/bin/env bash
# Turns a prepared Fox Explorer 6 app directory into dist/foxexplorer6-VERSION-ARCH.tar.xz
#   scripts/package.sh APP_DIR VERSION ARCH OUTDIR
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$1"; VERSION="$2"; ARCH="$3"; OUT="$4"
mkdir -p "$OUT"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -a "$APP" "$STAGE/foxexplorer6"
D="$STAGE/foxexplorer6"
install -d "$D/foxexplorer/appicons"
for s in 16 22 24 32 48 64 128 256; do
  install -m 0644 "$HERE/branding/foxexplorer/default$s.png" "$D/foxexplorer/appicons/foxexplorer6-$s.png"
done
# scalable icon: an SVG wrapping the logo, so desktops that prefer SVG pick up the new logo
B64="$(base64 -w0 "$HERE/branding/foxexplorer/default256.png")"
printf '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="256" height="256" viewBox="0 0 256 256"><image width="256" height="256" xlink:href="data:image/png;base64,%s"/></svg>\n' "$B64" > "$D/foxexplorer/appicons/foxexplorer6.svg"
install -m 0644 "$HERE/packaging/foxexplorer6.desktop" "$D/foxexplorer/foxexplorer6.desktop"
install -m 0644 "$HERE/packaging/foxexplorer6.metainfo.xml" "$D/foxexplorer/foxexplorer6.metainfo.xml"
install -m 0755 "$HERE/packaging/foxexplorer6.sh" "$D/foxexplorer/foxexplorer6.sh.in"
install -m 0755 "$HERE/scripts/install.sh" "$D/foxexplorer/install.sh"
install -m 0644 "$HERE/LICENSE" "$D/foxexplorer/LICENSE"
echo "$VERSION" > "$D/foxexplorer/VERSION"
TARBALL="$OUT/foxexplorer6-$VERSION-$ARCH.tar.xz"
tar -C "$STAGE" -cJf "$TARBALL" foxexplorer6
echo "$TARBALL"

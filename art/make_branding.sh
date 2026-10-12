#!/usr/bin/env bash
# Renders the Fox Explorer 6 branding overlay (icons + about-box art) from art/foxexplorer-logo.png
# into branding/foxexplorer/ and theme/fe6/icons/logo.png. Needs ImageMagick (sudo dnf install ImageMagick).
# The rendered PNGs are committed, so builds don't need this.
set -euo pipefail
cd "$(dirname "$0")/.."
B=branding/foxexplorer
SQ="$(mktemp --suffix=.png)"; trap 'rm -f "$SQ"' EXIT
# trim, then pad to a square so nothing is cropped
convert art/foxexplorer-logo.png -trim +repage -background none -gravity center \
        -extent "%[fx:max(w,h)]x%[fx:max(w,h)]" "$SQ" 2>/dev/null || \
convert art/foxexplorer-logo.png -trim +repage -background none -gravity center -extent 1360x1360 "$SQ"
sq() { convert "$SQ" -filter Lanczos -resize "${1}x${1}" -strip "$2"; }
sq 256 theme/fe6/icons/logo.png
for s in 16 22 24 32 48 64 128 256; do sq $s "$B/default$s.png"; done
sq 192 "$B/content/about-logo.png"
sq 384 "$B/content/about-logo@2x.png"
cp "$B/content/about-logo.png" "$B/content/about-logo-private.png"
cp "$B/content/about-logo@2x.png" "$B/content/about-logo-private@2x.png"
# about-logo.svg just wraps the PNG so every Firefox version finds the file it expects
B64="$(base64 -w0 "$B/content/about-logo@2x.png")"
printf '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="192" height="192" viewBox="0 0 192 192"><image width="192" height="192" xlink:href="data:image/png;base64,%s"/></svg>\n' "$B64" > "$B/content/about-logo.svg"
cat > "$B/content/about-wordmark.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="44" viewBox="0 0 300 44">
  <text x="0" y="33" font-family="Tahoma, 'Liberation Sans', Arial, sans-serif" font-size="30" font-weight="bold" fill="#000080">Fox Explorer<tspan fill="#ff8a1c" dx="8">6</tspan></text>
</svg>
SVG
cp "$B/content/about-wordmark.svg" "$B/content/firefox-wordmark.svg"
convert -background none "$B/content/about-wordmark.svg" "$B/content/about.png" 2>/dev/null || cp "$B/content/about-logo.png" "$B/content/about.png"
echo "branding art rendered into $B"

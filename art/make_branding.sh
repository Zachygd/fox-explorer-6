#!/usr/bin/env bash
# Renders the Fox Explorer 6 branding overlay (icons + about-box art) into branding/foxexplorer/.
# Needs rsvg-convert (Fedora: librsvg2-tools). The rendered PNGs are committed, so builds don't need this.
set -euo pipefail
cd "$(dirname "$0")/.."
B=branding/foxexplorer
EMB=theme/fe6/icons/foxexplorer.svg
for s in 16 22 24 32 48 64 128 256; do rsvg-convert -w $s -h $s "$EMB" -o "$B/default$s.png"; done
rsvg-convert -w 192 -h 192 "$EMB" -o "$B/content/about-logo.png"
rsvg-convert -w 384 -h 384 "$EMB" -o "$B/content/about-logo@2x.png"
cp "$B/content/about-logo.png" "$B/content/about-logo-private.png"
cp "$B/content/about-logo@2x.png" "$B/content/about-logo-private@2x.png"
cp "$EMB" "$B/content/about-logo.svg"
cat > "$B/content/about-wordmark.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="44" viewBox="0 0 300 44">
  <text x="0" y="33" font-family="Tahoma, 'Liberation Sans', Arial, sans-serif" font-size="30" font-weight="bold" fill="#000080">Fox Explorer<tspan fill="#ff8a1c" dx="8">6</tspan></text>
</svg>
SVG
cp "$B/content/about-wordmark.svg" "$B/content/firefox-wordmark.svg"
rsvg-convert -w 300 -h 44 "$B/content/about-wordmark.svg" -o "$B/content/about.png"
echo "branding art rendered into $B"

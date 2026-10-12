#!/usr/bin/env bash
# Installs the Fox Explorer 6 chrome layer (IE6 theme + autoconfig) into a Firefox
# installation directory — the folder that contains omni.ja and the firefox binary.
#   scripts/apply-layer.sh /path/to/firefox
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D="${1:?usage: apply-layer.sh FIREFOX_DIR}"
[ -f "$D/omni.ja" ] || { echo "error: $D doesn't look like a Firefox install (no omni.ja)" >&2; exit 1; }

rm -rf "$D/foxexplorer"
install -d "$D/foxexplorer"
cp -r "$HERE/theme/fe6/." "$D/foxexplorer/"
install -m 0644 "$HERE/autoconfig/foxexplorer.cfg" "$D/foxexplorer.cfg"
install -D -m 0644 "$HERE/autoconfig/defaults/pref/foxexplorer-prefs.js" "$D/defaults/pref/foxexplorer-prefs.js"
echo "Fox Explorer 6 layer installed into $D"

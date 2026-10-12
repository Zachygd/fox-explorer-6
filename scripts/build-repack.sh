#!/usr/bin/env bash
# Fox Explorer 6 — quick build from an official Mozilla Firefox release (about 2 minutes).
#
# Downloads the official Firefox Linux build from archive.mozilla.org, checks its
# SHA-512 (and Mozilla's GPG signature when gpg is installed), then:
#   1. swaps the branding to Fox Explorer 6        (scripts/rebrand-omni.py)
#   2. gives it its own profile + window class      (scripts/make-appini.py)
#   3. installs the IE6 / Windows 98 chrome layer   (scripts/apply-layer.sh)
#   4. turns off Mozilla's self-updater (re-run this script, or your RPM, to update)
#   5. packs dist/foxexplorer6-VERSION-ARCH.tar.xz and, with --rpm, a Fedora RPM.
#
# Usage:
#   scripts/build-repack.sh [--channel release|esr] [--version 158.0.1] [--lang en-US]
#                           [--from firefox-xxx.tar.xz|DIR] [--rpm] [--no-gpg]
#                           [--ie6-icons /path/to/IE6.iso]   (use the real IE6 icons from your own CD)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANNEL=release; VERSION=latest; LANG_CODE=en-US; FROM=""; RPM=0; GPG=1; IE6_MEDIA=""
while [ $# -gt 0 ]; do
  case "$1" in
    --channel) CHANNEL="$2"; shift 2;;
    --version) VERSION="$2"; shift 2;;
    --lang) LANG_CODE="$2"; shift 2;;
    --from) FROM="$2"; shift 2;;
    --rpm) RPM=1; shift;;
    --no-gpg) GPG=0; shift;;
    --ie6-icons) IE6_MEDIA="$2"; shift 2;;
    -h|--help) sed -n 2,17p "$0"; exit 0;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done

case "$(uname -m)" in
  x86_64) ARCH=x86_64; MOZARCH=linux-x86_64;;
  aarch64|arm64) ARCH=aarch64; MOZARCH=linux-aarch64;;
  *) echo "unsupported architecture $(uname -m) (Mozilla ships x86_64 and aarch64 Linux builds)" >&2; exit 1;;
esac

WORK="$HERE/work/repack"
rm -rf "$WORK"; mkdir -p "$WORK"
need() { command -v "$1" >/dev/null || { echo "missing tool: $1 (sudo dnf install $2)" >&2; exit 1; }; }
need python3 python3; need tar tar; need xz xz

if [ -z "$FROM" ]; then
  need curl curl
  if [ "$VERSION" = latest ]; then
    KEY=LATEST_FIREFOX_VERSION; [ "$CHANNEL" = esr ] && KEY=FIREFOX_ESR
    VERSION="$(curl -fsSL https://product-details.mozilla.org/1.0/firefox_versions.json |
               python3 -c "import json,sys; print(json.load(sys.stdin)['$KEY'])")"
  fi
  BASE="https://archive.mozilla.org/pub/firefox/releases/$VERSION"
  echo "==> Firefox $VERSION ($MOZARCH, $LANG_CODE)"
  curl -fsSL -o "$WORK/SHA512SUMS" "$BASE/SHA512SUMS"
  for ext in tar.xz tar.bz2; do
    REL="$MOZARCH/$LANG_CODE/firefox-$VERSION.$ext"
    if grep -q " $REL\$" "$WORK/SHA512SUMS"; then break; fi
  done
  grep -q " $REL\$" "$WORK/SHA512SUMS" || { echo "no Linux build listed for $VERSION" >&2; exit 1; }
  TARBALL="$WORK/$(basename "$REL")"
  curl -fL --progress-bar -o "$TARBALL" "$BASE/$REL"
  echo "==> checking SHA-512"
  WANT="$(grep " $REL\$" "$WORK/SHA512SUMS" | cut -d' ' -f1)"
  GOT="$(sha512sum "$TARBALL" | cut -d' ' -f1)"
  [ "$WANT" = "$GOT" ] || { echo "SHA-512 mismatch for $TARBALL" >&2; exit 1; }
  if [ "$GPG" = 1 ] && command -v gpg >/dev/null; then
    echo "==> checking Mozilla's GPG signature"
    export GNUPGHOME="$WORK/gnupg"; mkdir -m 700 -p "$GNUPGHOME"
    curl -fsSL -o "$WORK/KEY" "$BASE/KEY"
    curl -fsSL -o "$WORK/SHA512SUMS.asc" "$BASE/SHA512SUMS.asc"
    gpg -q --import "$WORK/KEY" 2>/dev/null
    # Mozilla Software Releases signing key
    MOZ_FPR="14F26682D0916CDD81E37B6D61B7B526D98F0353"
    STATUS="$(gpg --status-fd 1 --verify "$WORK/SHA512SUMS.asc" "$WORK/SHA512SUMS" 2>/dev/null || true)"
    if echo "$STATUS" | grep -q "VALIDSIG.*$MOZ_FPR"; then
      echo "    signature OK (Mozilla $MOZ_FPR)"
    else
      echo "GPG signature check failed — refusing to continue (use --no-gpg to skip if Mozilla rotated its key)" >&2; exit 1
    fi
    unset GNUPGHOME
  else
    echo "    (gpg not installed: SHA-512 checked, signature skipped)"
  fi
  tar -C "$WORK" -xf "$TARBALL"
elif [ -d "$FROM" ]; then
  cp -a "$FROM" "$WORK/firefox"
else
  tar -C "$WORK" -xf "$FROM"
fi

APP="$WORK/firefox"
[ -f "$APP/omni.ja" ] || { echo "no Firefox found in the archive" >&2; exit 1; }
if [ "$VERSION" = latest ]; then
  VERSION="$(sed -n 's/^Version=//p' "$APP/application.ini" | head -1)"
fi

echo "==> rebranding"
python3 "$HERE/scripts/rebrand-omni.py" "$APP" "$HERE/branding/foxexplorer"
python3 "$HERE/scripts/make-appini.py" "$APP"
echo "==> installing the IE6 chrome layer"
"$HERE/scripts/apply-layer.sh" "$APP"
if [ -n "$IE6_MEDIA" ]; then
  echo "==> importing IE6 icons from $IE6_MEDIA"
  python3 "$HERE/scripts/import-ie6-icons.py" "$IE6_MEDIA" "$APP/foxexplorer/ie6"
fi
install -D -m 0644 "$HERE/distribution/policies.json" "$APP/distribution/policies.json"
rm -f "$APP/updater" "$APP/updater.ini" "$APP/update-settings.ini"

echo "==> packaging"
TARBALL_OUT="$("$HERE/scripts/package.sh" "$APP" "$VERSION" "$ARCH" "$HERE/dist")"
echo "    $TARBALL_OUT"

if [ "$RPM" = 1 ]; then
  "$HERE/scripts/build-rpm.sh" "$TARBALL_OUT" "$VERSION"
fi
echo "Done."

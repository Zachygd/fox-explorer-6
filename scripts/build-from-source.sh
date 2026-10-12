#!/usr/bin/env bash
# Fox Explorer 6 — full build from Mozilla's Firefox source on GitHub.
#
#   scripts/build-from-source.sh [--branch release|beta|esr153|main] [--rpm] [--jobs N]
#                                [--ie6-icons /path/to/IE6.iso]
#
# Clones https://github.com/mozilla-firefox/firefox (shallow), adds the Fox Explorer 6
# branding as browser/branding/foxexplorer, compiles with packaging/mozconfig, then adds the
# IE6 chrome layer and packs dist/foxexplorer6-VERSION-ARCH.tar.xz (+ RPM with --rpm).
#
# Needs: ~16 GB RAM (8 GB + swap works, slowly), ~40 GB free disk, and 1–3 hours.
# First run installs Mozilla's toolchain with `./mach bootstrap` (asks for sudo for dnf packages).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="https://github.com/mozilla-firefox/firefox.git"
BRANCH=release; RPM=0; JOBS=""; IE6_MEDIA=""
while [ $# -gt 0 ]; do
  case "$1" in
    --branch) BRANCH="$2"; shift 2;;
    --rpm) RPM=1; shift;;
    --jobs) JOBS="$2"; shift 2;;
    --ie6-icons) IE6_MEDIA="$2"; shift 2;;
    -h|--help) sed -n 2,13p "$0"; exit 0;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
SRC="${FE6_SRC:-$HERE/work/firefox-src}"

mem_gb=$(awk '/MemTotal/ {printf "%d", $2/1048576}' /proc/meminfo)
disk_gb=$(df -Pk "$HERE" | awk 'NR==2 {printf "%d", $4/1048576}')
echo "==> machine: ${mem_gb} GB RAM, ${disk_gb} GB free disk"
if [ "$mem_gb" -lt 8 ]; then echo "warning: less than 8 GB RAM — linking libxul will likely fail" >&2; fi
if [ "$disk_gb" -lt 40 ]; then echo "warning: less than 40 GB free disk — the build may run out of space" >&2; fi

command -v git >/dev/null || { echo "install git first: sudo dnf install git" >&2; exit 1; }
if [ ! -d "$SRC/.git" ]; then
  echo "==> cloning $REPO ($BRANCH)"
  git clone --depth 1 --branch "$BRANCH" "$REPO" "$SRC"
else
  echo "==> updating $SRC ($BRANCH)"
  git -C "$SRC" fetch --depth 1 origin "$BRANCH"
  git -C "$SRC" checkout -f FETCH_HEAD
fi

echo "==> adding Fox Explorer 6 branding"
rm -rf "$SRC/browser/branding/foxexplorer"
cp -r "$SRC/browser/branding/unofficial" "$SRC/browser/branding/foxexplorer"
cp -r "$HERE/branding/foxexplorer/." "$SRC/browser/branding/foxexplorer/"
cp "$HERE/packaging/mozconfig" "$SRC/mozconfig"
if [ -n "$JOBS" ]; then echo "mk_add_options MOZ_PARALLEL_BUILD=$JOBS" >> "$SRC/mozconfig"; fi

cd "$SRC"
if [ ! -d "$HOME/.mozbuild" ]; then
  echo "==> first run: installing Mozilla's build toolchain (mach bootstrap)"
  ./mach --no-interactive bootstrap --application-choice "Firefox for Desktop"
fi
echo "==> building (this takes a while)"
./mach build
./mach package

PKG="$(ls -t obj-foxexplorer6/dist/foxexplorer6-*.tar.* | head -1)"
VERSION="$(cat browser/config/version_display.txt)"
case "$(uname -m)" in aarch64|arm64) ARCH=aarch64;; *) ARCH=x86_64;; esac
WORK="$HERE/work/source-stage"; rm -rf "$WORK"; mkdir -p "$WORK"
tar -C "$WORK" -xf "$PKG"
APP="$WORK/foxexplorer6"
echo "==> installing the IE6 chrome layer"
"$HERE/scripts/apply-layer.sh" "$APP"
if [ -n "$IE6_MEDIA" ]; then
  python3 "$HERE/scripts/import-ie6-icons.py" "$IE6_MEDIA" "$APP/foxexplorer/ie6"
fi
TARBALL_OUT="$("$HERE/scripts/package.sh" "$APP" "$VERSION" "$ARCH" "$HERE/dist")"
echo "    $TARBALL_OUT"
if [ "$RPM" = 1 ]; then "$HERE/scripts/build-rpm.sh" "$TARBALL_OUT" "$VERSION"; fi
echo "Done."

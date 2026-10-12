#!/usr/bin/env bash
# Builds a Fedora RPM from a Fox Explorer 6 tarball.
#   scripts/build-rpm.sh dist/foxexplorer6-VERSION-ARCH.tar.xz VERSION
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARBALL="$(realpath "$1")"; VERSION="$2"
command -v rpmbuild >/dev/null || { echo "rpmbuild missing: sudo dnf install rpm-build" >&2; exit 1; }
TOP="$HERE/work/rpmbuild"; rm -rf "$TOP"; mkdir -p "$TOP"/{SOURCES,SPECS,BUILD,RPMS,SRPMS}
cp "$TARBALL" "$TOP/SOURCES/"
RPMVER="${VERSION//-/.}"; RPMVER="${RPMVER//esr/}"
rpmbuild -bb "$HERE/packaging/foxexplorer6.spec" \
  --define "_topdir $TOP" \
  --define "fe_version $RPMVER" \
  --define "fe_tarball $(basename "$TARBALL")"
mkdir -p "$HERE/dist"
find "$TOP/RPMS" -name '*.rpm' -exec cp {} "$HERE/dist/" \; -print

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
# Mozilla's prebuilt libraries carry RUNPATHs Fedora's check-rpaths dislikes (see the spec)
export QA_RPATHS=$(( 0x0001 | 0x0002 | 0x0004 | 0x0008 | 0x0010 | 0x0020 ))
rpmbuild -bb "$HERE/packaging/foxexplorer6.spec" \
  --define "_topdir $TOP" \
  --define "fe_version $RPMVER" \
  --define "fe_release $(date +%Y%m%d%H%M)" \
  --define "fe_tarball $(basename "$TARBALL")"
mkdir -p "$HERE/dist"
# keep only the newest RPM in dist/, so "dnf install ./dist/foxexplorer6-*.rpm" can't pick an old one
rm -f "$HERE/dist"/foxexplorer6-*.rpm
find "$TOP/RPMS" -name '*.rpm' -exec cp {} "$HERE/dist/" \; -print
echo "Install or update with:  sudo dnf install $HERE/dist/foxexplorer6-*.rpm"

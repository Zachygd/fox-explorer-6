#!/usr/bin/env bash
# Prints the IE6 CD image to import icons from: the one given ($1), or the first found in the
# usual places. Prints nothing for "none" or when none is found (the build then keeps
# Fox Explorer's own icons).
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case "${1:-}" in
  none) exit 0;;
  "") ;;
  *) [ -e "$1" ] && { echo "$1"; exit 0; }; echo "IE6 media not found: $1" >&2; exit 0;;
esac
if ! command -v cabextract >/dev/null; then
  for f in "$HOME"/Downloads/*[Ii][Ee]6*.iso "$HOME"/*[Ii][Ee]6*.iso; do
    [ -e "$f" ] && { echo "note: found $f but cabextract isn't installed (sudo dnf install cabextract) — using Fox Explorer's own icons" >&2; break; }
  done
  exit 0
fi
shopt -s nullglob nocaseglob
for f in "$HOME/Downloads/IE6.iso" "$HOME/IE6.iso" "$HERE/IE6.iso" \
         "$HOME"/Downloads/*ie6*.iso "$HOME"/*ie6*.iso "$HERE"/*ie6*.iso; do
  [ -f "$f" ] && { echo "$f"; exit 0; }
done
exit 0

#!/usr/bin/env python3
"""Draw the Downloads button animation: theme/fe6/se98/downloading.png.

Like the Windows 98 download dialog, a page flies out of the globe, along the arrow and into
the folder. The frames are drawn over the SE98 download icon (theme/fe6/se98/downloads.png,
by nestoris, GPL-2.0), so the result is a modified SE98 icon under the same licence.

Usage: art/make_download_anim.py      (run after art/make_se98.py)
Writes a horizontal strip of 22x22 frames; fe6.css steps through it while a download runs.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SE98 = os.path.join(HERE, "..", "theme", "fe6", "se98")

# a 6x7 Win98 document: black outline, white paper, folded corner, two gray lines of "text"
PAGE = [
    "XXXXX.",
    "XWWWXX",
    "XWGGWX",
    "XWWWWX",
    "XWGGWX",
    "XWWWWX",
    "XXXXXX",
]
COLOURS = {"X": (0, 0, 0, 255), "W": (255, 255, 255, 255), "G": (128, 128, 128, 255)}
# top-left of the page in each frame: out of the globe, along the dashed arrow, down into the
# folder; then two frames with nothing flying so the loop has a beat between pages
PATH = [(7, 2), (10, 1), (13, 1), (15, 3), (15, 6), (15, 9), (15, 12), None, None]


def main():
    base = Image.open(os.path.join(SE98, "downloads.png")).convert("RGBA")
    w, h = base.size
    strip = Image.new("RGBA", (w * len(PATH), h), (0, 0, 0, 0))
    for i, pos in enumerate(PATH):
        frame = base.copy()
        if pos:
            px, py = pos
            for y, row in enumerate(PAGE):
                for x, ch in enumerate(row):
                    if ch in COLOURS and 0 <= px + x < w and 0 <= py + y < h:
                        frame.putpixel((px + x, py + y), COLOURS[ch])
        strip.paste(frame, (i * w, 0))
    out = os.path.join(SE98, "downloading.png")
    strip.save(out, optimize=True)
    print("wrote", os.path.normpath(out), f"({len(PATH)} frames)")


if __name__ == "__main__":
    main()

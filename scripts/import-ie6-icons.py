#!/usr/bin/env python3
"""Import the original Internet Explorer 6 toolbar and status-bar icons from YOUR OWN
IE6 installation media into a Fox Explorer 6 build.

    import-ie6-icons.py IE6.iso OUT_DIR

  IE6.iso   an IE6 setup CD image (or a folder holding its .CAB files)
  OUT_DIR   where to write the icons + ie6.css, normally
            <app>/foxexplorer/ie6  (build-repack.sh --ie6-icons does this for you), or
            /usr/lib64/foxexplorer6/foxexplorer/ie6 to update an installed copy (sudo).

The artwork is Microsoft's, so it is never stored in the Fox Explorer 6 repository or
packages made from it for sharing; this script only converts the files you already own,
on your own machine. Needs: python3 and cabextract (sudo dnf install cabextract).
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

# ------------------------------------------------------------------ ISO 9660 reader
def iso_files(path):
    """Yield (name, offset, size) for every file on an ISO 9660 image."""
    f = open(path, "rb")
    f.seek(16 * 2048)
    pvd = f.read(2048)
    if pvd[1:6] != b"CD001":
        raise SystemExit(f"{path} is not an ISO 9660 image")
    root = pvd[156:190]

    def walk(lba, size, prefix):
        f.seek(lba * 2048)
        data = f.read(size)
        p = 0
        while p < len(data):
            ln = data[p]
            if ln == 0:                     # records don't cross sector boundaries
                p = (p // 2048 + 1) * 2048
                continue
            rec = data[p:p + ln]
            ext = struct.unpack("<I", rec[2:6])[0]
            sz = struct.unpack("<I", rec[10:14])[0]
            flags = rec[25]
            nlen = rec[32]
            name = rec[33:33 + nlen]
            p += ln
            if name in (b"\x00", b"\x01"):
                continue
            name = name.decode("latin-1").split(";")[0]
            if flags & 2:
                yield from walk(ext, sz, prefix + name + "/")
            else:
                yield prefix + name, ext * 2048, sz

    yield from walk(struct.unpack("<I", root[2:6])[0], struct.unpack("<I", root[10:14])[0], "")


def collect_cabs(src, workdir):
    cabs = []
    if os.path.isdir(src):
        for n in os.listdir(src):
            if n.lower().endswith(".cab"):
                cabs.append(os.path.join(src, n))
        return cabs
    with open(src, "rb") as f:
        for name, off, size in iso_files(src):
            if name.lower().endswith(".cab"):
                out = os.path.join(workdir, os.path.basename(name))
                f.seek(off)
                with open(out, "wb") as o:
                    o.write(f.read(size))
                cabs.append(out)
    return cabs


def extract_dll(cabs, dll, workdir):
    """Pull one DLL out of whichever CAB has it (prefers the Win9x/IEMIL set)."""
    if not shutil.which("cabextract"):
        raise SystemExit("cabextract is needed: sudo dnf install cabextract")
    cabs = sorted(cabs, key=lambda c: (not os.path.basename(c).upper().startswith("IEMIL"), c))
    for cab in cabs:
        listing = subprocess.run(["cabextract", "-l", cab], capture_output=True, text=True).stdout.lower()
        if dll.lower() in listing:
            dest = os.path.join(workdir, "x_" + dll.lower())
            os.makedirs(dest, exist_ok=True)
            subprocess.run(["cabextract", "-q", "-F", dll, "-d", dest, cab], capture_output=True)
            for root, _, files in os.walk(dest):
                for n in files:
                    if n.lower() == dll.lower():
                        return open(os.path.join(root, n), "rb").read()
    raise SystemExit(f"{dll} not found in the IE6 media — is this an Internet Explorer 6 setup CD?")

# ------------------------------------------------------------------ PE resources
def pe_resources(data):
    """Return {(type, id): bytes} for every resource in a PE file."""
    pe = struct.unpack("<I", data[0x3C:0x40])[0]
    nsec = struct.unpack("<H", data[pe + 6:pe + 8])[0]
    optsz = struct.unpack("<H", data[pe + 20:pe + 22])[0]
    opt = pe + 24
    magic = struct.unpack("<H", data[opt:opt + 2])[0]
    ddir = opt + (96 if magic == 0x10B else 112)
    rva, _ = struct.unpack("<II", data[ddir + 2 * 8:ddir + 2 * 8 + 8])
    secs = []
    s = opt + optsz
    for i in range(nsec):
        vsize, vaddr, rsize, raddr = struct.unpack("<IIII", data[s + i * 40 + 8:s + i * 40 + 24])
        secs.append((vaddr, max(vsize, rsize), raddr))

    def off(r):
        for va, sz, ra in secs:
            if va <= r < va + sz:
                return r - va + ra
        raise ValueError("bad rva")

    base = off(rva)
    out = {}

    def entries(o):
        n_named, n_id = struct.unpack("<HH", data[o + 12:o + 16])
        for k in range(n_named + n_id):
            name, target = struct.unpack("<II", data[o + 16 + k * 8:o + 24 + k * 8])
            yield (None if name & 0x80000000 else name), target

    for typ, t1 in entries(base):
        if not t1 & 0x80000000:
            continue
        for rid, t2 in entries(base + (t1 & 0x7FFFFFFF)):
            if not t2 & 0x80000000:
                continue
            for _lang, t3 in entries(base + (t2 & 0x7FFFFFFF)):
                drva, dsize = struct.unpack("<II", data[base + t3:base + t3 + 8])
                if typ is not None and rid is not None:
                    out.setdefault((typ, rid), data[off(drva):off(drva) + dsize])
                break
    return out

# ------------------------------------------------------------------ DIB decoding / PNG writing
def decode_dib(dib, icon=False):
    """Decode a BITMAPINFOHEADER DIB to (w, h, rows of RGBA tuples). Icons: XOR+AND masks."""
    hsz, w, h, planes, bpp, comp = struct.unpack("<IiiHHI", dib[:20])
    ncolors = struct.unpack("<I", dib[32:36])[0]
    if comp not in (0, 1, 2, 3):
        raise ValueError(f"unsupported bitmap compression {comp}")
    if icon:
        h //= 2
    bottom_up = h > 0
    h = abs(h)
    pal_n = ncolors or (1 << bpp if bpp <= 8 else 0)
    pal = [tuple(dib[hsz + i * 4:hsz + i * 4 + 3][::-1]) for i in range(pal_n)]
    p = hsz + pal_n * 4 + (12 if comp == 3 else 0)
    if comp in (1, 2):                      # BI_RLE8 / BI_RLE4 -> expand to plain 8 bpp indices
        idx = rle_decode(dib[p:], w, h, 8 if comp == 1 else 4)
        rows = [[pal[i] + (255,) if i < len(pal) else (0, 0, 0, 255) for i in r] for r in idx]
        if bottom_up:
            rows.reverse()
        return w, h, rows
    stride = ((w * bpp + 31) // 32) * 4
    rows = []
    for y in range(h):
        row = dib[p + y * stride:p + (y + 1) * stride]
        px = []
        for x in range(w):
            if bpp == 32:
                b, g, r, a = row[x * 4:x * 4 + 4]
                px.append((r, g, b, a))
            elif bpp == 24:
                b, g, r = row[x * 3:x * 3 + 3]
                px.append((r, g, b, 255))
            elif bpp == 16:
                v = struct.unpack("<H", row[x * 2:x * 2 + 2])[0]
                px.append((((v >> 10) & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, (v & 31) * 255 // 31, 255))
            else:
                per = 8 // bpp
                byte = row[x // per]
                idx = (byte >> (8 - bpp * (x % per + 1))) & ((1 << bpp) - 1)
                r, g, b = pal[idx] if idx < len(pal) else (0, 0, 0)
                px.append((r, g, b, 255))
        rows.append(px)
    if icon and bpp < 32:
        mp = p + stride * h
        mstride = ((w + 31) // 32) * 4
        for y in range(h):
            m = dib[mp + y * mstride:mp + (y + 1) * mstride]
            for x in range(w):
                if (m[x // 8] >> (7 - x % 8)) & 1:
                    r, g, b, _ = rows[y][x]
                    rows[y][x] = (r, g, b, 0)
    if bottom_up:
        rows.reverse()
    return w, h, rows


def rle_decode(data, w, h, bits):
    """Decode BI_RLE8/BI_RLE4 into h rows (bottom-up order) of palette indices."""
    rows = [[0] * w for _ in range(h)]
    x = y = p = 0
    while p + 1 < len(data) and y < h:
        n, v = data[p], data[p + 1]
        p += 2
        if n:                                   # encoded run
            for k in range(n):
                c = v if bits == 8 else ((v >> 4) if k % 2 == 0 else (v & 15))
                if x < w:
                    rows[y][x] = c
                x += 1
        elif v == 0:                            # end of line
            x, y = 0, y + 1
        elif v == 1:                            # end of bitmap
            break
        elif v == 2:                            # delta
            x += data[p]; y += data[p + 1]; p += 2
        else:                                   # absolute run of v pixels
            nbytes = v if bits == 8 else (v + 1) // 2
            for k in range(v):
                if bits == 8:
                    c = data[p + k]
                else:
                    b = data[p + k // 2]
                    c = (b >> 4) if k % 2 == 0 else (b & 15)
                if x < w:
                    rows[y][x] = c
                x += 1
            p += nbytes + (nbytes & 1)          # word aligned
    return rows


def write_png(path, rows):
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(c for px in r for c in px) for r in rows)
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def key_magenta(rows):
    return [[(r, g, b, 0) if (r, g, b) == (255, 0, 255) else (r, g, b, a) for r, g, b, a in row] for row in rows]


def crop(rows, x, y, w, h):
    return [row[x:x + w] for row in rows[y:y + h]]


def best_icon(res, group_id, size=16):
    """Pick the best size×size image of an icon group (most colours)."""
    grp = res.get((14, group_id))
    if not grp:
        return None
    count = struct.unpack("<H", grp[4:6])[0]
    best = None
    for i in range(count):
        e = grp[6 + i * 14:6 + (i + 1) * 14]
        w, h, colors, _, planes, bpp, size_b, icon_id = struct.unpack("<BBBBHHIH", e)
        w = w or 256
        if w != size:
            continue
        score = bpp or 0
        if best is None or score > best[0]:
            best = (score, icon_id)
    if not best:
        return None
    dib = res.get((3, best[1]))
    if not dib or dib[:4] == b"\x89PNG":
        return None
    return decode_dib(dib, icon=True)[2]

# ------------------------------------------------------------------ mapping
# browseui.dll bitmap 265 (cold, grey) / 266 (hot, colour): 16 buttons, 20x20 each
TOOLBAR = {
    0: "back", 1: "forward", 2: "stop", 3: "refresh", 4: "home", 5: "search",
    6: "favorites", 7: "print", 8: "fonts", 9: "edit", 10: "discuss", 11: "media",
    12: "history", 13: "mail", 14: "fullscreen", 15: "encoding",
}
BUTTONS = {   # Firefox / Fox Explorer button id -> icon name (main IE6 strip)
    "back-button": "back", "forward-button": "forward", "fe6-stop-button": "stop", "stop-button": "stop",
    "fe6-refresh-button": "refresh", "reload-button": "refresh", "home-button": "home",
    "fe6-search-button": "search", "fe6-favorites-button": "favorites", "bookmarks-menu-button": "favorites",
    "bookmarks-toolbar-button": "favorites", "fe6-history-button": "history", "history-panelmenu": "history",
    "fe6-mail-button": "mail", "email-link-button": "mail", "fe6-print-button": "print", "print-button": "print",
    "fullscreen-button": "fullscreen", "characterencoding-button": "encoding",
}
# browseui.dll bitmap 276 (cold) / 277 (hot): Windows Explorer / Edit buttons, 20x20 each
SHELL = {
    4: "explorerbar", 5: "cut", 6: "copy", 7: "paste", 10: "delete", 12: "open", 13: "save",
    15: "properties", 17: "find", 41: "newwindow", 43: "folders", 45: "copyto",
}
SHELL_BUTTONS = {
    "sidebar-button": "explorerbar", "cut-button": "cut", "copy-button": "copy", "paste-button": "paste",
    "panic-button": "delete", "open-file-button": "open", "save-page-button": "save",
    "preferences-button": "properties", "find-button": "find", "new-window-button": "newwindow",
    "library-button": "folders", "import-button": "copyto",
}
ICONS16 = {   # shdocvw.dll icon groups: status bar, Downloads
    111: "internet", 12768: "lock", 113: "downloads16",
}


def pad(rows, size=20):
    """Centre a smaller image on a transparent size×size canvas (keeps pixels crisp)."""
    h, w = len(rows), len(rows[0])
    ox, oy = (size - w) // 2, (size - h) // 2
    out = [[(0, 0, 0, 0)] * size for _ in range(size)]
    for y in range(h):
        for x in range(w):
            out[y + oy][x + ox] = rows[y][x]
    return out


def grey(rows):
    """IE-style 'cold' version of a colour icon."""
    res = []
    for row in rows:
        r2 = []
        for r, g, b, a in row:
            v = int(0.3 * r + 0.59 * g + 0.11 * b)
            v = 128 + (v - 128) // 2 if a else v
            r2.append((v, v, v, a))
        res.append(r2)
    return res


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        cabs = collect_cabs(src, work)
        if not cabs:
            raise SystemExit("no .CAB files found — point this at an IE6 setup CD image")
        browseui = pe_resources(extract_dll(cabs, "BROWSEUI.DLL", work))
        shdocvw = pe_resources(extract_dll(cabs, "SHDOCVW.DLL", work))

    written = []
    for state, bid in (("cold", 265), ("hot", 266)):
        dib = browseui.get((2, bid))
        if not dib:
            raise SystemExit(f"toolbar bitmap {bid} missing from BROWSEUI.DLL (unexpected IE version)")
        w, h, rows = decode_dib(dib)
        rows = key_magenta(rows)
        for i, name in TOOLBAR.items():
            write_png(os.path.join(out, f"{name}-{state}.png"), crop(rows, i * 20, 0, 20, 20))
            written.append(f"{name}-{state}.png")
    for state, bid in (("cold", 276), ("hot", 277)):   # Explorer / Edit strip
        dib = browseui.get((2, bid))
        if not dib:
            continue
        w, h, rows = decode_dib(dib)
        rows = key_magenta(rows)
        for i, name in SHELL.items():
            if (i + 1) * 20 <= w:
                write_png(os.path.join(out, f"{name}-{state}.png"), crop(rows, i * 20, 0, 20, 20))
                written.append(f"{name}-{state}.png")
    for state, bid in (("cold", 290), ("hot", 291)):   # the "Go" arrow
        dib = browseui.get((2, bid))
        if dib:
            w, h, rows = decode_dib(dib)
            write_png(os.path.join(out, f"go-{state}.png"), key_magenta(rows))
            written.append(f"go-{state}.png")
    for gid, name in ICONS16.items():
        rows = best_icon(shdocvw, gid)
        if rows:
            write_png(os.path.join(out, f"{name}.png"), rows)
            written.append(f"{name}.png")
            if name == "downloads16":         # toolbar-size Downloads button from the 16px icon
                write_png(os.path.join(out, "downloads-hot.png"), pad(rows))
                write_png(os.path.join(out, "downloads-cold.png"), pad(grey(rows)))
                written += ["downloads-hot.png", "downloads-cold.png"]

    have = set(written)
    css = ["/* Generated by import-ie6-icons.py from your IE6 media. Not for redistribution. */"]
    mapped = dict(BUTTONS)
    mapped.update({k: v for k, v in SHELL_BUTTONS.items() if f"{v}-cold.png" in have})
    if "downloads-cold.png" in have:
        mapped["downloads-button"] = "downloads"
    for bid, name in mapped.items():
        # these buttons have real IE6 cold/hot artwork, so switch images instead of greying
        css.append(f"#{bid} .toolbarbutton-icon {{ filter: none !important; }}")
        css.append(f"#{bid}[disabled] .toolbarbutton-icon {{ filter: grayscale(1) opacity(.45) !important; }}")
        css.append(f"#{bid}, #{bid} .toolbarbutton-icon {{ list-style-image: url(\"{name}-cold.png\") !important; }}")
        css.append(f"#{bid}:not([disabled]):is(:hover, [open], [checked]), #{bid}:not([disabled]):is(:hover, [open], [checked]) .toolbarbutton-icon "
                   f"{{ list-style-image: url(\"{name}-hot.png\") !important; }}")
    if "downloads-cold.png" in have:
        css.append('#downloads-indicator-icon { list-style-image: url("downloads-cold.png") !important; filter: none !important; }')
        css.append('#downloads-button:not([disabled]):is(:hover, [open]) #downloads-indicator-icon { list-style-image: url("downloads-hot.png") !important; }')
    if "go-cold.png" in have:
        css.append('#fe6-go-button, #fe6-go-button .toolbarbutton-icon { list-style-image: url("go-cold.png") !important; filter: none !important; }')
        css.append('#fe6-go-button:hover, #fe6-go-button:hover .toolbarbutton-icon { list-style-image: url("go-hot.png") !important; }')
        css.append("#fe6-go-button > .toolbarbutton-icon { width: 18px !important; height: 16px !important; }")
    if "internet.png" in have:
        css.append('#fe6-status-zone:not([zone="local"]) #fe6-status-zone-icon { list-style-image: url("internet.png") !important; }')
    if "lock.png" in have:
        css.append('#fe6-status-lock { list-style-image: url("lock.png") !important; }')
    with open(os.path.join(out, "ie6.css"), "w") as f:
        f.write("\n".join(css) + "\n")
    print(f"imported {len(written)} IE6 icons into {out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Swap the Firefox branding inside an official Firefox build for Fox Explorer 6.

    rebrand-omni.py FIREFOX_DIR BRANDING_DIR

FIREFOX_DIR is the unpacked install (contains omni.ja and browser/omni.ja).
BRANDING_DIR is branding/foxexplorer from this repo.

Only branding resources change: names in brand.ftl/brand.properties, logos, icons and
the branding prefs. Everything else in omni.ja is copied byte-for-byte.
(Self-built source builds don't need this script: they use --with-branding.)
"""
import os
import re
import shutil
import sys
import zipfile


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ff, brand = sys.argv[1], sys.argv[2]
    omni = os.path.join(ff, "browser", "omni.ja")
    if not os.path.isfile(omni):
        sys.exit(f"error: {omni} not found")

    def read(rel):
        with open(os.path.join(brand, rel), "rb") as f:
            return f.read()

    brand_ftl = read("locales/en-US/brand.ftl")
    brand_props = read("locales/en-US/brand.properties")
    replacements = {
        "chrome/browser/content/branding/about-logo.png": read("content/about-logo.png"),
        "chrome/browser/content/branding/about-logo@2x.png": read("content/about-logo@2x.png"),
        "chrome/browser/content/branding/about-logo.svg": read("content/about-logo.svg"),
        "chrome/browser/content/branding/about-logo-private.png": read("content/about-logo-private.png"),
        "chrome/browser/content/branding/about-logo-private@2x.png": read("content/about-logo-private@2x.png"),
        "chrome/browser/content/branding/about-wordmark.svg": read("content/about-wordmark.svg"),
        "chrome/browser/content/branding/firefox-wordmark.svg": read("content/firefox-wordmark.svg"),
        "chrome/browser/content/branding/about.png": read("content/about.png"),
        "chrome/browser/content/branding/aboutDialog.css": read("content/aboutDialog.css"),
        "defaults/preferences/firefox-branding.js": read("pref/firefox-branding.js"),
    }
    for size in (16, 32, 48, 64, 128):
        replacements[f"chrome/browser/content/branding/icon{size}.png"] = read(f"default{size}.png")

    ftl_re = re.compile(r"^localization/[^/]+/branding/brand\.ftl$")
    props_re = re.compile(r"^chrome/[^/]+/locale/branding/brand\.properties$")

    tmp = omni + ".fe6tmp"
    changed = []
    with zipfile.ZipFile(omni) as src, zipfile.ZipFile(tmp, "w") as dst:
        for info in src.infolist():
            name = info.filename
            if name in replacements:
                data = replacements[name]
            elif ftl_re.match(name):
                data = brand_ftl
            elif props_re.match(name):
                data = brand_props
            else:
                dst.writestr(info, src.read(name), compress_type=info.compress_type)
                continue
            changed.append(name)
            new = zipfile.ZipInfo(name, date_time=info.date_time)
            new.external_attr = info.external_attr
            dst.writestr(new, data, compress_type=zipfile.ZIP_DEFLATED)
    os.replace(tmp, omni)

    # window / taskbar icons
    icon_dir = os.path.join(ff, "browser", "chrome", "icons", "default")
    os.makedirs(icon_dir, exist_ok=True)
    for size in (16, 32, 48, 64, 128):
        shutil.copyfile(os.path.join(brand, f"default{size}.png"), os.path.join(icon_dir, f"default{size}.png"))

    print(f"rebranded {len(changed)} resources in {omni}")
    if not any(ftl_re.match(n) for n in changed):
        sys.exit("error: no brand.ftl found in omni.ja — unexpected Firefox layout")


if __name__ == "__main__":
    main()

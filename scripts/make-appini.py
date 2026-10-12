#!/usr/bin/env python3
"""Write FIREFOX_DIR/browser/foxexplorer6.ini from the build's application.ini.

The launcher starts Firefox with `-app browser/foxexplorer6.ini`, which gives Fox Explorer 6
its own profile folder (~/.mozilla/foxexplorer6) and its own window class / remoting name,
so it never shares a profile or a running instance with a normal Firefox install.
The app Name and ID stay "Firefox" so websites, the user-agent string and addons.mozilla.org
treat it exactly like Firefox.
"""
import configparser, os, sys

ff = sys.argv[1]
src = None
for cand in (os.path.join(ff, "application.ini"), os.path.join(ff, "browser", "application.ini")):
    if os.path.isfile(cand):
        src = cand
        break
if not src:
    sys.exit("error: no application.ini in " + ff)

cp = configparser.ConfigParser(interpolation=None, strict=False)
cp.optionxform = str
with open(src, encoding="utf-8") as f:
    text = "\n".join(l for l in f.read().splitlines() if not l.lstrip().startswith(";"))
cp.read_string(text)
app = cp["App"]
app["Profile"] = "mozilla/foxexplorer6"
app["RemotingName"] = "foxexplorer6"
if cp.has_section("Crash Reporter"):
    cp["Crash Reporter"]["Enabled"] = "0"   # don't send crashes from a modified build to Mozilla
out = os.path.join(ff, "browser", "foxexplorer6.ini")
with open(out, "w", encoding="utf-8") as f:
    f.write("; Fox Explorer 6 application data (see scripts/make-appini.py)\n")
    cp.write(f, space_around_delimiters=False)
print("wrote", out, "(Firefox", app.get("Version", "?") + ")")

#!/usr/bin/env python3
"""Generates the Fox Explorer 6 icon set (original artwork, Win98-style 16-colour palette)."""
import os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "theme", "fe6", "icons")
os.makedirs(OUT, exist_ok=True)
K, W, G, S, N, B, T, GR, LI, M, R, O, Y = ("#000000", "#ffffff", "#808080", "#c0c0c0", "#000080", "#0000ff",
    "#008080", "#008000", "#00c000", "#800000", "#ff0000", "#808000", "#ffff00")

def svg(name, size, body, extra=""):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
                f'shape-rendering="crispEdges"{extra}>{body}</svg>\n')

def arrow(flip):
    pts = [(1.5,10),(9.5,2.5),(9.5,6.5),(18.5,6.5),(18.5,13.5),(9.5,13.5),(9.5,17.5)]
    if flip: pts = [(20-x, y) for x, y in pts]
    p = " ".join(f"{x},{y}" for x, y in pts)
    hi = "M9.5,7.5 H17.5" if not flip else "M2.5,7.5 H10.5"
    return (f'<polygon points="{p}" fill="{GR}" stroke="{K}" shape-rendering="geometricPrecision"/>'
            f'<path d="{hi}" stroke="{LI}" stroke-width="1.5"/>')

svg("back.svg", 20, arrow(False))
svg("forward.svg", 20, arrow(True))
svg("stop.svg", 20,
    f'<polygon points="6.5,1.5 13.5,1.5 18.5,6.5 18.5,13.5 13.5,18.5 6.5,18.5 1.5,13.5 1.5,6.5" fill="{R}" stroke="{M}"/>'
    f'<path d="M6,6 L14,14 M14,6 L6,14" stroke="{W}" stroke-width="2.6" stroke-linecap="square" shape-rendering="geometricPrecision"/>')
svg("refresh.svg", 20,
    f'<path d="M3.5,1.5 H12.5 L16.5,5.5 V18.5 H3.5 Z" fill="{W}" stroke="{K}"/><path d="M12.5,1.5 V5.5 H16.5" fill="{S}" stroke="{K}"/>'
    f'<g fill="none" stroke="{GR}" stroke-width="2" shape-rendering="geometricPrecision">'
    f'<path d="M6,11 A4,4 0 0 1 13,8.5"/><path d="M14,12 A4,4 0 0 1 7,14.5"/></g>'
    f'<polygon points="13.5,6 14.8,10 10.6,9.6" fill="{GR}" shape-rendering="geometricPrecision"/>'
    f'<polygon points="6.5,17 5.2,13 9.4,13.4" fill="{GR}" shape-rendering="geometricPrecision"/>')
svg("home.svg", 20,
    f'<rect x="4.5" y="9.5" width="11" height="9" fill="{Y}" stroke="{K}"/><rect x="8.5" y="12.5" width="3" height="6" fill="{M}" stroke="{K}"/>'
    f'<polygon points="1,10.5 10,2 19,10.5" fill="{R}" stroke="{K}" shape-rendering="geometricPrecision"/>'
    f'<rect x="13.5" y="3.5" width="2" height="4" fill="{M}" stroke="{K}"/>')
globe = lambda cx, cy, r: (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{B}" stroke="{N}" shape-rendering="geometricPrecision"/>'
    f'<path d="M{cx-r*.6},{cy-r*.5} q{r*.5},{-r*.2} {r*.7},{r*.4} q{-r*.1},{r*.5} {-r*.6},{r*.6} z M{cx+r*.2},{cy+r*.2} q{r*.5},{-r*.1} {r*.6},{r*.4} q{-r*.3},{r*.4} {-r*.5},{r*.3} z" fill="{LI}" shape-rendering="geometricPrecision"/>')
svg("search.svg", 20, globe(8, 8, 6.5) +
    f'<circle cx="12" cy="12" r="4.5" fill="#bfe8ff" fill-opacity=".85" stroke="{K}" stroke-width="1.6" shape-rendering="geometricPrecision"/>'
    f'<path d="M15.2,15.2 L19,19" stroke="{K}" stroke-width="3" stroke-linecap="round" shape-rendering="geometricPrecision"/>')
svg("favorites.svg", 20,
    f'<polygon points="10,1.5 12.6,7.2 18.7,7.6 14,11.6 15.5,17.7 10,14.4 4.5,17.7 6,11.6 1.3,7.6 7.4,7.2" fill="{Y}" stroke="{O}" shape-rendering="geometricPrecision"/>'
    f'<path d="M10,4 L11.5,7.6" stroke="{W}" stroke-width="1.2" shape-rendering="geometricPrecision"/>')
svg("history.svg", 20,
    f'<circle cx="10" cy="10" r="7.5" fill="{W}" stroke="{K}" shape-rendering="geometricPrecision"/>'
    f'<path d="M10,4.5 V10 H14" fill="none" stroke="{K}" stroke-width="1.5"/>'
    f'<path d="M3.2,13.5 A8.3,8.3 0 0 0 17,15" fill="none" stroke="{GR}" stroke-width="2" shape-rendering="geometricPrecision"/>'
    f'<polygon points="17.5,12 18.8,17 14.2,16" fill="{GR}" shape-rendering="geometricPrecision"/>')
svg("print.svg", 20,
    f'<rect x="5.5" y="1.5" width="9" height="7" fill="{W}" stroke="{K}"/><rect x="1.5" y="7.5" width="17" height="8" fill="{S}" stroke="{K}"/>'
    f'<rect x="2.5" y="8.5" width="15" height="1" fill="{W}"/><rect x="14.5" y="10.5" width="2" height="1" fill="{GR}"/>'
    f'<rect x="4.5" y="13.5" width="11" height="5" fill="{W}" stroke="{K}"/><path d="M6,15.5 H14 M6,17 H12" stroke="{G}"/>')
svg("mail.svg", 20,
    f'<rect x="1.5" y="4.5" width="17" height="12" fill="{W}" stroke="{K}"/><path d="M1.5,4.5 L10,11.5 L18.5,4.5" fill="none" stroke="{K}" shape-rendering="geometricPrecision"/>'
    f'<rect x="14.5" y="6.5" width="3" height="3" fill="{R}"/>')
svg("go.svg", 16,
    f'<rect x="0.5" y="0.5" width="15" height="15" fill="{GR}" stroke="{K}"/><rect x="1" y="1" width="14" height="1" fill="{LI}"/>'
    f'<polygon points="3,6 8,6 8,3 13,8 8,13 8,10 3,10" fill="{W}" shape-rendering="geometricPrecision"/>')
svg("page.svg", 16,
    f'<path d="M2.5,0.5 H10.5 L13.5,3.5 V15.5 H2.5 Z" fill="{W}" stroke="{K}"/><path d="M10.5,0.5 V3.5 H13.5" fill="{S}" stroke="{K}"/>'
    f'<path d="M4.5,6.5 H11.5 M4.5,8.5 H11.5 M4.5,10.5 H11.5 M4.5,12.5 H9.5" stroke="{G}"/>')
svg("extensions.svg", 20,
    f'<path d="M3.5,6.5 H7.5 A2.2,2.2 0 1 1 11.5,6.5 H15.5 V10.5 A2.2,2.2 0 1 1 15.5,14.5 V18.5 H3.5 Z" fill="{T}" stroke="{K}" shape-rendering="geometricPrecision"/>'
    f'<path d="M4.5,7.5 H7 M4.5,7.5 V17" stroke="#40c0c0"/>')
svg("downloads.svg", 20,
    f'<rect x="1.5" y="13.5" width="17" height="5" fill="{S}" stroke="{K}"/><rect x="2.5" y="14.5" width="15" height="1" fill="{W}"/>'
    f'<polygon points="7.5,1.5 12.5,1.5 12.5,7.5 16,7.5 10,13.5 4,7.5 7.5,7.5" fill="{GR}" stroke="{K}"/>')
svg("newtab.svg", 16,
    f'<path d="M1.5,1.5 H9.5 L12.5,4.5 V14.5 H1.5 Z" fill="{W}" stroke="{K}"/><path d="M9.5,1.5 V4.5 H12.5" fill="{S}" stroke="{K}"/>'
    f'<rect x="9" y="9" width="7" height="7" fill="{GR}"/><path d="M12.5,10 V15 M10,12.5 H15" stroke="{W}" stroke-width="1.6"/>')
svg("lock.svg", 16,
    f'<path d="M4.5,7 V4.5 A3.5,3.5 0 0 1 11.5,4.5 V7" fill="none" stroke="{K}" stroke-width="1.6" shape-rendering="geometricPrecision"/>'
    f'<rect x="2.5" y="6.5" width="11" height="8" fill="{Y}" stroke="{K}"/><rect x="3.5" y="7.5" width="9" height="1" fill="{W}"/><rect x="7" y="9.5" width="2" height="3" fill="{K}"/>')
svg("globe.svg", 16, globe(8, 8, 6.8))
svg("computer.svg", 16,
    f'<rect x="1.5" y="1.5" width="13" height="10" fill="{S}" stroke="{K}"/><rect x="3.5" y="3.5" width="9" height="6" fill="{T}" stroke="{K}"/>'
    f'<rect x="4.5" y="12.5" width="7" height="2" fill="{S}" stroke="{K}"/>')
svg("bookmark.svg", 16,
    f'<path d="M2.5,1.5 H10.5 L13.5,4.5 V14.5 H2.5 Z" fill="{W}" stroke="{K}"/>'
    f'<polygon points="8,5 9.3,7.8 12.3,8 10,10 10.8,13 8,11.3 5.2,13 6,10 3.7,8 6.7,7.8" fill="{Y}" stroke="{O}" shape-rendering="geometricPrecision"/>')
svg("folder.svg", 16,
    f'<path d="M0.5,3.5 H5.5 L7.5,5.5 H14.5 V13.5 H0.5 Z" fill="{Y}" stroke="{O}"/><rect x="1.5" y="6.5" width="12" height="1" fill="{W}"/>')
svg("menu.svg", 20, f'<rect x="3" y="4" width="14" height="2" fill="{K}"/><rect x="3" y="9" width="14" height="2" fill="{K}"/><rect x="3" y="14" width="14" height="2" fill="{K}"/>')
svg("sidebar.svg", 20, f'<rect x="1.5" y="2.5" width="17" height="15" fill="{W}" stroke="{K}"/><rect x="2" y="3" width="6" height="14" fill="{S}"/><path d="M8.5,3 V17" stroke="{K}"/>')

print("icons written to", os.path.abspath(OUT))

# Win98 caption-button glyphs (drawn in the current text colour via context-fill)
cf = 'fill="context-fill"'
svg("cap-min.svg", 16, f'<rect x="4" y="9" width="6" height="2" {cf}/>', ' viewBox-fix=""'.replace(' viewBox-fix=""', ''))
svg("cap-max.svg", 16, f'<path d="M3,3 H12 V11 H3 Z M4,5 V10 H11 V5 Z" {cf} fill-rule="evenodd"/>')
svg("cap-restore.svg", 16, f'<path d="M5,2 H12 V8 H10 V7 H11 V4 H6 V5 H5 Z" {cf}/><path d="M3,5 H10 V11 H3 Z M4,7 V10 H9 V7 Z" {cf} fill-rule="evenodd"/>')
svg("cap-close.svg", 16, f'<path d="M4,3 H6 L7.5,5 L9,3 H11 L8.5,6.5 L11,10 H9 L7.5,8 L6,10 H4 L6.5,6.5 Z" {cf}/>')
svg("menu-check.svg", 16, f'<path d="M4,7 L6,9 L11,4 V6 L6,11 L4,9 Z" {cf}/>')
svg("menu-radio.svg", 16, f'<rect x="6" y="6" width="4" height="4" {cf}/><rect x="5" y="7" width="6" height="2" {cf}/><rect x="7" y="5" width="2" height="6" {cf}/>')
# "List all tabs": a Win98 combo-box drop arrow
svg("alltabs.svg", 16, f'<path d="M4,6 H12 L8,10 Z" {cf}/>')

# ---------------------------------------------------------------- palette / sidebar icons (20x20)
GP = ' shape-rendering="geometricPrecision"'
page = lambda x=3.5, y=1.5, w=12, h=17: (f'<path d="M{x},{y} H{x+w-4} L{x+w},{y+4} V{y+h} H{x} Z" fill="{W}" stroke="{K}"/>'
                                         f'<path d="M{x+w-4},{y} V{y+4} H{x+w}" fill="{S}" stroke="{K}"/>')
svg("save.svg", 20, f'<rect x="2.5" y="2.5" width="15" height="15" fill="{N}" stroke="{K}"/><rect x="5.5" y="2.5" width="9" height="6" fill="{W}" stroke="{K}"/>'
    f'<rect x="11" y="3.5" width="2" height="4" fill="{N}"/><rect x="4.5" y="11.5" width="11" height="6" fill="{S}" stroke="{K}"/><path d="M6,13.5 H14 M6,15.5 H12" stroke="{G}"/>')
svg("find.svg", 20, page(2.5, 1.5, 11, 16) + f'<path d="M4.5,6.5 H10.5 M4.5,8.5 H8.5" stroke="{G}"/>'
    f'<circle cx="12" cy="11" r="4" fill="#bfe8ff" stroke="{K}" stroke-width="1.6"{GP}/><path d="M15,14 L18.5,17.5" stroke="{K}" stroke-width="3" stroke-linecap="round"{GP}/>')
svg("open.svg", 20, f'<path d="M1.5,5.5 H6.5 L8.5,7.5 H15.5 V16.5 H1.5 Z" fill="{Y}" stroke="{O}"/>'
    f'<path d="M3.5,10.5 H18.5 L15.5,16.5 H1.5 Z" fill="#ffe680" stroke="{O}"/><path d="M12,2 Q16,1 17,5" fill="none" stroke="{B}" stroke-width="1.5"{GP}/><polygon points="17.5,6.5 15.5,4 19,3.5" fill="{B}"{GP}/>')
svg("cut.svg", 20, f'<path d="M7,2 L11,11 M13,2 L9,11" stroke="{G}" stroke-width="2"{GP}/>'
    f'<circle cx="6.5" cy="14.5" r="3" fill="none" stroke="{B}" stroke-width="1.8"{GP}/><circle cx="13.5" cy="14.5" r="3" fill="none" stroke="{B}" stroke-width="1.8"{GP}/>')
svg("copy.svg", 20, page(1.5, 1.5, 10, 12) + page(7.5, 6.5, 10, 12) + f'<path d="M9.5,11.5 H15.5 M9.5,13.5 H15.5 M9.5,15.5 H13.5" stroke="{B}"/>')
svg("paste.svg", 20, f'<rect x="2.5" y="3.5" width="12" height="15" fill="#b08040" stroke="{K}"/><rect x="5.5" y="1.5" width="6" height="4" fill="{S}" stroke="{K}"/>'
    + page(8.5, 7.5, 9, 11) + f'<path d="M10.5,11.5 H15.5 M10.5,13.5 H15.5 M10.5,15.5 H14.5" stroke="{B}"/>')
svg("zoom-in.svg", 20, f'<circle cx="8.5" cy="8.5" r="6" fill="#bfe8ff" stroke="{K}" stroke-width="1.6"{GP}/><path d="M13,13 L18.5,18.5" stroke="{K}" stroke-width="3" stroke-linecap="round"{GP}/>'
    f'<path d="M5.5,8.5 H11.5 M8.5,5.5 V11.5" stroke="{K}" stroke-width="1.6"/>')
svg("zoom-out.svg", 20, f'<circle cx="8.5" cy="8.5" r="6" fill="#bfe8ff" stroke="{K}" stroke-width="1.6"{GP}/><path d="M13,13 L18.5,18.5" stroke="{K}" stroke-width="3" stroke-linecap="round"{GP}/>'
    f'<path d="M5.5,8.5 H11.5" stroke="{K}" stroke-width="1.6"/>')
svg("encoding.svg", 20, f'<text x="1" y="12" font-family="Times New Roman, serif" font-size="12" font-weight="bold" fill="{B}">A</text>'
    f'<text x="9" y="17" font-family="Times New Roman, serif" font-size="11" font-weight="bold" fill="{GR}">a</text><path d="M3,17.5 H8 M15,3 V8" stroke="{R}" stroke-width="1.5"/>')
svg("key.svg", 20, f'<circle cx="6" cy="10" r="4" fill="{Y}" stroke="{O}" stroke-width="1.4"{GP}/><circle cx="6" cy="10" r="1.3" fill="{W}"{GP}/>'
    f'<rect x="9.5" y="9" width="9" height="2" fill="{Y}" stroke="{O}"/><rect x="14.5" y="11" width="2" height="3" fill="{Y}" stroke="{O}"/><rect x="17" y="11" width="1.5" height="2" fill="{O}"/>')
svg("share.svg", 20, page(2.5, 4.5, 11, 14) + f'<path d="M8,11 Q10,4 16,4" fill="none" stroke="{GR}" stroke-width="2"{GP}/><polygon points="15,1 19.5,4 15,7" fill="{GR}"{GP}/>')
svg("synced.svg", 20, f'<rect x="1.5" y="3.5" width="11" height="8" fill="{T}" stroke="{K}"/><rect x="5.5" y="11.5" width="3" height="2" fill="{S}" stroke="{K}"/>'
    f'<rect x="12.5" y="8.5" width="6" height="10" fill="{S}" stroke="{K}"/><rect x="13.5" y="9.5" width="4" height="7" fill="{T}"/>'
    f'<path d="M4,16 Q6,18.5 10,17" fill="none" stroke="{GR}" stroke-width="1.6"{GP}/>')
svg("sendtab.svg", 20, page(1.5, 2.5, 9, 12) + f'<rect x="12.5" y="6.5" width="6" height="11" fill="{S}" stroke="{K}"/><rect x="13.5" y="7.5" width="4" height="8" fill="{T}"/>'
    f'<path d="M5,9.5 H11" stroke="{GR}" stroke-width="2"/><polygon points="10,6.5 13,9.5 10,12.5" fill="{GR}"/>')
svg("settings.svg", 20, f'<rect x="2.5" y="2.5" width="15" height="15" fill="{W}" stroke="{K}"/><rect x="2.5" y="2.5" width="15" height="3" fill="{N}" stroke="{K}"/>'
    f'<rect x="4.5" y="8.5" width="3" height="3" fill="{W}" stroke="{K}"/><path d="M5,10 L6,11 L8,8" stroke="{GR}" stroke-width="1.2" fill="none"{GP}/><path d="M9.5,10.5 H15.5 M9.5,14.5 H15.5" stroke="{G}"/>'
    f'<rect x="4.5" y="12.5" width="3" height="3" fill="{W}" stroke="{K}"/>')
svg("forget.svg", 20, page(3.5, 1.5, 12, 17) + f'<path d="M6,6 L13,15 M13,6 L6,15" stroke="{R}" stroke-width="2.4"{GP}/>')
svg("private.svg", 20, f'<rect x="1.5" y="3.5" width="17" height="13" fill="{W}" stroke="{K}"/><rect x="1.5" y="3.5" width="17" height="3" fill="#600080" stroke="{K}"/>'
    f'<path d="M4,11 Q7,9 10,11 Q13,9 16,11 L15,14 Q12.5,15 11,13 L9,13 Q7.5,15 5,14 Z" fill="{K}"{GP}/>')
svg("fxview.svg", 20, f'<rect x="1.5" y="4.5" width="17" height="13" fill="{W}" stroke="{K}"/><rect x="2.5" y="2.5" width="5" height="3" fill="{S}" stroke="{K}"/><rect x="8.5" y="2.5" width="5" height="3" fill="{S}" stroke="{K}"/>'
    f'<path d="M4.5,8.5 H15.5 M4.5,11.5 H15.5 M4.5,14.5 H11.5" stroke="{B}"/>')
svg("developer.svg", 20, f'<rect x="2" y="3" width="9" height="5" fill="{G}" stroke="{K}" transform="rotate(-35 6.5 5.5)"/>'
    f'<rect x="7.5" y="6.5" width="3" height="12" fill="{M}" stroke="{K}" transform="rotate(-35 9 12.5)"/>'
    f'<path d="M12,4 L17,4 L17,6 L14,6 L14,17 L12,17 Z" fill="{S}" stroke="{K}"/>')
svg("screenshot.svg", 20, f'<rect x="1.5" y="5.5" width="17" height="11" fill="{G}" stroke="{K}"/><rect x="6.5" y="3.5" width="6" height="2" fill="{G}" stroke="{K}"/>'
    f'<circle cx="10" cy="11" r="3.5" fill="#bfe8ff" stroke="{K}" stroke-width="1.3"{GP}/><rect x="14.5" y="6.5" width="2" height="1.5" fill="{Y}"/>')
svg("import.svg", 20, f'<path d="M1.5,7.5 H6.5 L8.5,9.5 H18.5 V18.5 H1.5 Z" fill="{Y}" stroke="{O}"/><rect x="2.5" y="10.5" width="15" height="1" fill="{W}"/>'
    f'<path d="M10,1.5 V9" stroke="{GR}" stroke-width="2.2"/><polygon points="6.5,7 10,11 13.5,7" fill="{GR}"/>')
svg("newwindow.svg", 20, f'<rect x="1.5" y="4.5" width="14" height="12" fill="{W}" stroke="{K}"/><rect x="1.5" y="4.5" width="14" height="3" fill="{N}" stroke="{K}"/>'
    f'<path d="M15.5,1 L16.5,3.5 L19,4.5 L16.5,5.5 L15.5,8 L14.5,5.5 L12,4.5 L14.5,3.5 Z" fill="{Y}" stroke="{O}" stroke-width=".8"{GP}/>')
svg("fullscreen.svg", 20, f'<rect x="1.5" y="2.5" width="17" height="15" fill="{W}" stroke="{K}"/><rect x="1.5" y="2.5" width="17" height="3" fill="{N}" stroke="{K}"/>'
    f'<path d="M5,9 V7.5 H7 M15,9 V7.5 H13 M5,13 V15 H7 M15,13 V15 H13" fill="none" stroke="{R}" stroke-width="1.4"/>')
svg("library.svg", 20, f'<rect x="1.5" y="3.5" width="4" height="14" fill="{R}" stroke="{K}"/><rect x="5.5" y="5.5" width="4" height="12" fill="{B}" stroke="{K}"/>'
    f'<rect x="9.5" y="2.5" width="4" height="15" fill="{GR}" stroke="{K}"/><rect x="13.5" y="5.5" width="4" height="12" fill="{Y}" stroke="{O}" transform="rotate(12 15.5 17)"/>'
    f'<path d="M2.5,6.5 H4.5 M6.5,8.5 H8.5 M10.5,5.5 H12.5" stroke="{W}"/>')
svg("account.svg", 20, f'<circle cx="10" cy="7" r="4" fill="#ffd8b0" stroke="{K}"{GP}/><path d="M3,18.5 Q3,11.5 10,11.5 Q17,11.5 17,18.5 Z" fill="{B}" stroke="{K}"{GP}/>'
    f'<path d="M6.5,6 Q10,1.5 13.5,6" fill="{M}" stroke="{K}" stroke-width=".8"{GP}/>')
svg("tabgroups.svg", 20, f'<rect x="1.5" y="6.5" width="17" height="11" fill="{W}" stroke="{K}"/><rect x="1.5" y="3.5" width="5" height="3" fill="{R}" stroke="{K}"/>'
    f'<rect x="6.5" y="3.5" width="5" height="3" fill="{GR}" stroke="{K}"/><rect x="11.5" y="3.5" width="5" height="3" fill="{B}" stroke="{K}"/>')
svg("splitview.svg", 20, f'<rect x="1.5" y="3.5" width="17" height="14" fill="{W}" stroke="{K}"/><rect x="1.5" y="3.5" width="17" height="3" fill="{N}" stroke="{K}"/><path d="M10,6.5 V17" stroke="{K}"/>')
svg("pip.svg", 20, f'<rect x="1.5" y="3.5" width="17" height="14" fill="{W}" stroke="{K}"/><rect x="9.5" y="10.5" width="7" height="5" fill="{T}" stroke="{K}"/>')
svg("chat.svg", 20, f'<path d="M2.5,3.5 H17.5 V13.5 H8 L4,17 V13.5 H2.5 Z" fill="#ffffe1" stroke="{K}"/><path d="M5,7 H15 M5,10 H12" stroke="{G}"/>')
svg("reader.svg", 20, page(3.5, 1.5, 13, 17) + f'<path d="M5.5,6.5 H13.5 M5.5,9 H13.5 M5.5,11.5 H13.5 M5.5,14 H11" stroke="{K}"/>')
svg("monitor.svg", 20, f'<path d="M2,15 A8,8 0 0 1 18,15 Z" fill="{W}" stroke="{K}"{GP}/><path d="M10,15 L14,8" stroke="{R}" stroke-width="1.8"{GP}/>'
    f'<circle cx="10" cy="15" r="1.5" fill="{K}"{GP}/><path d="M3.5,15 H5 M15,15 H16.5 M10,8 V9.5" stroke="{K}"/>')
svg("customize.svg", 20, f'<path d="M1.5,5.5 H6.5 L8.5,7.5 H15.5 V16.5 H1.5 Z" fill="{Y}" stroke="{O}"/>'
    f'<rect x="12" y="1" width="6" height="4" fill="{G}" stroke="{K}"/><rect x="14" y="5" width="2" height="12" fill="{M}" stroke="{K}"/>')
# Links-bar chevron (») and a plain drop arrow for the Search drop-down
svg("chevron.svg", 16, f'<path d="M4,4 L7,8 L4,12 M8,4 L11,8 L8,12" fill="none" {cf.replace("fill","stroke")} stroke-width="1.6"/>')
svg("tag.svg", 16, f'<path d="M1.5,2.5 H8.5 L14.5,8.5 L8.5,14.5 L1.5,7.5 Z" fill="{Y}" stroke="{O}"{GP}/><circle cx="4.5" cy="5.5" r="1.2" fill="{W}" stroke="{O}" stroke-width=".8"{GP}/>')
svg("day.svg", 16, f'<rect x="1.5" y="2.5" width="13" height="12" fill="{W}" stroke="{K}"/><rect x="1.5" y="2.5" width="13" height="3" fill="{R}" stroke="{K}"/><path d="M4,8.5 H6 M7,8.5 H9 M10,8.5 H12 M4,11.5 H6 M7,11.5 H9" stroke="{K}"/>')
svg("folder-favorites.svg", 16, f'<path d="M0.5,3.5 H5.5 L7.5,5.5 H14.5 V13.5 H0.5 Z" fill="{Y}" stroke="{O}"/><polygon points="8,6.5 9,8.8 11.4,9 9.6,10.5 10.2,12.8 8,11.5 5.8,12.8 6.4,10.5 4.6,9 7,8.8" fill="{W}" stroke="{O}" stroke-width=".7"{GP}/>')

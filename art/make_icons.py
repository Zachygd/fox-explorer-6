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

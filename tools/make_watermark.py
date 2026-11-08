"""Generate the LedgerX watermark tiles (logo + name, staggered, rotated).

Outputs (into the app):
  public/images/ledgerx-watermark.svg        light UI
  public/images/ledgerx-watermark-dark.svg   dark UI
  public/css/ledgerx_print.css               print watermark, SVG embedded as a data URI
                                             (self-contained: PDF engines never need to fetch it)
The wordmark is converted to outlined paths, so no font is needed at render time.
"""
import base64
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

# Usage:  python tools/make_watermark.py ledgerx        (needs: pip install fonttools)
# Set LEDGERX_FONT to a bold TTF (Poppins Bold gives the shipped look) if the default is missing.
FONT = os.environ.get("LEDGERX_FONT", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
APP = sys.argv[1]  # the app package folder, e.g. ./ledgerx

TILE_W, TILE_H = 520, 340
ANGLE = -22
SCALE = 0.8

font = TTFont(FONT)
gs = font.getGlyphSet()
cmap = font.getBestCmap()
upm = font["head"].unitsPerEm


def outline(text, size, x0, baseline):
    scale = size / upm
    x = x0
    parts = []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        parts.append(pen.getCommands())
        x += gs[name].width * scale
    return " ".join(parts), x


led, x_end = outline("Ledger", 46, 78, 46)
xg, x_end2 = outline("X", 46, x_end + 1, 46)
LOGO_W = x_end2  # ~272 wide, 64 tall

MARK = """<rect x="2" y="2" width="60" height="60" rx="17" fill="url(#bg)"/>
      <path d="M20 14 V47 H50" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
      <g stroke="url(#gold)" stroke-width="6" stroke-linecap="round">
        <line x1="31" y1="23" x2="45" y2="37"/><line x1="45" y1="23" x2="31" y2="37"/>
      </g>"""


def tile(word, xcol, opacity):
    cx, cy = LOGO_W / 2, 32
    # two staggered instances so the pattern reads as a brick layout
    placements = [(130, 85), (390, 255)]
    uses = "\n  ".join(
        f'<use xlink:href="#lx" transform="translate({px} {py}) rotate({ANGLE}) scale({SCALE}) translate({-cx:.1f} {-cy})"/>'
        for px, py in placements
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{TILE_W}" height="{TILE_H}" viewBox="0 0 {TILE_W} {TILE_H}">
  <defs>
    <linearGradient id="bg" x1="6" y1="4" x2="58" y2="60" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0B2A5B"/><stop offset="0.55" stop-color="#0B5E78"/><stop offset="1" stop-color="#14B8A6"/>
    </linearGradient>
    <linearGradient id="gold" x1="30" y1="22" x2="47" y2="40" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFD166"/><stop offset="1" stop-color="#F5A524"/>
    </linearGradient>
    <g id="lx">
      {MARK}
      <path d="{led}" fill="{word}"/>
      <path d="{xg}" fill="{xcol}"/>
    </g>
  </defs>
  <g opacity="{opacity}">
  {uses}
  </g>
</svg>
"""


# Gold on white is weak, so the light/print tiles use a deeper gold for the X.
light = tile("#0B2A5B", "#E39A0B", 0.09)
dark = tile("#FFFFFF", "#FFD166", 0.09)
print_tile = tile("#0B2A5B", "#E39A0B", 0.13)

open(f"{APP}/public/images/ledgerx-watermark.svg", "w").write(light)
open(f"{APP}/public/images/ledgerx-watermark-dark.svg", "w").write(dark)

b64 = base64.b64encode(print_tile.encode()).decode()
css = f"""/*
 * LedgerX print watermark (logo + name, tiled, behind the content).
 *
 * This file is appended to a copy of Frappe's default "Redesign" print style when the app is
 * installed/migrated (see ledgerx/install.py), producing the "LedgerX" Print Style that the
 * Print Settings uses. It applies to the print preview and to PDFs.
 *
 * The tile is an embedded SVG (data URI), so PDF engines never need to download anything.
 * To change the strength or spacing, edit the opacity / TILE size in tools/make_watermark.py and
 * run `python tools/make_watermark.py ledgerx`, then `bench migrate` to refresh the Print Style.
 * To turn it off: Print Settings -> Print Style -> choose another style (e.g. "Redesign").
 */

/* Print preview on screen: the watermark lives on the white paper sheet (not the grey gutter). */
@media screen {{
	.print-format {{
		background-image: url("data:image/svg+xml;base64,{b64}") !important;
		background-repeat: repeat !important;
		background-size: {TILE_W}px {TILE_H}px !important;
	}}
}}

/* PDF / paper: paint the tile on the page itself so it covers the whole sheet on every page,
   even when the content is short. The sheet container must be transparent to let it show. */
@media print {{
	html,
	body {{
		background-image: url("data:image/svg+xml;base64,{b64}") !important;
		background-repeat: repeat !important;
		background-size: {TILE_W}px {TILE_H}px !important;
		-webkit-print-color-adjust: exact;
		print-color-adjust: exact;
	}}

	.print-format {{
		background: transparent !important;
		-webkit-print-color-adjust: exact;
		print-color-adjust: exact;
	}}
}}
"""
open(f"{APP}/public/css/ledgerx_print.css", "w").write(css)
print("logo width", round(LOGO_W, 1), "| print css", len(css), "bytes")

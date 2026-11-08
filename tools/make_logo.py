"""Generate LedgerX logo SVGs with the wordmark converted to outlined paths."""
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

# Usage:  python tools/make_logo.py ledgerx/public/images   (needs: pip install fonttools)
FONT = os.environ.get("LEDGERX_FONT", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
OUT = sys.argv[1]

MARK_DEFS = """<defs>
    <linearGradient id="lx-bg" x1="6" y1="4" x2="58" y2="60" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0B2A5B"/>
      <stop offset="0.55" stop-color="#0B5E78"/>
      <stop offset="1" stop-color="#14B8A6"/>
    </linearGradient>
    <linearGradient id="lx-gold" x1="30" y1="22" x2="47" y2="40" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFD166"/>
      <stop offset="1" stop-color="#F5A524"/>
    </linearGradient>
  </defs>"""

MARK_BODY = """<rect x="2" y="2" width="60" height="60" rx="17" fill="url(#lx-bg)"/>
  <g stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1.5" stroke-linecap="round">
    <line x1="12" y1="20" x2="52" y2="20"/>
    <line x1="12" y1="30" x2="52" y2="30"/>
    <line x1="12" y1="40" x2="52" y2="40"/>
  </g>
  <path d="M20 14 V47 H50" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <g stroke="url(#lx-gold)" stroke-width="6" stroke-linecap="round">
    <line x1="31" y1="23" x2="45" y2="37"/>
    <line x1="45" y1="23" x2="31" y2="37"/>
  </g>"""

font = TTFont(FONT)
gs = font.getGlyphSet()
cmap = font.getBestCmap()
upm = font["head"].unitsPerEm


def outline(text, size, x0, baseline):
    """Return (path_d, end_x) for text laid out with simple advance widths + kerning-free spacing."""
    scale = size / upm
    x = x0
    parts = []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        tpen = TransformPen(pen, (scale, 0, 0, -scale, x, baseline))
        gs[name].draw(tpen)
        parts.append(pen.getCommands())
        x += gs[name].width * scale
    return " ".join(parts), x


SIZE = 46
BASE = 46
led, x_end = outline("Ledger", SIZE, 78, BASE)
xg, x_end2 = outline("X", SIZE, x_end + 1, BASE)
width = int(x_end2 + 8)


def logo(color_word, color_x, bg=None):
    bg_rect = f'<rect width="{width}" height="64" fill="{bg}"/>' if bg else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 64" role="img" aria-label="LedgerX">
  {MARK_DEFS}
  {bg_rect}
  {MARK_BODY}
  <path d="{led}" fill="{color_word}"/>
  <path d="{xg}" fill="{color_x}"/>
</svg>
"""


open(f"{OUT}/ledgerx-logo.svg", "w").write(logo("#0B2A5B", "#F5A524"))
open(f"{OUT}/ledgerx-logo-light.svg", "w").write(logo("#FFFFFF", "#FFD166"))

mark = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="LedgerX">
  {MARK_DEFS}
  {MARK_BODY}
</svg>
"""
open(f"{OUT}/ledgerx-mark.svg", "w").write(mark)
open(f"{OUT}/ledgerx-favicon.svg", "w").write(mark)
print("width", width)

"""Build TrueType fonts from the parametric glyph definitions."""

import io

import ttfautohint
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from . import style as M
from .geometry import to_ttglyph
from .glyphs import GLYPHS, SPACE_WIDTH

FAMILY = "altfont"
VERSION = "0.001"


def _notdef(S):
    w, v = 1000, S.hstem
    pen = TTGlyphPen(None)
    for x0, y0, x1, y1, cw in ((0, 0, w, M.CAP_HEIGHT, True),
                               (v, v, w - v, M.CAP_HEIGHT - v, False)):
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        if not cw:
            pts.reverse()
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph(), w


def _side_bearing(S, kind):
    return S.sb_straight if kind == "S" else S.sb_round


def build_unhinted(S):
    glyph_order = [".notdef", "space"] + list(GLYPHS)
    cmap = {0x0020: "space", 0x00A0: "space"}
    glyf, hmtx = {}, {}

    notdef, w = _notdef(S)
    glyf[".notdef"] = notdef
    hmtx[".notdef"] = (w + 2 * S.sb_straight, 0)
    glyf["space"] = TTGlyphPen(None).glyph()
    hmtx["space"] = (SPACE_WIDTH[S.name], 0)

    for name, (fn, unicodes, (left, right)) in GLYPHS.items():
        lsb, rsb = _side_bearing(S, left), _side_bearing(S, right)
        shape = fn(S)
        g = to_ttglyph(shape)
        # Shift so the left extreme sits at x = lsb.
        g.recalcBounds(None)
        dx = lsb - (g.xMin if g.numberOfContours else 0)
        if g.numberOfContours:
            g.coordinates.translate((dx, 0))
            g.recalcBounds(None)
        glyf[name] = g
        hmtx[name] = (g.xMax + rsb, g.xMin)
        for u in unicodes:
            cmap[u] = name

    fb = FontBuilder(M.UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=M.LINE_ASCENT, descent=-M.LINE_DESCENT)
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": S.name,
        "uniqueFontIdentifier": f"{FAMILY}-{S.name};{VERSION}",
        "fullName": f"{FAMILY} {S.name}",
        "psName": f"{FAMILY}-{S.name}",
        "version": f"Version {VERSION}",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fs_selection = (1 << 7)  # USE_TYPO_METRICS
    fs_selection |= (1 << 5) if S.is_bold else (1 << 6)  # BOLD / REGULAR
    fb.setupOS2(
        version=4,
        usWeightClass=S.weight,
        fsSelection=fs_selection,
        sTypoAscender=M.LINE_ASCENT,
        sTypoDescender=-M.LINE_DESCENT,
        sTypoLineGap=0,
        usWinAscent=M.LINE_ASCENT,
        usWinDescent=M.LINE_DESCENT,
        sxHeight=M.X_HEIGHT,
        sCapHeight=M.CAP_HEIGHT,
        achVendID="NONE",
    )
    fb.setupPost()
    fb.font["head"].macStyle = 1 if S.is_bold else 0
    return fb.font


def autohint(font):
    src = io.BytesIO()
    font.save(src)
    hinted = ttfautohint.ttfautohint(
        in_buffer=src.getvalue(),
        hinting_range_min=8,
        hinting_range_max=50,
        increase_x_height=14,
        default_script="latn",
        fallback_script="latn",
        windows_compatibility=True,
        no_info=True,
    )
    return TTFont(io.BytesIO(hinted))


def build(S, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    font = build_unhinted(S)
    paths = {}
    unhinted_path = out_dir / f"{FAMILY}-{S.name}-unhinted.ttf"
    font.save(unhinted_path)
    paths["unhinted"] = unhinted_path
    hinted_path = out_dir / f"{FAMILY}-{S.name}.ttf"
    autohint(TTFont(unhinted_path)).save(hinted_path)
    paths["hinted"] = hinted_path
    return paths

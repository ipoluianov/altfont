"""Build TrueType fonts from the parametric glyph definitions."""

import io
import json
import math
import re
from dataclasses import replace
from pathlib import Path

import ttfautohint
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from . import style as M
from .geometry import to_ttglyph
from .glyphs import GLYPHS, SPACE_WIDTH

FAMILY = "altfont"
VERSION = "0.001"

# Per-glyph pixel-fit adjustments produced by scripts/fit.py:
# {style: {glyph: [lsb delta, width delta, rsb delta]}} in font units.
FIT_FILE = Path(__file__).with_name("fit.json")
# Kerning pairs of base glyphs produced by scripts/kern.py: {style: [[a, b, value]]}.
KERN_FILE = Path(__file__).with_name("kern.json")


def load_fit(S):
    if not FIT_FILE.exists():
        return {}
    return json.loads(FIT_FILE.read_text()).get(S.upright, {})


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


def is_tabular(name):
    return GLYPHS[metrics_glyph(name)].spacing == ("F", "F")


def is_combining(name):
    return GLYPHS[name].spacing == ("Z", "Z")


def combining_center(S):
    """x of combining marks, relative to the following origin: centre of n."""
    return -(S.sb_straight * 2 + S.widths["n"]) / 2


def side_bearings(S, name, width=None):
    """Nominal (lsb, rsb). Tabular glyphs need their ink `width` to center it."""
    kinds = GLYPHS[name].spacing
    if kinds == ("Z", "Z"):
        lsb = round(combining_center(S) - width / 2)
        return lsb, -lsb - width
    if kinds == ("F", "F"):
        lsb = round((S.figure_advance - width) / 2)
        return lsb, S.figure_advance - width - lsb
    by_kind = {"S": S.sb_straight, "R": S.sb_round,
               "T": S.sb_terminal, "D": S.sb_diagonal}
    return tuple(by_kind[k] for k in kinds)


def metrics_glyph(name):
    """The glyph whose spacing, width and fit `name` uses (itself or its base)."""
    return GLYPHS[name].base or name


def draw_glyph(S, name, dw=0):
    """Draw glyph `name` with its width changed by `dw`.

    Returns (glyph, ink width), positioned so that the left extreme of the
    metrics glyph is at x = 0; marks of accented glyphs may stick out.
    """
    key = metrics_glyph(name)
    if dw and key in S.widths:
        S = replace(S, widths={**S.widths, key: S.widths[key] + dw})
    x0, _, x1, _ = GLYPHS[key].fn(S).path.bounds
    g = to_ttglyph(GLYPHS[name].fn(S))
    if g.numberOfContours:
        g.coordinates.translate((-round(x0), 0))
        g.recalcBounds(None)
    return g, round(x1) - round(x0)


def shear(g, angle):
    """Slant a positioned glyph around the middle of the x-height."""
    k = math.tan(math.radians(angle))
    yc = M.X_HEIGHT / 2
    g.coordinates = type(g.coordinates)([(round(x + k * (y - yc)), y) for x, y in g.coordinates])
    g.recalcBounds(None)


VALID_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


def production_name(name):
    """Glyph name stored in the font: source names like "en-cy" become uniXXXX."""
    if VALID_NAME.match(name):
        return name
    return f"uni{GLYPHS[name].unicodes[0]:04X}"


def build_unhinted(S):
    glyph_order = [".notdef", "space"] + list(GLYPHS)
    cmap = {0x0020: "space", 0x00A0: "space"}
    glyf, hmtx = {}, {}
    fit = load_fit(S)

    notdef, w = _notdef(S)
    glyf[".notdef"] = notdef
    hmtx[".notdef"] = (w + 2 * S.sb_straight, 0)
    glyf["space"] = TTGlyphPen(None).glyph()
    hmtx["space"] = (SPACE_WIDTH[S.upright], 0)

    for name, defn in GLYPHS.items():
        dl, dw, dr = fit.get(metrics_glyph(name), (0, 0, 0))
        g, width = draw_glyph(S, name, dw)
        lsb, rsb = side_bearings(S, name, width)
        if is_tabular(name):
            dr = -dl  # keep the advance fixed
        if g.numberOfContours:
            g.coordinates.translate((lsb + dl, 0))
            g.recalcBounds(None)
        if S.is_italic and g.numberOfContours:
            shear(g, S.slant)
        glyf[name] = g
        extra = defn.extra(S) if callable(defn.extra) else defn.extra
        hmtx[name] = (lsb + dl + width + rsb + dr + extra, g.xMin if g.numberOfContours else 0)
        for u in defn.unicodes:
            cmap[u] = name

    for g in glyf.values():
        if g.numberOfContours:
            g.recalcBounds(None)

    rename = {n: production_name(n) for n in GLYPHS}
    glyph_order = [rename.get(n, n) for n in glyph_order]
    assert len(set(glyph_order)) == len(glyph_order), "duplicate production names"
    glyf = {rename.get(n, n): g for n, g in glyf.items()}
    hmtx = {rename.get(n, n): m for n, m in hmtx.items()}
    cmap = {u: rename.get(n, n) for u, n in cmap.items()}

    fb = FontBuilder(M.UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=M.LINE_ASCENT, descent=-M.LINE_DESCENT)
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": S.name,
        "uniqueFontIdentifier": f"{FAMILY}-{S.file_name};{VERSION}",
        "fullName": f"{FAMILY} {S.name}",
        "psName": f"{FAMILY}-{S.file_name}",
        "version": f"Version {VERSION}",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    }, mac=False)
    fs_selection = (1 << 7)  # USE_TYPO_METRICS
    if S.is_bold:
        fs_selection |= 1 << 5   # BOLD
    if S.is_italic:
        fs_selection |= 1 << 0   # ITALIC
    if not (S.is_bold or S.is_italic):
        fs_selection |= 1 << 6   # REGULAR
    fb.setupOS2(
        version=4,
        usWeightClass=S.weight,
        fsSelection=fs_selection,
        sTypoAscender=M.LINE_ASCENT,
        sTypoDescender=-M.LINE_DESCENT,
        sTypoLineGap=0,
        usWinAscent=M.LINE_ASCENT,    # set family-wide in build_family()
        usWinDescent=M.LINE_DESCENT,
        sxHeight=M.X_HEIGHT,
        sCapHeight=M.CAP_HEIGHT,
        achVendID="NONE",
    )
    fb.setupPost()
    fb.font["head"].fontRevision = float(VERSION)
    os2 = fb.font["OS/2"]
    os2.recalcUnicodeRanges(fb.font)
    os2.recalcCodePageRanges(fb.font)
    _setup_stat(fb, S)
    fb.font["head"].macStyle = (1 if S.is_bold else 0) | (2 if S.is_italic else 0)
    if S.is_italic:
        fb.font["post"].italicAngle = -S.slant
        fb.font["hhea"].caretSlopeRise = 1000
        fb.font["hhea"].caretSlopeRun = round(1000 * math.tan(math.radians(S.slant)))
    _force_integer_ppem(fb.font)
    return fb.font


def _setup_stat(fb, S):
    """STAT of a static font: one axis value per axis, the font's own."""
    weight = (dict(value=700, name="Bold") if S.is_bold
              else dict(value=400, name="Regular", flags=0x2, linkedValue=700))
    italic = (dict(value=1, name="Italic") if S.is_italic
              else dict(value=0, name="Roman", flags=0x2, linkedValue=1))
    fb.setupStat([
        dict(tag="wght", name="Weight", values=[weight]),
        dict(tag="ital", name="Italic", values=[italic]),
    ], elidedFallbackName="Regular")


def _force_integer_ppem(font):
    # head.flags bit 3: rasterizers round the scale to whole ppem, so
    # fractional sizes (e.g. 10 pt at 96 dpi = 13.33 px) render exactly as
    # the integer ppem the outlines are fitted for.
    font["head"].flags |= 1 << 3


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
    font = TTFont(io.BytesIO(hinted))
    _force_integer_ppem(font)
    return font


def add_kerning(font, S):
    if not KERN_FILE.exists():
        return
    from .kern import feature_text
    pairs = {(a, b): v for a, b, v in json.loads(KERN_FILE.read_text()).get(S.upright, [])}
    if pairs:
        addOpenTypeFeaturesFromString(font, feature_text(pairs))


def set_win_metrics(fonts):
    """Win metrics only clip, so they cover the tallest glyph of the family.

    Line spacing comes from the typo metrics (USE_TYPO_METRICS) and hhea.
    """
    y_max = max(g.yMax for f in fonts for g in f["glyf"].glyphs.values() if g.numberOfContours)
    y_min = min(g.yMin for f in fonts for g in f["glyf"].glyphs.values() if g.numberOfContours)
    for f in fonts:
        f["OS/2"].usWinAscent = max(M.LINE_ASCENT, y_max)
        f["OS/2"].usWinDescent = max(M.LINE_DESCENT, -y_min)


def build_family(styles, out_dir):
    """Build all styles; returns {style name: {"unhinted": path, "hinted": path}}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fonts = {S.name: build_unhinted(S) for S in styles}
    for S in styles:
        add_kerning(fonts[S.name], S)
    set_win_metrics(list(fonts.values()))
    paths = {}
    for S in styles:
        unhinted = out_dir / f"{FAMILY}-{S.file_name}-unhinted.ttf"
        hinted = out_dir / f"{FAMILY}-{S.file_name}.ttf"
        fonts[S.name].save(unhinted)
        autohint(TTFont(unhinted)).save(hinted)
        paths[S.name] = {"unhinted": unhinted, "hinted": hinted}
    return paths

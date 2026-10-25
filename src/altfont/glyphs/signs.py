"""Latin-1 signs, superscripts, subscripts, fractions, general punctuation, currency."""

from dataclasses import replace

from ..geometry import ellipse, rect, ring, slant_half_width, slanted, union
from ..style import CAP_HEIGHT, OVERSHOOT, X_HEIGHT
from .common import GLYPHS, d_bowl, glyph, hook_up
from .latin import M_, R, T, W, Y, a, c, c_shape, o, s_shape
from .symbols import (AXIS, PAREN_BOTTOM, PAREN_TOP, eight, exclam, figure_width, five,
                      four, nine, one, pdot, percent, question, seven, six_, three,
                      two, zero)

CAP_TOP = CAP_HEIGHT + OVERSHOOT
DIGITS = [zero, one, two, three, four, five, six_, seven, eight, nine]


def small_style(S, scale):
    """A style whose strokes, scaled by `scale`, end up ~80 % of the full weight."""
    k = 0.8 / scale
    return replace(S, vstem=round(S.vstem * k), hstem=round(S.hstem * k),
                   hstem_tight=round(S.hstem_tight * k))


def small(shape_fn, S, scale, y):
    """Draw shape_fn at reduced size with its baseline at y."""
    return shape_fn(small_style(S, scale)).transform(scale, 0, 0, scale, 0, y)


SUP_SCALE = 0.60
SUP_Y = CAP_HEIGHT - round(CAP_HEIGHT * SUP_SCALE)   # superscript top at cap height
SUB_Y = -150


# --- Latin-1 ---------------------------------------------------------------------------

@glyph("exclamdown", [0x00A1], ("S", "S"))
def exclamdown(S):
    p = pdot(S)
    return exclam(S).rotate180(p / 2, CAP_HEIGHT / 2).translate(0, X_HEIGHT - CAP_HEIGHT)


@glyph("questiondown", [0x00BF], ("R", "T"))
def questiondown(S):
    shape = question(S)
    x0, _, x1, _ = shape.path.bounds
    return shape.rotate180((x0 + x1) / 2, CAP_HEIGHT / 2).translate(0, X_HEIGHT - CAP_HEIGHT)


@glyph("cent", [0x00A2], ("R", "R"))
def cent(S):
    w, v = S.widths["c"], S.vstem
    cx = w * 0.52
    return c(S) | rect(cx - v / 2, -200, cx + v / 2, X_HEIGHT + 200)


@glyph("sterling", [0x00A3], ("T", "T"))
def sterling(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    x = round(w * 0.26)
    hook, center = hook_up(S, x, round(w * 0.92), CAP_TOP, ry=round(CAP_HEIGHT * 0.24))
    y = round(CAP_HEIGHT * 0.42)
    return union(rect(x, 0, x + v, center + 1), hook, rect(0, 0, w, h),
                 rect(round(w * 0.05), y, round(w * 0.72), y + h))


@glyph("currency", [0x00A4], ("T", "T"))
def currency(S):
    v = S.vstem
    r = 300 if not S.is_bold else 340
    cx, cy = r + 140, AXIS
    body = ring(cx - r, cy - r, cx + r, cy + r, S.round_vstem, S.hstem)
    d = r * 0.72
    stubs = union(*(slanted(*sorted_pts(cx + sx * d, cy + sy * d, cx + sx * (d + 170), cy + sy * (d + 170)), v)
                    for sx in (-1, 1) for sy in (-1, 1)))
    return body | stubs


def sorted_pts(x0, y0, x1, y1):
    """Order two points bottom first, as `slanted` expects."""
    return (x0, y0, x1, y1) if y0 < y1 else (x1, y1, x0, y0)


@glyph("yen", [0x00A5], ("D", "D"))
def yen(S):
    w, h = S.widths["Y"], S.hstem
    y1, y2 = round(CAP_HEIGHT * 0.22), round(CAP_HEIGHT * 0.40)
    return union(Y(S), rect(w * 0.2, y1, w * 0.8, y1 + h), rect(w * 0.2, y2, w * 0.8, y2 + h))


@glyph("brokenbar", [0x00A6], ("S", "S"))
def brokenbar(S):
    v = S.vstem
    return rect(0, PAREN_BOTTOM, v, AXIS - 130) | rect(0, AXIS + 130, v, PAREN_TOP)


@glyph("section", [0x00A7], ("R", "R"))
def section(S):
    w = 860 if not S.is_bold else 1000
    st = S.tight
    upper = s_shape(st, w, 1000).translate(0, 600)
    lower = s_shape(st, w, 1000).translate(0, -300)
    return upper | lower


def _encircled(S, inner):
    d = CAP_HEIGHT + 200
    v = S.vstem * 0.8
    body = ring(0, -OVERSHOOT - 100, d, d - OVERSHOOT - 100, v, S.hstem * 0.8)
    x0, y0, x1, y1 = inner.path.bounds
    dx = d / 2 - (x0 + x1) / 2
    dy = (d - 200) / 2 - OVERSHOOT - (y0 + y1) / 2
    return body | inner.translate(dx, dy)


@glyph("copyright", [0x00A9], ("R", "R"))
def copyright(S):
    scale = 0.52
    return _encircled(S, small(lambda s: c_shape(s, 1300, CAP_HEIGHT), S, scale, 0))


@glyph("registered", [0x00AE], ("R", "R"))
def registered(S):
    scale = 0.52
    return _encircled(S, small(R, S, scale, 0))


def _ordinal(S, letter):
    scale = 0.62
    shape = small(letter, S, scale, SUP_Y + 120)
    x0, _, x1, _ = shape.path.bounds
    return shape | rect(x0, SUP_Y - 60, x1, SUP_Y - 60 + S.hstem)


@glyph("ordfeminine", [0x00AA], ("T", "T"))
def ordfeminine(S):
    return _ordinal(S, a)


@glyph("ordmasculine", [0x00BA], ("T", "T"))
def ordmasculine(S):
    return _ordinal(S, o)


@glyph("logicalnot", [0x00AC], ("F", "F"))
def logicalnot(S):
    v, h = S.vstem, S.hstem
    w = 1000
    return rect(0, AXIS, w, AXIS + h) | rect(w - v, AXIS - 300, w, AXIS + h)


@glyph("paragraph", [0x00B6], ("T", "S"))
def paragraph(S):
    v, h = S.vstem, S.hstem
    x1 = 520 if not S.is_bold else 600
    x2 = x1 + (300 if not S.is_bold else 360)
    bottom = round(CAP_HEIGHT * 0.40)
    blob = ellipse(0, bottom, 2 * x1, CAP_HEIGHT) & rect(0, bottom, x1, CAP_HEIGHT)
    return union(blob, rect(x1, -300, x1 + v, CAP_HEIGHT), rect(x2, -300, x2 + v, CAP_HEIGHT),
                 rect(x1, CAP_HEIGHT - h, x2 + v, CAP_HEIGHT))


# --- Superscripts, subscripts, fractions ------------------------------------------------

SUPERSCRIPTS = {0x2070: 0, 0x00B9: 1, 0x00B2: 2, 0x00B3: 3, 0x2074: 4, 0x2075: 5,
                0x2076: 6, 0x2077: 7, 0x2078: 8, 0x2079: 9}


def _register_digit_forms():
    for cp, d in SUPERSCRIPTS.items():
        glyph(f"uni{cp:04X}", [cp], ("T", "T"))(
            lambda S, d=d: small(DIGITS[d], S, SUP_SCALE, SUP_Y))
    for d in range(10):
        cp = 0x2080 + d
        glyph(f"uni{cp:04X}", [cp], ("T", "T"))(
            lambda S, d=d: small(DIGITS[d], S, SUP_SCALE, SUB_Y))


_register_digit_forms()


def fraction_slash(S, x, height=CAP_HEIGHT):
    t = S.vstem * 0.8
    w = 520
    hw = slant_half_width(w, height, t)
    return slanted(x + hw, 0, x + w - hw, height, t)


@glyph("fraction", [0x2044], ("D", "D"))
def fraction(S):
    return fraction_slash(S, 0)


FRACTIONS = {0x00BC: (1, 4), 0x00BD: (1, 2), 0x00BE: (3, 4), 0x2153: (1, 3),
             0x2154: (2, 3), 0x215B: (1, 8), 0x215C: (3, 8), 0x215D: (5, 8), 0x215E: (7, 8)}
FRAC_SCALE = 0.52


def _fraction_glyph(num, den):
    def fn(S):
        top = small(DIGITS[num], S, FRAC_SCALE, CAP_HEIGHT - round(CAP_HEIGHT * FRAC_SCALE))
        nw = top.path.bounds[2]
        slash = fraction_slash(S, nw - 60)
        bottom = small(DIGITS[den], S, FRAC_SCALE, 0)
        return union(top, slash, bottom.translate(nw + 400))
    return fn


for _cp, (_n, _d) in FRACTIONS.items():
    glyph(f"uni{_cp:04X}", [_cp], ("T", "T"))(_fraction_glyph(_n, _d))


# --- General punctuation --------------------------------------------------------------------

@glyph("perthousand", [0x2030], ("R", "R"))
def perthousand(S):
    shape = percent(S)
    x1 = shape.path.bounds[2]
    w = 1500 if not S.is_bold else 1700
    extra = ring(x1 + 80, -OVERSHOOT, x1 + 80 + w * 0.38, CAP_HEIGHT * 0.48, S.round_vstem, S.hstem)
    return shape | extra


@glyph("dagger", [0x2020], ("T", "T"))
def dagger(S):
    v, h = S.vstem, S.hstem
    w = 860
    x = (w - v) / 2
    y = round(CAP_HEIGHT * 0.66)
    return rect(x, -300, x + v, CAP_HEIGHT) | rect(0, y, w, y + h)


@glyph("daggerdbl", [0x2021], ("T", "T"))
def daggerdbl(S):
    h = S.hstem
    w = 860
    return dagger(S) | rect(0, 120, w, 120 + h)


@glyph("minute", [0x2032], ("T", "T"))
def minute(S):
    return slanted(40, CAP_HEIGHT - 460, 200, CAP_HEIGHT, S.vstem)


@glyph("second", [0x2033], ("T", "T"))
def second(S):
    return minute(S) | minute(S).translate(S.vstem + 160)


@glyph("exclamdbl", [0x203C], ("S", "S"))
def exclamdbl(S):
    return exclam(S) | exclam(S).translate(pdot(S) + 220)


@glyph("trademark", [0x2122], ("T", "T"))
def trademark(S):
    scale = 0.50
    y = CAP_HEIGHT - round(CAP_HEIGHT * scale)
    t = small(T, S, scale, y)
    m = small(M_, S, scale, y)
    return t | m.translate(t.path.bounds[2] + 90)


# --- Currency ------------------------------------------------------------------------------

@glyph("uni20B4", [0x20B4], ("R", "R"))
def hryvnia(S):
    w, h = figure_width(S), S.hstem
    body = s_shape(S, w, CAP_HEIGHT).mirror_x(w / 2)
    y1, y2 = round(CAP_HEIGHT * 0.36), round(CAP_HEIGHT * 0.58)
    return union(body, rect(0, y1, w, y1 + h), rect(0, y2, w, y2 + h))


@glyph("uni20B8", [0x20B8], ("T", "T"))
def tenge(S):
    w, v, h = figure_width(S) + 80, S.vstem, S.hstem
    x = (w - v) / 2
    y = round(CAP_HEIGHT * 0.70)
    return union(rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT), rect(0, y, w, y + h), rect(x, 0, x + v, y + h))


@glyph("uni20BA", [0x20BA], ("T", "R"))
def lira(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    x = round(w * 0.30)
    bars = union(slanted(0, CAP_HEIGHT * 0.36, w * 0.75, CAP_HEIGHT * 0.56, h),
                 slanted(0, CAP_HEIGHT * 0.56, w * 0.75, CAP_HEIGHT * 0.76, h))
    foot = ring(x - (w - x), -OVERSHOOT, w, CAP_HEIGHT * 0.7, S.round_vstem, h) & rect(x, -OVERSHOOT, w, CAP_HEIGHT * 0.35)
    return union(rect(x, CAP_HEIGHT * 0.3, x + v, CAP_HEIGHT), bars & rect(0, 0, w, CAP_HEIGHT), foot,
                 rect(x, 0, x + v, CAP_HEIGHT * 0.35))


@glyph("uni20A9", [0x20A9], ("D", "D"))
def won(S):
    w, h = S.widths["W"], S.hstem
    y1, y2 = round(CAP_HEIGHT * 0.38), round(CAP_HEIGHT * 0.58)
    return union(W(S), rect(0, y1, w, y1 + h), rect(0, y2, w, y2 + h))


@glyph("dong", [0x20AB], ("R", "T"))
def dong(S):
    shape = GLYPHS["dcroat"].fn(S)
    x0, _, x1, _ = shape.path.bounds
    return shape | rect(x0, -300, x1, -300 + S.hstem)


@glyph("uni20B9", [0x20B9], ("T", "T"))
def rupee(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    y2 = round(CAP_HEIGHT * 0.70)
    bowl_bottom = round(CAP_HEIGHT * 0.42)
    t = v
    hw = slant_half_width(w * 0.5, bowl_bottom, t)
    leg = slanted(w * 0.78 - hw, 0, w * 0.22, bowl_bottom + h / 2, t) & rect(0, 0, w, CAP_HEIGHT)
    bowl = d_bowl(S, w * 0.22, w * 0.86, bowl_bottom, CAP_HEIGHT)
    return union(rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT), rect(0, y2, w, y2 + h),
                 bowl, rect(0, bowl_bottom, w * 0.3, bowl_bottom + h), leg)


@glyph("uni20AE", [0x20AE], ("T", "T"))
def tugrik(S):
    w, h = S.widths["T"], S.hstem
    t = T(S)
    return union(t, slanted(w * 0.2, CAP_HEIGHT * 0.25, w * 0.8, CAP_HEIGHT * 0.45, h),
                 slanted(w * 0.2, CAP_HEIGHT * 0.45, w * 0.8, CAP_HEIGHT * 0.65, h))


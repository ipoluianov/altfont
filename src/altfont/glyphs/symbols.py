"""Figures, punctuation and symbols."""

from ..geometry import ellipse, polygon, rect, ring, slant_half_width, slanted, union
from ..style import ASCENDER, CAP_HEIGHT, OVERSHOOT, X_HEIGHT
from .common import d_bowl, glyph, hook_up
from .marks import comma_shape, mark_grave
from .latin import c_shape, s_shape, x_shape

CAP_TOP = CAP_HEIGHT + OVERSHOOT
AXIS = 630                   # math axis: centre of + = < > ~
HYPHEN_Y = 540               # centre of hyphen and dashes
PAREN_TOP, PAREN_BOTTOM = 1720, -380


def figure_width(S):
    """Ink width of the tabular figures."""
    return S.figure_advance - (220 if S.is_bold else 260)


def pdot(S):
    """Size of the punctuation dot."""
    return round(S.vstem * 1.12)


def square(x, y, size):
    return rect(x, y, x + size, y + size)


# --- Figures -------------------------------------------------------------------

def lower_bowl(S, w, top):
    """Bowl of 3 and 5: right half, top stroke from 40 % of the width, foot terminal."""
    center = (top - OVERSHOOT) / 2
    r = ring(0, -OVERSHOOT, w, top, S.round_vstem, S.hstem)
    keep = (rect(w * 0.40, center, w, top) | rect(w * 0.5, -OVERSHOOT, w, center)
            | rect(0, -OVERSHOOT, w * 0.5, CAP_HEIGHT * 0.20))
    return r & keep


def six(S, w):
    rv = S.round_vstem
    bowl_top = round(CAP_HEIGHT * 0.62)
    hook, center = hook_up(S, 0, round(w * 0.88), CAP_TOP, ry=round(CAP_HEIGHT * 0.25))
    return union(
        ring(0, -OVERSHOOT, w, bowl_top, rv, S.hstem),
        rect(0, (bowl_top - OVERSHOOT) / 2, rv, center + 1),
        hook,
    )


@glyph("zero", [0x0030], ("F", "F"))
def zero(S):
    # Narrower and squarer than O.
    return ring(0, -OVERSHOOT, figure_width(S), CAP_TOP, S.round_vstem, S.hstem, k=0.66)


@glyph("one", [0x0031], ("F", "F"))
def one(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    x = round(w * 0.56 - v / 2)
    flag = slanted(w * 0.14, CAP_HEIGHT * 0.76, x + v * 0.5, CAP_HEIGHT, v * 0.95)
    return union(
        rect(x, 0, x + v, CAP_HEIGHT),
        flag & rect(0, 0, x + v, CAP_HEIGHT),
        rect(round(w * 0.14), 0, round(w * 0.96), h),  # base bar: unlike l and I
    )


@glyph("two", [0x0032], ("F", "F"))
def two(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    ry = round(CAP_HEIGHT * 0.28)
    r = ring(0, CAP_TOP - 2 * ry, w, CAP_TOP, S.round_vstem, h)
    center = CAP_TOP - ry
    arch = r & rect(0, center, w, CAP_TOP)
    diagonal = slanted(v * 0.6, h * 0.5, w - S.round_vstem * 0.5, center, v)
    return union(arch, diagonal & rect(0, 0, w, CAP_HEIGHT), rect(0, 0, w, h))


@glyph("three", [0x0033], ("F", "F"))
def three(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    bowl_top = round(CAP_HEIGHT * 0.60)
    # Flat top tells 3 apart from З.
    diagonal = slanted(w * 0.46, bowl_top - h, w * 0.90 - v * 0.6, CAP_HEIGHT - h / 2, v)
    return union(
        rect(round(w * 0.06), CAP_HEIGHT - h, round(w * 0.92), CAP_HEIGHT),
        diagonal & rect(0, bowl_top - h, w * 0.92, CAP_HEIGHT),
        lower_bowl(S, w, bowl_top),
    )


@glyph("four", [0x0034], ("F", "F"))
def four(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    x = round(w * 0.66)
    bar_y = round(CAP_HEIGHT * 0.26)
    hw = slant_half_width(x, CAP_HEIGHT - bar_y, v)
    diagonal = slanted(hw, bar_y, x + v * 0.5, CAP_HEIGHT, v) & rect(0, bar_y, x + v, CAP_HEIGHT)
    return union(rect(x, 0, x + v, CAP_HEIGHT), rect(0, bar_y, w, bar_y + h), diagonal)


@glyph("five", [0x0035], ("F", "F"))
def five(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    bowl_top = round(CAP_HEIGHT * 0.60)
    x = round(w * 0.10)
    return union(
        rect(x, bowl_top - h, x + v, CAP_HEIGHT),
        rect(x, CAP_HEIGHT - h, round(w * 0.92), CAP_HEIGHT),
        rect(x, bowl_top - h, w * 0.5, bowl_top),   # joins the stem to the bowl
        lower_bowl(S, w, bowl_top),
    )


@glyph("six", [0x0036], ("F", "F"))
def six_(S):
    return six(S, figure_width(S))


@glyph("seven", [0x0037], ("F", "F"))
def seven(S):
    w, v, h = figure_width(S), S.vstem, S.hstem
    hw = slant_half_width(w * 0.6, CAP_HEIGHT, v)
    diagonal = slanted(w * 0.30, 0, w - hw, CAP_HEIGHT - h / 2, v) & rect(0, 0, w, CAP_HEIGHT)
    return rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT) | diagonal


@glyph("eight", [0x0038], ("F", "F"))
def eight(S):
    w, h, rv = figure_width(S), S.hstem, S.round_vstem
    mid = round(CAP_HEIGHT * 0.54)
    return (ring(w * 0.07, mid - h / 2, w * 0.93, CAP_TOP, rv, h)
            | ring(0, -OVERSHOOT, w, mid + h / 2, rv, h))


@glyph("nine", [0x0039], ("F", "F"))
def nine(S):
    w = figure_width(S)
    return six(S, w).rotate180(w / 2, CAP_HEIGHT / 2)


# --- Punctuation -----------------------------------------------------------------

@glyph("period", [0x002E], ("S", "S"))
def period(S):
    return square(0, 0, pdot(S))


@glyph("comma", [0x002C], ("S", "S"))
def comma(S):
    return comma_shape(S)


@glyph("colon", [0x003A], ("S", "S"))
def colon(S):
    p = pdot(S)
    return square(0, 0, p) | square(0, X_HEIGHT - p, p)


@glyph("semicolon", [0x003B, 0x037E], ("S", "S"))
def semicolon(S):
    p = pdot(S)
    return comma_shape(S) | square(0, X_HEIGHT - p, p)


@glyph("ellipsis", [0x2026], ("S", "S"))
def ellipsis(S):
    p = pdot(S)
    step = p + 240
    return union(*(square(i * step, 0, p) for i in range(3)))


@glyph("exclam", [0x0021], ("S", "S"))
def exclam(S):
    p, v = pdot(S), S.vstem
    x = (p - v) / 2
    return rect(x, p + 240, x + v, CAP_HEIGHT) | square(0, 0, p)


@glyph("question", [0x003F], ("T", "R"))
def question(S):
    v, h, rv = S.vstem, S.hstem, S.round_vstem
    w = 860 if not S.is_bold else 980
    p = pdot(S)
    ry = round(CAP_HEIGHT * 0.27)
    bottom = CAP_TOP - 2 * ry
    center = CAP_TOP - ry
    r = ring(0, bottom, w, CAP_TOP, rv, h)
    curl = r & (rect(0, center, w, CAP_TOP) | rect(w / 2, bottom, w, center))
    cx = w / 2
    return union(
        curl,
        rect(cx - v / 2, p + 240, cx + v / 2, bottom + h),
        square(cx - p / 2, 0, p),
    )


@glyph("quotesingle", [0x0027], ("S", "S"))
def quotesingle(S):
    return rect(0, CAP_HEIGHT - 440, S.vstem, CAP_HEIGHT)


@glyph("quotedbl", [0x0022], ("S", "S"))
def quotedbl(S):
    v = S.vstem
    gap = round(v * 1.4)
    return rect(0, CAP_HEIGHT - 440, v, CAP_HEIGHT) | rect(v + gap, CAP_HEIGHT - 440, 2 * v + gap, CAP_HEIGHT)


def _quote_right(S):
    return comma_shape(S).translate(0, CAP_HEIGHT - pdot(S))


def _quote_left(S):
    p = pdot(S)
    return comma_shape(S).rotate180(p / 2, p / 2).translate(0, CAP_HEIGHT - p - 280)


def _pair(shape, S):
    step = pdot(S) * 1.9
    return shape | shape.translate(step)


@glyph("quoteright", [0x2019], ("S", "S"))
def quoteright(S):
    return _quote_right(S)


@glyph("quoteleft", [0x2018], ("S", "S"))
def quoteleft(S):
    return _quote_left(S)


@glyph("quotesinglbase", [0x201A], ("S", "S"))
def quotesinglbase(S):
    return comma_shape(S)


@glyph("quotedblright", [0x201D], ("S", "S"))
def quotedblright(S):
    return _pair(_quote_right(S), S)


@glyph("quotedblleft", [0x201C], ("S", "S"))
def quotedblleft(S):
    return _pair(_quote_left(S), S)


@glyph("quotedblbase", [0x201E], ("S", "S"))
def quotedblbase(S):
    return _pair(comma_shape(S), S)


def chevron(S, dx, height, cy, pointing_left=True):
    """< shape whose centre lines span `dx` horizontally.

    The strokes are shallow, so they get the horizontal stem width; the
    outer width grows with the stroke so the angle stays the same in Bold.
    """
    t = S.hstem
    hw = slant_half_width(dx, height / 2, t)
    w = dx + 2 * hw
    lower = slanted(dx + hw, cy - height / 2, hw, cy, t)
    upper = slanted(hw, cy, dx + hw, cy + height / 2, t)
    shape = (lower | upper) & rect(0, cy - height / 2, w, cy + height / 2)
    return shape if pointing_left else shape.mirror_x(w / 2)


def _guillemet(S, double, left):
    dx, height = (240, 560) if not S.is_bold else (300, 620)
    shape = chevron(S, dx, height, X_HEIGHT / 2, left)
    if double:
        x0, _, x1, _ = shape.path.bounds
        shape = shape | shape.translate((x1 - x0) * 0.75)
    return shape


@glyph("guillemetleft", [0x00AB], ("D", "D"))
def guillemetleft(S):
    return _guillemet(S, True, True)


@glyph("guillemetright", [0x00BB], ("D", "D"))
def guillemetright(S):
    return _guillemet(S, True, False)


@glyph("guilsinglleft", [0x2039], ("D", "D"))
def guilsinglleft(S):
    return _guillemet(S, False, True)


@glyph("guilsinglright", [0x203A], ("D", "D"))
def guilsinglright(S):
    return _guillemet(S, False, False)


@glyph("hyphen", [0x002D, 0x2010, 0x2011], ("T", "T"))
def hyphen(S):
    h = S.hstem
    return rect(0, HYPHEN_Y - h / 2, 520 if not S.is_bold else 560, HYPHEN_Y + h / 2)


@glyph("endash", [0x2013, 0x2012], ("T", "T"))
def endash(S):
    h = S.hstem
    return rect(0, HYPHEN_Y - h / 2, 1000, HYPHEN_Y + h / 2)


@glyph("emdash", [0x2014], ("T", "T"))
def emdash(S):
    h = S.hstem
    return rect(0, HYPHEN_Y - h / 2, 1880, HYPHEN_Y + h / 2)


@glyph("underscore", [0x005F], ("T", "T"))
def underscore(S):
    return rect(0, -300, 1000, -300 + S.hstem)


@glyph("parenleft", [0x0028], ("R", "T"))
def parenleft(S):
    w = 440 if not S.is_bold else 520
    r = ring(0, PAREN_BOTTOM, 2 * w, PAREN_TOP, S.vstem, S.hstem, k=0.62)
    return r & rect(0, PAREN_BOTTOM, w, PAREN_TOP)


@glyph("parenright", [0x0029], ("T", "R"))
def parenright(S):
    w = 440 if not S.is_bold else 520
    return parenleft(S).mirror_x(w / 2)


@glyph("bracketleft", [0x005B], ("S", "T"))
def bracketleft(S):
    v, h = S.vstem, S.hstem
    w = 400 if not S.is_bold else 480
    return union(rect(0, PAREN_BOTTOM, v, PAREN_TOP), rect(0, PAREN_TOP - h, w, PAREN_TOP),
                 rect(0, PAREN_BOTTOM, w, PAREN_BOTTOM + h))


@glyph("bracketright", [0x005D], ("T", "S"))
def bracketright(S):
    w = 400 if not S.is_bold else 480
    return bracketleft(S).mirror_x(w / 2)


@glyph("braceleft", [0x007B], ("T", "T"))
def braceleft(S):
    v, h = S.vstem, S.hstem
    x = 200 if not S.is_bold else 240
    mid = (PAREN_TOP + PAREN_BOTTOM) / 2
    arm = 280 if not S.is_bold else 320
    point = polygon([(0, mid - h / 2), (x + v, mid - 220), (x + v, mid + 220), (0, mid + h / 2)])
    return union(
        rect(x, PAREN_BOTTOM, x + v, PAREN_TOP),
        rect(x, PAREN_TOP - h, x + v + arm, PAREN_TOP),
        rect(x, PAREN_BOTTOM, x + v + arm, PAREN_BOTTOM + h),
        point,
    )


@glyph("braceright", [0x007D], ("T", "T"))
def braceright(S):
    shape = braceleft(S)
    x0, _, x1, _ = shape.path.bounds
    return shape.mirror_x((x0 + x1) / 2)


@glyph("slash", [0x002F], ("D", "D"))
def slash(S):
    w, v = (640, S.vstem) if not S.is_bold else (760, S.vstem)
    hw = slant_half_width(w, ASCENDER + 260, v)
    return slanted(hw, -260, w - hw, ASCENDER, v) & rect(0, -260, w, ASCENDER)


@glyph("backslash", [0x005C], ("D", "D"))
def backslash(S):
    w = 640 if not S.is_bold else 760
    return slash(S).mirror_x(w / 2)


@glyph("bar", [0x007C], ("S", "S"))
def bar(S):
    return rect(0, PAREN_BOTTOM, S.vstem, PAREN_TOP)


# --- Symbols -------------------------------------------------------------------

@glyph("numbersign", [0x0023], ("T", "T"))
def numbersign(S):
    v, h = S.vstem, S.hstem
    w = 1100 if not S.is_bold else 1300
    x1, x2 = round(w * 0.22), round(w * 0.78 - v)
    top = round(CAP_HEIGHT * 0.94)
    y1, y2 = round(CAP_HEIGHT * 0.26), round(CAP_HEIGHT * 0.66 - h)
    return union(rect(x1, 0, x1 + v, top), rect(x2, 0, x2 + v, top),
                 rect(0, y1, w, y1 + h), rect(0, y2, w, y2 + h))


@glyph("dollar", [0x0024], ("R", "R"))
def dollar(S):
    v = S.vstem
    w = 980 if not S.is_bold else 1120
    cx = w / 2
    return s_shape(S, w, CAP_HEIGHT) | rect(cx - v / 2, -200, cx + v / 2, CAP_HEIGHT + 200)


@glyph("percent", [0x0025], ("R", "R"))
def percent(S):
    v, h, rv = S.vstem, S.hstem, S.round_vstem
    w = 1500 if not S.is_bold else 1700
    hw = slant_half_width(w * 0.6, CAP_HEIGHT, v)
    return union(
        ring(0, CAP_HEIGHT * 0.52, w * 0.38, CAP_TOP, rv, h),
        ring(w * 0.62, -OVERSHOOT, w, CAP_HEIGHT * 0.48, rv, h),
        slanted(w * 0.20 + hw, 0, w * 0.80 - hw, CAP_HEIGHT, v),
    )


@glyph("ampersand", [0x0026], ("R", "D"))
def ampersand(S):
    v, h, rv = S.vstem, S.hstem, S.round_vstem
    w = 1300 if not S.is_bold else 1480
    lower_top = round(CAP_HEIGHT * 0.60)
    lower = ring(0, -OVERSHOOT, w * 0.80, lower_top, rv, h) - rect(w * 0.45, CAP_HEIGHT * 0.20, w, lower_top + 1)
    upper = ring(w * 0.10, CAP_HEIGHT * 0.50, w * 0.62, CAP_TOP, rv, h)
    hw = slant_half_width(w * 0.6, CAP_HEIGHT * 0.55, v)
    leg = slanted(w - hw, 0, w * 0.24, CAP_HEIGHT * 0.58, v) & rect(0, 0, w, CAP_HEIGHT)
    tail = slanted(w * 0.70, CAP_HEIGHT * 0.12, w * 0.92, CAP_HEIGHT * 0.48, v)
    return union(lower, upper, leg, tail & rect(0, 0, w, CAP_HEIGHT))


@glyph("at", [0x0040], ("R", "R"))
def at(S):
    v, h, rv = S.vstem, S.hstem, S.round_vstem
    w = 1700 if not S.is_bold else 1880
    bottom, top = -320, CAP_HEIGHT
    outer = ring(0, bottom, w, top, rv, h) - rect(w * 0.5, bottom - 1, w + 1, CAP_HEIGHT * 0.30)
    ix0, ix1 = w * 0.30, w * 0.66
    iy0, iy1 = CAP_HEIGHT * 0.22, CAP_HEIGHT * 0.74
    inner = ring(ix0, iy0, ix1, iy1, rv, h)
    x = round(ix1 - v)
    return union(
        outer, inner,
        rect(x, iy0, x + v, iy1),                      # stem of the inner a
        rect(x, iy0, w - rv / 2, iy0 + h),             # foot to the outer ring
        rect(w - rv, iy0, w, CAP_HEIGHT * 0.30 + 1),   # join to the ring's end
    )


@glyph("asterisk", [0x002A], ("T", "T"))
def asterisk(S):
    v = S.vstem * 0.9
    r = 300 if not S.is_bold else 330
    cx, cy = r * 0.87, CAP_HEIGHT - r
    dx, dy = r * 0.866, r * 0.5
    return union(
        rect(cx - v / 2, cy - r, cx + v / 2, cy + r),
        slanted(cx - dx, cy - dy, cx + dx, cy + dy, v),
        slanted(cx + dx, cy - dy, cx - dx, cy + dy, v),
    )


@glyph("plus", [0x002B], ("F", "F"))
def plus(S):
    v, h = S.vstem, S.hstem
    w = 1000
    return rect(0, AXIS - h / 2, w, AXIS + h / 2) | rect(w / 2 - v / 2, AXIS - w / 2, w / 2 + v / 2, AXIS + w / 2)


@glyph("minus", [0x2212], ("F", "F"))
def minus(S):
    h = S.hstem
    return rect(0, AXIS - h / 2, 1000, AXIS + h / 2)


@glyph("equal", [0x003D], ("F", "F"))
def equal(S):
    h = S.hstem
    d = 170 if not S.is_bold else 200
    return rect(0, AXIS + d - h / 2, 1000, AXIS + d + h / 2) | rect(0, AXIS - d - h / 2, 1000, AXIS - d + h / 2)


@glyph("less", [0x003C], ("F", "F"))
def less(S):
    return chevron(S, 680, 760, AXIS, True)


@glyph("greater", [0x003E], ("F", "F"))
def greater(S):
    return chevron(S, 680, 760, AXIS, False)


@glyph("asciitilde", [0x007E], ("F", "F"))
def asciitilde(S):
    v, h = S.vstem * 0.95, S.hstem
    w = 1000
    left = ring(0, AXIS - 150, w * 0.56, AXIS + 150, v, h) & rect(0, AXIS, w * 0.56, AXIS + 150)
    right = ring(w * 0.44, AXIS - 150, w, AXIS + 150, v, h) & rect(w * 0.44, AXIS - 150, w, AXIS)
    return left | right


@glyph("asciicircum", [0x005E], ("D", "D"))
def asciicircum(S):
    v = S.vstem
    w = 900
    bottom = CAP_HEIGHT * 0.58
    hw = slant_half_width(w / 2, CAP_HEIGHT - bottom, v)
    strokes = slanted(hw, bottom, w / 2, CAP_HEIGHT, v) | slanted(w - hw, bottom, w / 2, CAP_HEIGHT, v)
    return strokes & rect(0, bottom, w, CAP_HEIGHT)


@glyph("grave", [0x0060], ("T", "T"))
def grave(S):
    return mark_grave(S, 0, CAP_HEIGHT + 140, cap=True)


@glyph("bullet", [0x2022], ("R", "R"))
def bullet(S):
    r = 190 if not S.is_bold else 230
    return ellipse(0, AXIS - r, 2 * r, AXIS + r, k=0.64)


@glyph("periodcentered", [0x00B7, 0x0387], ("S", "S"))
def periodcentered(S):
    p = pdot(S)
    return square(0, AXIS - p / 2, p)


@glyph("degree", [0x00B0], ("R", "R"))
def degree(S):
    d = 520 if not S.is_bold else 600
    return ring(0, CAP_HEIGHT - d, d, CAP_HEIGHT, S.vstem * 0.9, S.hstem * 0.9)


@glyph("multiply", [0x00D7], ("F", "F"))
def multiply(S):
    return x_shape(S, 720, 720).translate(0, AXIS - 360)


@glyph("divide", [0x00F7], ("F", "F"))
def divide(S):
    h, p = S.hstem, pdot(S)
    w = 1000
    return union(rect(0, AXIS - h / 2, w, AXIS + h / 2),
                 square(w / 2 - p / 2, AXIS + 220, p),
                 square(w / 2 - p / 2, AXIS - 220 - p, p))


@glyph("plusminus", [0x00B1], ("F", "F"))
def plusminus(S):
    v, h = S.vstem, S.hstem
    w = 1000
    cy = AXIS + 140
    return union(rect(0, cy - h / 2, w, cy + h / 2),
                 rect(w / 2 - v / 2, cy - 420, w / 2 + v / 2, cy + 420),
                 rect(0, AXIS - 480, w, AXIS - 480 + h))


@glyph("numero", [0x2116], ("S", "T"))
def numero(S):
    v, h, rv = S.vstem, S.hstem, S.round_vstem
    wn = 1060 if not S.is_bold else 1220
    diagonal = slanted(wn - v, 0, v, CAP_HEIGHT, v * 0.95) & rect(v, 0, wn - v, CAP_HEIGHT)
    ox = wn + 120
    ow = 440 if not S.is_bold else 520
    return union(
        rect(0, 0, v, CAP_HEIGHT), rect(wn - v, 0, wn, CAP_HEIGHT), diagonal,
        ring(ox, CAP_HEIGHT * 0.44, ox + ow, CAP_HEIGHT, rv, h),
        rect(ox, CAP_HEIGHT * 0.24, ox + ow, CAP_HEIGHT * 0.24 + h),
    )


@glyph("Euro", [0x20AC], ("T", "R"))
def Euro(S):
    h = S.hstem
    w = figure_width(S) + 120
    shift = 140
    y1, y2 = round(CAP_HEIGHT * 0.38), round(CAP_HEIGHT * 0.58)
    return union(
        c_shape(S, w - shift, CAP_HEIGHT).translate(shift),
        rect(0, y1, round(w * 0.66), y1 + h),
        rect(0, y2, round(w * 0.70), y2 + h),
    )


@glyph("ruble", [0x20BD], ("T", "R"))
def ruble(S):
    v, h = S.vstem, S.hstem
    w = figure_width(S)
    x = round(w * 0.18)
    bowl_bottom = round(CAP_HEIGHT * 0.42)
    bar_y = round(CAP_HEIGHT * 0.20)
    return union(
        rect(x, 0, x + v, CAP_HEIGHT),
        d_bowl(S, x, w, bowl_bottom, CAP_HEIGHT),
        rect(0, bar_y, round(w * 0.72), bar_y + h),
    )

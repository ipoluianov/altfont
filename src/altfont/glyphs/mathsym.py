"""Mathematical operators."""

from ..geometry import rect, ring, slant_half_width, slanted, union
from ..style import ASCENDER, DESCENDER, OVERSHOOT
from .common import GLYPHS, arch_bottom, arch_top, glyph, hook_left, hook_up
from .latin import v_shape
from .symbols import AXIS, asciitilde, chevron, equal, figure_width, six

W = 1000  # width of operators


def _add_codes(name, *codes):
    GLYPHS[name].unicodes.extend(codes)


# Operators drawn like existing glyphs.
for _name, _codes in {
    "Sigma": [0x2211], "Pe-cy": [0x220F], "Delta": [0x2206], "periodcentered": [0x22C5, 0x2219],
    "slash": [0x2215], "asterisk": [0x2217], "asciitilde": [0x223C],
}.items():
    _add_codes(_name, *_codes)


def _bar(S, y):
    h = S.hstem
    return rect(0, y - h / 2, W, y + h / 2)


@glyph("lessequal", [0x2264], ("F", "F"))
def lessequal(S):
    return chevron(S, 640, 640, AXIS + 140, True) | _bar(S, AXIS - 330)


@glyph("greaterequal", [0x2265], ("F", "F"))
def greaterequal(S):
    return chevron(S, 640, 640, AXIS + 140, False) | _bar(S, AXIS - 330)


@glyph("notequal", [0x2260], ("F", "F"))
def notequal(S):
    hw = slant_half_width(500, 900, S.vstem * 0.9)
    return equal(S) | slanted(250 + hw, AXIS - 450, 750 - hw, AXIS + 450, S.vstem * 0.9)


@glyph("approxequal", [0x2248], ("F", "F"))
def approxequal(S):
    t = asciitilde(S)
    return t.translate(0, 170) | t.translate(0, -170)


@glyph("equivalence", [0x2261], ("F", "F"))
def equivalence(S):
    return union(_bar(S, AXIS + 280), _bar(S, AXIS), _bar(S, AXIS - 280))


@glyph("infinity", [0x221E], ("R", "R"))
def infinity(S):
    r = 300 if not S.is_bold else 330
    v, h = S.round_vstem, S.hstem
    left = ring(0, AXIS - r, 2 * r + v * 0.5, AXIS + r, v, h)
    right = ring(2 * r - v * 0.5, AXIS - r, 4 * r, AXIS + r, v, h)
    return left | right


@glyph("radical", [0x221A], ("D", "T"))
def radical(S):
    v = S.vstem
    w = 1100
    t = v * 0.9
    long_hw = slant_half_width(w * 0.4, ASCENDER, t)
    short = slanted(w * 0.42, -60, w * 0.12, AXIS, t)
    long = slanted(w * 0.42, -60, w * 0.70 - long_hw, ASCENDER - S.hstem / 2, t)
    return union((short | long) & rect(0, 0, w, ASCENDER), rect(w * 0.70 - long_hw * 2, ASCENDER - S.hstem, w, ASCENDER))


@glyph("integral", [0x222B], ("T", "T"))
def integral(S):
    v = S.vstem
    w = 760
    x = round(w * 0.45)
    top, tc = hook_up(S, x, w, ASCENDER + OVERSHOOT, ry=240)
    bottom, bc = hook_left(S, x + v, DESCENDER - OVERSHOOT, ry=240)
    return union(rect(x, bc - 1, x + v, tc + 1), top, bottom)


@glyph("partialdiff", [0x2202], ("R", "R"))
def partialdiff(S):
    w = figure_width(S)
    return six(S, w).mirror_x(w / 2)


def _element(S, slashed=False):
    w = 860
    h = S.hstem
    top = AXIS + 380
    bottom = AXIS - 380
    r = ring(0, bottom, 2 * w, top, S.round_vstem, h) & rect(0, bottom, w, top)
    shape = r | rect(0, AXIS - h / 2, w, AXIS + h / 2)
    if slashed:
        hw = slant_half_width(300, 1000, S.vstem * 0.9)
        shape = shape | slanted(w * 0.3 + hw, AXIS - 500, w * 0.6 + 300 - hw, AXIS + 500, S.vstem * 0.9)
    return shape


@glyph("element", [0x2208], ("F", "F"))
def element(S):
    return _element(S)


@glyph("notelement", [0x2209], ("F", "F"))
def notelement(S):
    return _element(S, True)


@glyph("intersection", [0x2229], ("S", "S"))
def intersection(S):
    v = S.vstem
    arch, center = arch_top(0, W, AXIS + 420, 300, S)
    return union(arch, rect(0, AXIS - 420, v, center + 1), rect(W - v, AXIS - 420, W, center + 1))


@glyph("union", [0x222A], ("S", "S"))
def union_(S):
    v = S.vstem
    arch, center = arch_bottom(0, W, AXIS - 420, 300, S)
    return union(arch, rect(0, center - 1, v, AXIS + 420), rect(W - v, center - 1, W, AXIS + 420))


def _subset(S):
    h = S.hstem
    top, bottom = AXIS + 380, AXIS - 380
    w = 900
    r = ring(0, bottom, 760, top, S.round_vstem, h) & rect(0, bottom, 380, top)
    return union(r, rect(380, top - h, w, top), rect(380, bottom, w, bottom + h))


@glyph("propersubset", [0x2282], ("F", "F"))
def propersubset(S):
    return _subset(S)


@glyph("propersuperset", [0x2283], ("F", "F"))
def propersuperset(S):
    return _subset(S).mirror_x(450)


@glyph("emptyset", [0x2205], ("R", "R"))
def emptyset(S):
    d = 1100
    t = S.vstem * 0.9
    body = ring(0, AXIS - d / 2, d, AXIS + d / 2, S.round_vstem, S.hstem)
    return body | slanted(d * 0.1, AXIS - d * 0.62, d * 0.9, AXIS + d * 0.62, t)


@glyph("logicaland", [0x2227], ("D", "D"))
def logicaland(S):
    return v_shape(S, 900, 840).transform(1, 0, 0, -1, 0, AXIS + 420)


@glyph("logicalor", [0x2228], ("D", "D"))
def logicalor(S):
    return v_shape(S, 900, 840).translate(0, AXIS - 420)

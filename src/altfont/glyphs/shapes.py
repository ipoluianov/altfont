"""Arrows, geometric shapes and UI symbols (check marks, ballot boxes)."""

import math
from dataclasses import replace

from ..geometry import ellipse, polygon, rect, ring, slanted, union
from ..style import CAP_HEIGHT
from .common import glyph
from .latin import x_shape
from .symbols import AXIS, chevron, pdot, square

ARROW = 1300   # length of horizontal arrows
BOX = 1100     # size of squares, circles and ballot boxes, centred on the axis


def rotated(shape, angle, cx, cy):
    """Rotate counter-clockwise by `angle` degrees around (cx, cy)."""
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    return shape.transform(ca, sa, -sa, ca, cx - ca * cx + sa * cy, cy - sa * cx - ca * cy)


# --- Arrows ------------------------------------------------------------------------------

def _head(S, cy, pointing_left):
    return chevron(S, 320, 640, cy, pointing_left)


def arrow_right(S, length=ARROW, cy=AXIS):
    h = S.hstem
    head = _head(S, cy, False)
    hx0, _, hx1, _ = head.path.bounds
    head = head.translate(length - hx1)
    return rect(0, cy - h / 2, length - S.hstem * 0.6, cy + h / 2) | head


def _arrow_glyph(name, code, angle):
    def fn(S):
        shape = arrow_right(S)
        return rotated(shape, angle, ARROW / 2, AXIS)
    glyph(name, [code], ("T", "T"))(fn)


for _name, _code, _angle in [
    ("arrowright", 0x2192, 0), ("arrowup", 0x2191, 90), ("arrowleft", 0x2190, 180),
    ("arrowdown", 0x2193, 270), ("uni2197", 0x2197, 45), ("uni2196", 0x2196, 135),
    ("uni2199", 0x2199, 225), ("uni2198", 0x2198, 315),
]:
    _arrow_glyph(_name, _code, _angle)


@glyph("arrowboth", [0x2194], ("T", "T"))
def arrowboth(S):
    h = S.hstem
    left = _head(S, AXIS, True)
    right = _head(S, AXIS, False)
    rx1 = right.path.bounds[2]
    return union(left, right.translate(ARROW - rx1), rect(h, AXIS - h / 2, ARROW - h, AXIS + h / 2))


@glyph("arrowupdn", [0x2195], ("T", "T"))
def arrowupdn(S):
    return rotated(arrowboth(S), 90, ARROW / 2, AXIS)


def _double_arrow(S, both=False):
    h = S.hstem
    gap = 140 if not S.is_bold else 170
    head = chevron(S, 420, 900, AXIS, False)
    rx1 = head.path.bounds[2]
    shaft_end = ARROW - 260
    shafts = rect(0, AXIS + gap - h / 2, shaft_end, AXIS + gap + h / 2) | rect(0, AXIS - gap - h / 2, shaft_end, AXIS - gap + h / 2)
    shape = shafts | head.translate(ARROW - rx1)
    if both:
        shape = shape & rect(260, AXIS - 600, ARROW, AXIS + 600)
        shape = shape | chevron(S, 420, 900, AXIS, True) | rect(260, AXIS - gap - h / 2, 400, AXIS + gap + h / 2) - rect(260, AXIS - gap + h / 2, 400, AXIS + gap - h / 2)
    return shape


@glyph("arrowdblright", [0x21D2], ("T", "T"))
def arrowdblright(S):
    return _double_arrow(S)


@glyph("arrowdblleft", [0x21D0], ("T", "T"))
def arrowdblleft(S):
    return _double_arrow(S).mirror_x(ARROW / 2)


@glyph("arrowdblboth", [0x21D4], ("T", "T"))
def arrowdblboth(S):
    right = _double_arrow(S) & rect(ARROW / 2, -2000, ARROW, 4000)
    return right | right.mirror_x(ARROW / 2)


@glyph("carriagereturn", [0x21B5], ("T", "T"))
def carriagereturn(S):
    v, h = S.vstem, S.hstem
    cy = AXIS - 160
    head = _head(S, cy, True)
    return union(head, rect(h, cy - h / 2, ARROW, cy + h / 2), rect(ARROW - v, cy - h / 2, ARROW, CAP_HEIGHT * 0.86))


# --- Geometric shapes ---------------------------------------------------------------------

def _box(S, size=BOX):
    return 0, AXIS - size / 2, size, AXIS + size / 2


@glyph("filledbox", [0x25A0], ("S", "S"))
def filledbox(S):
    return rect(*_box(S))


@glyph("whitesquare", [0x25A1, 0x2610], ("S", "S"))
def whitesquare(S):
    x0, y0, x1, y1 = _box(S)
    v, h = S.vstem, S.hstem
    return rect(x0, y0, x1, y1) - rect(x0 + v, y0 + h, x1 - v, y1 - h)


@glyph("filledrect", [0x25AA], ("S", "S"))
def smallsquare(S):
    return rect(*_box(S, 560))


@glyph("uni25AB", [0x25AB], ("S", "S"))
def whitesmallsquare(S):
    x0, y0, x1, y1 = _box(S, 560)
    v, h = S.vstem, S.hstem
    return rect(x0, y0, x1, y1) - rect(x0 + v, y0 + h, x1 - v, y1 - h)


def triangle(S, pointing, filled):
    size = BOX
    cx = size / 2
    pts = {
        "up": [(0, AXIS - size * 0.43), (size, AXIS - size * 0.43), (cx, AXIS + size * 0.43)],
        "down": [(0, AXIS + size * 0.43), (size, AXIS + size * 0.43), (cx, AXIS - size * 0.43)],
        "right": [(size * 0.07, AXIS - size / 2), (size * 0.07, AXIS + size / 2), (size * 0.93, AXIS)],
        "left": [(size * 0.93, AXIS - size / 2), (size * 0.93, AXIS + size / 2), (size * 0.07, AXIS)],
    }[pointing]
    outer = polygon(pts)
    if filled:
        return outer
    # Inner triangle: shrink towards the centroid so the sides keep ~ one stem.
    gx = sum(p[0] for p in pts) / 3
    gy = sum(p[1] for p in pts) / 3
    k = 1 - 2.2 * S.vstem / size
    inner = polygon([(gx + (x - gx) * k, gy + (y - gy) * k) for x, y in pts])
    return outer - inner


for _name, _code, _dir, _filled in [
    ("triagup", 0x25B2, "up", True), ("uni25B3", 0x25B3, "up", False),
    ("uni25B6", 0x25B6, "right", True), ("uni25B7", 0x25B7, "right", False),
    ("triagdn", 0x25BC, "down", True), ("uni25BD", 0x25BD, "down", False),
    ("uni25C0", 0x25C0, "left", True), ("uni25C1", 0x25C1, "left", False),
]:
    glyph(_name, [_code], ("T", "T"))(lambda S, d=_dir, f=_filled: triangle(S, d, f))


@glyph("uni25CF", [0x25CF], ("R", "R"))
def blackcircle(S):
    return ellipse(*_box(S), k=0.5523)


@glyph("circle", [0x25CB], ("R", "R"))
def whitecircle(S):
    x0, y0, x1, y1 = _box(S)
    return ring(x0, y0, x1, y1, S.round_vstem, S.hstem, k=0.5523)


@glyph("uni25E6", [0x25E6], ("R", "R"))
def whitebullet(S):
    r = 230 if not S.is_bold else 270
    return ring(0, AXIS - r, 2 * r, AXIS + r, S.vstem * 0.85, S.hstem * 0.85, k=0.5523)


def _diamond(size):
    c = size / 2
    return polygon([(0, AXIS), (c, AXIS + c * 1.1), (size, AXIS), (c, AXIS - c * 1.1)])


@glyph("uni25C6", [0x25C6], ("T", "T"))
def blackdiamond(S):
    return _diamond(BOX)


@glyph("uni25C7", [0x25C7, 0x25CA], ("T", "T"))
def whitediamond(S):
    outer = _diamond(BOX)
    t = S.vstem * 1.4
    inner = _diamond(BOX - 2 * t).translate(t)
    return outer - inner


def _star(r_outer, r_inner):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(90 + 36 * i)
        pts.append((r_outer + r * math.cos(a), AXIS + 40 + r * math.sin(a)))
    return polygon(pts)


@glyph("uni2605", [0x2605], ("T", "T"))
def blackstar(S):
    return _star(600, 250)


@glyph("uni2606", [0x2606], ("T", "T"))
def whitestar(S):
    t = S.vstem * 1.25
    outer = _star(600, 250)
    inner = _star(600 - t * 1.6, 250 - t * 0.7).translate(t * 1.6)
    return outer - inner


# --- UI symbols ------------------------------------------------------------------------------

def check(S, size, cy, weight=1.0):
    t = S.vstem * weight
    left = (0, cy)
    bottom = (size * 0.36, cy - size * 0.42)
    top = (size, cy + size * 0.52)
    short = slanted(bottom[0], bottom[1], left[0] + t * 0.5, left[1], t)
    long = slanted(bottom[0], bottom[1], top[0] - t * 0.5, top[1], t)
    return short | long


@glyph("uni2713", [0x2713], ("T", "T"))
def checkmark(S):
    return check(S, 1000, AXIS)


@glyph("uni2714", [0x2714], ("T", "T"))
def heavycheck(S):
    return check(S, 1000, AXIS, 1.6)


@glyph("uni2717", [0x2717, 0x2715], ("T", "T"))
def ballotx(S):
    return x_shape(S, 860, 860).translate(0, AXIS - 430)


@glyph("uni2718", [0x2718, 0x2716], ("T", "T"))
def heavyballotx(S):
    return x_shape(replace(S, vstem=round(S.vstem * 1.6)), 860, 860).translate(0, AXIS - 430)


@glyph("uni2611", [0x2611], ("S", "S"))
def ballotboxcheck(S):
    box = whitesquare(S)
    x0, y0, x1, y1 = _box(S)
    m = check(S, 680, AXIS - 20).translate(x0 + 210)
    return box | m


@glyph("uni2612", [0x2612], ("S", "S"))
def ballotboxx(S):
    box = whitesquare(S)
    x0, y0, x1, y1 = _box(S)
    m = x_shape(S, 600, 600).translate(x0 + 250, AXIS - 300)
    return box | m


@glyph("uni22EE", [0x22EE], ("S", "S"))
def vellipsis(S):
    p = pdot(S)
    step = p + 200
    return union(*(square(0, AXIS - p / 2 + k * step, p) for k in (-1, 0, 1)))


@glyph("uni22EF", [0x22EF], ("S", "S"))
def midlineellipsis(S):
    p = pdot(S)
    step = p + 240
    return union(*(square(k * step, AXIS - p / 2, p) for k in range(3)))

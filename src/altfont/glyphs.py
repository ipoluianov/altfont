"""Parametric glyph definitions.

Each glyph function takes a Style and returns a Shape drawn with its left
extreme at x = 0. Side bearings are added by the builder from the spacing
classes given in the registry: "S" (straight side) or "R" (round side).
"""

from .geometry import polygon, rect, ring, union
from .style import CAP_HEIGHT, DESCENDER, OVERSHOOT, X_HEIGHT

GLYPHS = {}  # name -> (function, unicodes, (left spacing, right spacing))


def glyph(name, unicodes, spacing):
    def register(fn):
        GLYPHS[name] = (fn, unicodes, spacing)
        return fn
    return register


def arch_top(x0, x1, top, ry, S):
    """Upper half of an oval stroke spanning x0..x1, with its apex at `top`."""
    center = top - ry
    r = ring(x0, top - 2 * ry, x1, top, S.round_vstem, S.hstem)
    return r & rect(x0, center, x1, top), center


def arch_bottom(x0, x1, bottom, ry, S):
    """Lower half of an oval stroke spanning x0..x1, with its lowest point at `bottom`."""
    center = bottom + ry
    r = ring(x0, bottom, x1, bottom + 2 * ry, S.round_vstem, S.hstem)
    return r & rect(x0, bottom, x1, center), center


# --- Latin -----------------------------------------------------------------

@glyph("n", [0x006E], ("S", "S"))
def n(S):
    w, v = S.widths["n"], S.vstem
    arch, center = arch_top(0, w, X_HEIGHT + OVERSHOOT, X_HEIGHT * 0.5, S)
    return union(
        rect(0, 0, v, X_HEIGHT),
        rect(w - v, 0, w, center + 1),
        arch,
    )


@glyph("o", [0x006F, 0x043E], ("R", "R"))
def o(S):
    w = S.widths["o"]
    return ring(0, -OVERSHOOT, w, X_HEIGHT + OVERSHOOT, S.round_vstem, S.hstem)


@glyph("a", [0x0061], ("R", "S"))
def a(S):
    w, v, h = S.widths["a"], S.vstem, S.hstem
    top = X_HEIGHT + OVERSHOOT
    terminal_y = X_HEIGHT * 0.72
    arch, _ = arch_top(0, w, top, X_HEIGHT * 0.5, S)
    arch = arch & rect(0, terminal_y, w, top)
    bowl_top = X_HEIGHT * (0.60 if S.is_bold else 0.56)
    bowl = ring(0, -OVERSHOOT, w, bowl_top, S.round_vstem, h)
    return union(
        arch,
        rect(w - v, 0, w, terminal_y + 1),
        bowl,
    )


@glyph("e", [0x0065], ("R", "R"))
def e(S):
    w, v, h = S.widths["e"], S.round_vstem, S.hstem
    # The eye takes half of the inner height left free by the bar.
    inner_top = X_HEIGHT + OVERSHOOT - h
    inner_bottom = -OVERSHOOT + h
    eye = (inner_top - inner_bottom - h) * 0.5
    bar_y = inner_top - eye - h
    aperture_bottom = X_HEIGHT * 0.24
    bowl = ring(0, -OVERSHOOT, w, X_HEIGHT + OVERSHOOT, v, h)
    bowl = bowl - rect(w * 0.5, aperture_bottom, w + 1, bar_y)
    bar = rect(v / 2, bar_y, w - v / 2, bar_y + h)
    return bowl | bar


@glyph("g", [0x0067], ("R", "S"))
def g(S):
    w, v = S.widths["g"], S.vstem
    bowl = ring(0, -OVERSHOOT, w, X_HEIGHT + OVERSHOOT, S.round_vstem, S.hstem)
    hook, center = arch_bottom(0, w, DESCENDER - OVERSHOOT, 260, S)
    hook = hook & rect(w * 0.1, DESCENDER - OVERSHOOT, w, center)
    return union(
        bowl,
        rect(w - v, center - 1, w, X_HEIGHT),
        hook,
    )


@glyph("H", [0x0048], ("S", "S"))
def H(S):
    w, v, h = S.widths["H"], S.vstem, S.hstem
    bar_y = CAP_HEIGHT * 0.5 - h / 2 + 10
    return union(
        rect(0, 0, v, CAP_HEIGHT),
        rect(w - v, 0, w, CAP_HEIGHT),
        rect(v, bar_y, w - v, bar_y + h),
    )


@glyph("O", [0x004F, 0x041E], ("R", "R"))
def O(S):
    w = S.widths["O"]
    return ring(0, -OVERSHOOT, w, CAP_HEIGHT + OVERSHOOT, S.round_vstem, S.hstem)


# --- Cyrillic --------------------------------------------------------------

@glyph("en-cy", [0x043D], ("S", "S"))
def en_cy(S):
    w, v, h = S.widths["en-cy"], S.vstem, S.hstem
    bar_y = X_HEIGHT * 0.5 - h / 2
    return union(
        rect(0, 0, v, X_HEIGHT),
        rect(w - v, 0, w, X_HEIGHT),
        rect(v, bar_y, w - v, bar_y + h),
    )


@glyph("i-cy", [0x0438], ("S", "S"))
def i_cy(S):
    w, v = S.widths["i-cy"], S.vstem
    # Horizontal width of the diagonal so its perpendicular thickness is
    # close to the stem thickness.
    dx, dy = w - 2 * v, X_HEIGHT
    hw = v * 0.95 * (dx * dx + dy * dy) ** 0.5 / dy
    diagonal = polygon([
        (v - hw * 0.5, 0),
        (w - v - hw * 0.5, X_HEIGHT),
        (w - v + hw * 0.5, X_HEIGHT),
        (v + hw * 0.5, 0),
    ]) & rect(v, 0, w - v, X_HEIGHT)
    return union(
        rect(0, 0, v, X_HEIGHT),
        rect(w - v, 0, w, X_HEIGHT),
        diagonal,
    )


@glyph("de-cy", [0x0434], ("S", "S"))
def de_cy(S):
    w, v, h = S.widths["de-cy"], S.vstem, S.hstem
    depth = -300
    leg_x = round(w * 0.16)
    return union(
        rect(0, depth, v, h),                  # left descender
        rect(0, 0, w, h),                      # base
        rect(w - v, depth, w, X_HEIGHT),       # right stem with descender
        rect(leg_x, 0, leg_x + v, X_HEIGHT),   # left leg
        rect(leg_x, X_HEIGHT - h, w - v, X_HEIGHT),  # top bar
    )


@glyph("Be-cy", [0x0411], ("S", "R"))
def Be_cy(S):
    w, v, h = S.widths["Be-cy"], S.vstem, S.hstem
    bowl_top = round(CAP_HEIGHT * 0.58)
    # D-shaped bowl: right half of an oval stroke centred on the stem.
    bowl = ring(-w, 0, w, bowl_top, S.round_vstem, h, k=0.68) & rect(0, 0, w, bowl_top)
    return union(
        rect(0, 0, v, CAP_HEIGHT),
        rect(0, CAP_HEIGHT - h, round(w * 0.9), CAP_HEIGHT),
        bowl,
    )


# --- Space -----------------------------------------------------------------

SPACE_WIDTH = {"Regular": 540, "Bold": 560}

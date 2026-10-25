"""Diacritical marks and their placement on base glyphs.

Above marks are functions (S, cx, y0, cap) -> Shape, drawn with their
bottom at y0 and centred on cx. `cap` selects the flatter variant used over
capitals and ascenders, so stacked marks stay low. Below marks are
functions (S, bounds, base) -> Shape.
"""

from ..geometry import ellipse, rect, ring, slant_half_width, slanted, union
from ..style import CAP_HEIGHT, OVERSHOOT, X_HEIGHT

# --- Geometry shared by marks ----------------------------------------------------


def _size(S):
    """Dot size: as thick as the heavier stem."""
    return max(S.vstem, S.hstem)


def _half(S):
    return 260 if not S.is_bold else 300


def mark_grave(S, cx, y0, cap=False):
    rise = 250 if cap else 300
    return slanted(cx + 60, y0, cx - 120, y0 + rise, S.vstem)


def mark_acute(S, cx, y0, cap=False):
    rise = 250 if cap else 300
    return slanted(cx - 60, y0, cx + 120, y0 + rise, S.vstem)


def _peak(S, cx, y0, rise, inverted=False):
    """Circumflex (^) or, inverted, caron (v)."""
    half = _half(S)
    t = S.vstem * 0.9
    hw = slant_half_width(half, rise, t)
    if not inverted:
        strokes = slanted(cx - half + hw, y0, cx, y0 + rise, t) | slanted(cx + half - hw, y0, cx, y0 + rise, t)
    else:
        strokes = slanted(cx, y0, cx - half + hw, y0 + rise, t) | slanted(cx, y0, cx + half - hw, y0 + rise, t)
    return strokes & rect(cx - half, y0, cx + half, y0 + rise)


def mark_circumflex(S, cx, y0, cap=False):
    return _peak(S, cx, y0, 240 if cap else 260)


def mark_caron(S, cx, y0, cap=False):
    return _peak(S, cx, y0, 240 if cap else 260, inverted=True)


def mark_tilde(S, cx, y0, cap=False):
    half = _half(S)
    amp = 90 if cap else 110
    v, h = S.vstem * 0.9, S.hstem
    mid = y0 + amp + h / 2
    x0, x1 = cx - half, cx + half
    w = x1 - x0
    left = ring(x0, mid - amp - h / 2, x0 + w * 0.56, mid + amp + h / 2, v, h) & rect(x0, mid, x0 + w * 0.56, y0 + 2 * amp + h)
    right = ring(x0 + w * 0.44, mid - amp - h / 2, x1, mid + amp + h / 2, v, h) & rect(x0 + w * 0.44, y0, x1, mid)
    return left | right


def mark_macron(S, cx, y0, cap=False):
    half = _half(S)
    return rect(cx - half, y0 + 20, cx + half, y0 + 20 + S.hstem)


def mark_breve(S, cx, y0, cap=False):
    """Cup: lower half of an oval, inner oval raised by the stroke thickness."""
    half = _half(S)
    height = (230 if not S.is_bold else 280) - (50 if cap else 0)
    h = min(S.hstem, 200)
    outer = ellipse(cx - half, y0, cx + half, y0 + 2 * height)
    inner = ellipse(cx - half + S.vstem, y0 + h, cx + half - S.vstem, y0 + 2 * height + h)
    return (outer - inner) & rect(cx - half, y0, cx + half, y0 + height)


def mark_dotaccent(S, cx, y0, cap=False):
    size = _size(S) if not cap else min(_size(S), 240)
    return rect(cx - size / 2, y0, cx + size / 2, y0 + size)


def mark_dieresis(S, cx, y0, cap=False):
    size = _size(S) if not cap else min(_size(S), 240)
    gap = round(size * 1.25)
    left = cx - gap / 2 - size
    return rect(left, y0, left + size, y0 + size) | rect(cx + gap / 2, y0, cx + gap / 2 + size, y0 + size)


def mark_ring(S, cx, y0, cap=False):
    r = 150 if cap else 175
    if S.is_bold:
        r += 40
    return ring(cx - r, y0, cx + r, y0 + 2 * r, S.vstem * 0.85, S.hstem * 0.85)


def mark_hungarumlaut(S, cx, y0, cap=False):
    d = 150 if not S.is_bold else 190
    return mark_acute(S, cx - d, y0, cap) | mark_acute(S, cx + d, y0, cap)


def mark_hookabove(S, cx, y0, cap=False):
    """Small question-mark curl (Vietnamese)."""
    v, h = S.vstem * 0.9, S.hstem
    r = 150 if not S.is_bold else 180
    height = 2 * r if not cap else round(1.7 * r)
    bottom = y0 + height - 2 * r + h
    rr = ring(cx - r, bottom, cx + r, bottom + 2 * r, v, h)
    center = bottom + r
    curl = rr & (rect(cx - r, center, cx + r, bottom + 2 * r) | rect(cx, bottom, cx + r, center))
    return curl | rect(cx - v / 2, y0, cx + v / 2, bottom + h)


ABOVE = {
    0x0300: mark_grave, 0x0301: mark_acute, 0x0302: mark_circumflex,
    0x0303: mark_tilde, 0x0304: mark_macron, 0x0306: mark_breve,
    0x0307: mark_dotaccent, 0x0308: mark_dieresis, 0x0309: mark_hookabove,
    0x030A: mark_ring, 0x030B: mark_hungarumlaut, 0x030C: mark_caron,
}

# Marks that sit beside a circumflex instead of on top of it (Vietnamese).
BESIDE_CIRCUMFLEX = {0x0300, 0x0301, 0x0309}
CIRCUMFLEX = 0x0302


# --- Below marks -------------------------------------------------------------------

def _pdot(S):
    return round(S.vstem * 1.12)


def comma_shape(S):
    """Square dot with a tail, bottom of the tail at y = -280, dot at 0..p."""
    p = _pdot(S)
    tail = slanted(p * 0.10, -280, p * 0.62, p * 0.5, p * 0.62) & rect(-60, -280, p, p * 0.5)
    return rect(0, 0, p, p) | tail


def mark_dotbelow(S, bounds, base):
    size = _size(S)
    cx = (bounds[0] + bounds[2]) / 2
    if base == "y":
        cx = bounds[0] + (bounds[2] - bounds[0]) * 0.74   # clear of the descender
    return rect(cx - size / 2, -150 - size, cx + size / 2, -150)


def mark_commabelow(S, bounds, base):
    p = _pdot(S) * 0.85
    cx = (bounds[0] + bounds[2]) / 2
    shape = comma_shape(S).transform(0.85, 0, 0, 0.85)
    return shape.translate(cx - p / 2, -130 - p)


def mark_cedilla(S, bounds, base):
    v, h = S.vstem * 0.85, S.hstem * 0.85
    cx = (bounds[0] + bounds[2]) / 2
    if base in ("t", "uni0163"):
        cx = bounds[0] + (bounds[2] - bounds[0]) * 0.24 + S.vstem / 2
    r = 170
    top, bottom = -110, -430
    hook = ring(cx - r, bottom, cx + r, top, v, h)
    hook = hook & (rect(cx - 10, bottom, cx + r, top) | rect(cx - r, bottom, cx, bottom + h))
    return hook | rect(cx - v / 2, top - h, cx + v / 2, 1)


def mark_ogonek(S, bounds, base):
    v, h = S.vstem, S.hstem
    x0, _, x1, _ = bounds
    if base in ("a", "u", "i", "I", "dotlessi"):
        xa = x1 - v                      # under the right stem
    else:
        xa = x0 + (x1 - x0) * 0.55
    r = 180
    bottom = -400
    center = bottom + 250
    curve = ring(xa, bottom, xa + 2 * r, center * 2 - bottom, v, h) & rect(xa, bottom, xa + r, center)
    return union(curve, rect(xa, center - 1, xa + v, 1), rect(xa + r, bottom, xa + r + 110, bottom + h))


BELOW = {
    0x0323: mark_dotbelow, 0x0326: mark_commabelow,
    0x0327: mark_cedilla, 0x0328: mark_ogonek,
}

HORN = 0x031B


def horn(S, bounds):
    """Horn of ơ ư Ơ Ư: a short stroke rising to the upper right of the shoulder."""
    _, _, x1, y1 = bounds
    v = S.vstem
    rise = 280 if y1 <= X_HEIGHT + OVERSHOOT + 1 else 220
    t = v * 0.85
    return slanted(x1 - t * 0.7, y1 - 140, x1 + 70, y1 + rise, t)


HORN_EXTRA = 160  # advance added to horned letters


def caron_apostrophe(S, bounds):
    """Caron of ď ľ ť Ľ: an apostrophe right of the ascender."""
    _, _, x1, y1 = bounds
    p = _pdot(S) * 0.9
    top = max(y1, CAP_HEIGHT)
    if y1 > CAP_HEIGHT + OVERSHOOT + 1:
        top = y1
    return comma_shape(S).transform(0.9, 0, 0, 0.9).translate(x1 + 90, top - p)


APOSTROPHE_EXTRA = 240


def turned_comma_above(S, bounds):
    """Cedilla of ģ, drawn as a turned comma above."""
    x0, _, x1, _ = bounds
    p = _pdot(S) * 0.85
    shape = comma_shape(S).transform(0.85, 0, 0, 0.85)
    cx = (x0 + x1) / 2
    shape = shape.rotate180(p / 2, p / 2)
    return shape.translate(cx - p / 2, X_HEIGHT + 200 + 240)


# --- Placement ---------------------------------------------------------------------

def mark_level(S, top):
    """Bottom of the first above mark and whether to use the flat variant."""
    if top <= X_HEIGHT + OVERSHOOT + 1:
        return X_HEIGHT + (220 if S.is_bold else 200), False
    if top <= CAP_HEIGHT + OVERSHOOT + 1:
        return CAP_HEIGHT + (150 if S.is_bold else 140), True
    return top + (150 if S.is_bold else 140), True


def place_marks(S, shape, base, marks):
    """Add `marks` (combining code points, in NFD order) to the base shape."""
    bounds = shape.path.bounds
    x0, _, x1, y1 = bounds
    cx = (x0 + x1) / 2
    y, cap = mark_level(S, y1)
    parts = [shape]
    previous = None
    for m in marks:
        if m in BELOW:
            parts.append(BELOW[m](S, bounds, base))
            continue
        if m == HORN:
            parts.append(horn(S, bounds))
            continue
        if previous == CIRCUMFLEX and m in BESIDE_CIRCUMFLEX:
            # Vietnamese: the second mark sits to the upper right of ^.
            parts.append(ABOVE[m](S, cx + _half(S) + 150, y_prev + 60, True))
            previous = m
            continue
        mark = ABOVE[m](S, cx, y, cap)
        parts.append(mark)
        y_prev = y
        y = mark.path.bounds[3] + 70
        cap = True  # further stacked marks are flat
        previous = m
    return union(*parts)

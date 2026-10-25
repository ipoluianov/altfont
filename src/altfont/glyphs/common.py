"""Glyph registry and construction helpers shared by all scripts."""

from typing import Callable, NamedTuple, Optional

from ..geometry import rect, ring, slant_half_width, slanted
from ..style import OVERSHOOT, X_HEIGHT


class GlyphDef(NamedTuple):
    fn: Callable              # Style -> Shape
    unicodes: list
    spacing: tuple            # (left class, right class)
    base: Optional[str]       # accented glyphs: metrics come from this glyph
    extra: object = 0         # advance added to the base's: int or fn(Style)


GLYPHS = {}  # name -> GlyphDef

SPACE_WIDTH = {"Regular": 540, "Bold": 560}

# Ascender of t, between x-height and ascender.
T_HEIGHT = 1400


def glyph(name, unicodes, spacing):
    """Register a glyph function.

    Spacing classes per side: "S" straight stem, "R" round side,
    "T" open terminal (r, f, t, j), "D" diagonal (v, w, x, y).
    ("F", "F") is a tabular glyph: fixed advance `Style.figure_advance`,
    ink centered. ("Z", "Z") is a zero-width combining mark, drawn over the
    preceding glyph.
    """
    def register(fn):
        GLYPHS[name] = GlyphDef(fn, unicodes, spacing, None)
        return fn
    return register


def accented(name, unicodes, base, decorate, extra=0):
    """Register base glyph + marks. Spacing, width and pixel fit follow the base.

    `decorate(S, shape)` returns the base shape with its marks.
    """
    def fn(S):
        return decorate(S, GLYPHS[base].fn(S))
    GLYPHS[name] = GlyphDef(fn, unicodes, GLYPHS[base].spacing, base, extra)


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


def bowl(S, w, bottom=-OVERSHOOT, top=X_HEIGHT + OVERSHOOT):
    """The o-shaped bowl of b d p q and friends."""
    return ring(0, bottom, w, top, S.round_vstem, S.hstem)


def dot(S, x0, width=None):
    """Square dot above x-height (i, j)."""
    width = width or S.vstem
    gap = 220 if S.is_bold else 200
    size = max(S.vstem, S.hstem)
    return rect(x0, X_HEIGHT + gap, x0 + width, X_HEIGHT + gap + size)


def hook_down(S, x_stem, x_end, bottom, ry=240):
    """Quarter-oval tail from a stem at x_stem..x_stem+v curving right to x_end.

    Used for the feet of l and t. Returns (shape, y where the stem joins).
    """
    span = x_end - x_stem
    r = ring(x_stem, bottom, x_stem + 2 * span, bottom + 2 * ry, S.round_vstem, S.hstem)
    return r & rect(x_stem, bottom, x_end, bottom + ry), bottom + ry


def hook_up(S, x_stem, x_end, top, ry=240):
    """Quarter-oval from a stem at x_stem..x_stem+v curving right at the top (f)."""
    span = x_end - x_stem
    r = ring(x_stem, top - 2 * ry, x_stem + 2 * span, top, S.round_vstem, S.hstem)
    return r & rect(x_stem, top - ry, x_end, top), top - ry


def d_bowl(S, x0, x1, y0, y1, k=0.68):
    """D-shaped bowl attached to a stem at x0 (open side towards the stem)."""
    span = x1 - x0
    r = ring(x0 - span, y0, x1, y1, S.round_vstem, S.hstem, k=k)
    return r & rect(x0, y0, x1, y1)


def d_bowl_left(S, x0, x1, y0, y1, k=0.68):
    """Mirror of d_bowl: attached to a stem at x1, bulging to the left (я)."""
    span = x1 - x0
    r = ring(x0, y0, x1 + span, y1, S.round_vstem, S.hstem, k=k)
    return r & rect(x0, y0, x1, y1)


def arm_and_leg(S, x_stem, x_end, height, joint_frac=0.42):
    """The arm and leg of k/K/к/ж, attached to a stem whose outer edge is x_stem.

    Returns the two diagonals clipped to x_stem..x_end, 0..height. With
    x_end < x_stem they are mirrored to the left, as in ж.
    """
    t = S.vstem * 0.95
    sign = 1 if x_end > x_stem else -1
    span = abs(x_end - x_stem)
    top_hw = slant_half_width(span, height * 0.6, t)
    arm_b = (x_stem - sign * S.vstem * 0.5, height * 0.30)
    arm_t = (x_end - sign * top_hw, height)
    joint = (arm_b[0] + (arm_t[0] - arm_b[0]) * joint_frac,
             arm_b[1] + (arm_t[1] - arm_b[1]) * joint_frac)
    leg_hw = slant_half_width(abs(x_end - joint[0]), joint[1], t)
    arm = slanted(*arm_b, *arm_t, t)
    leg = slanted(x_end - sign * leg_hw, 0, *joint, t)
    lo, hi = sorted((x_stem, x_end))
    return (arm | leg) & rect(lo, 0, hi, height)


def hook_left(S, x_stem_right, bottom, ry=240):
    """Quarter-oval tail of j: from a stem ending at x_stem_right curving left to x = 0."""
    r = ring(-x_stem_right, bottom, x_stem_right, bottom + 2 * ry, S.round_vstem, S.hstem)
    return r & rect(0, bottom, x_stem_right, bottom + ry), bottom + ry

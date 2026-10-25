"""Cyrillic glyphs.

Letters identical to Latin ones (а е о р с у х ѕ і ј, А В Е К М Н О Р С Т Х Ѕ І Ј)
are mapped to the Latin glyphs. Most shapes below are built at a given
height and registered twice, at x-height and at cap height. Letters with
diacritics (ё й ї ў ...) are generated in `composites.py`.
"""

from ..geometry import rect, ring, slant_half_width, slanted, union
from ..style import ASCENDER, CAP_HEIGHT, DESCENDER, OVERSHOOT, X_HEIGHT
from .common import (arch_bottom, arch_top, arm_and_leg, bowl, d_bowl,
                     d_bowl_left, glyph, hook_left, hook_up)
from .latin import C, H, K, X, Y, c, m_shape, v_shape, x

TAIL = -300  # depth of the short descenders of д ц щ џ


def both(lower, upper, lower_code, upper_code, spacing, upper_spacing=None):
    """Register one shape builder `fn(S, w, height)` as lowercase and uppercase."""
    def register(fn):
        glyph(lower, [lower_code], spacing)(lambda S: fn(S, S.widths[lower], X_HEIGHT))
        glyph(upper, [upper_code], upper_spacing or spacing)(
            lambda S: fn(S, S.widths[upper], CAP_HEIGHT))
        return fn
    return register


# --- Shapes used in both cases -------------------------------------------------

@both("ge-cy", "Ge-cy", 0x0433, 0x0413, ("S", "T"))
def ge(S, w, height):
    return rect(0, 0, S.vstem, height) | rect(0, height - S.hstem, w, height)


@both("gheupturn-cy", "Gheupturn-cy", 0x0491, 0x0490, ("S", "T"))
def gheupturn(S, w, height):
    v, h = S.vstem, S.hstem
    rise = 260 if height == X_HEIGHT else 220
    return union(rect(0, 0, v, height), rect(0, height - h, w, height),
                 rect(w - v, height - h, w, height + rise))


@both("de-cy", "De-cy", 0x0434, 0x0414, ("S", "S"))
def de(S, w, height):
    v, h = S.vstem, S.hstem
    leg_x = round(w * 0.16)
    return union(
        rect(0, TAIL, v, h),                     # left descender
        rect(0, 0, w, h),                        # base
        rect(w - v, TAIL, w, height),            # right stem with descender
        rect(leg_x, 0, leg_x + v, height),       # left leg
        rect(leg_x, height - h, w - v, height),  # top bar
    )


@both("zhe-cy", "Zhe-cy", 0x0436, 0x0416, ("D", "D"))
def zhe(S, w, height):
    v = S.vstem
    x0 = round((w - v) / 2)
    return union(
        rect(x0, 0, x0 + v, height),
        arm_and_leg(S, x0 + v, w, height),
        arm_and_leg(S, x0, 0, height),
    )


@both("ze-cy", "Ze-cy", 0x0437, 0x0417, ("T", "R"))
def ze(S, w, height):
    if height == X_HEIGHT:
        S = S.tight
    h, v = S.hstem, S.round_vstem
    top = height + OVERSHOOT
    mid = height / 2
    cx = w / 2
    # Mirror image of the halves of s: both bowls open to the left.
    upper = ring(w * 0.06, mid - h / 2, w * 0.97, top, v, h)
    upper = upper & (rect(cx, mid - h, w, top) | rect(0, height * 0.72, cx, top))
    lower = ring(0, -OVERSHOOT, w, mid + h / 2, v, h)
    lower = lower & (rect(cx, -OVERSHOOT, w, mid + h) | rect(0, -OVERSHOOT, cx, height * 0.26))
    bar = rect(w * 0.32, mid - h / 2, cx + 1, mid + h / 2)
    return union(upper, lower, bar)


@both("i-cy", "I-cy", 0x0438, 0x0418, ("S", "S"))
def i_(S, w, height):
    v = S.vstem
    # Diagonal from the foot of the left stem to the top of the right one.
    diagonal = slanted(v, 0, w - v, height, v * 0.95) & rect(v, 0, w - v, height)
    return union(rect(0, 0, v, height), rect(w - v, 0, w, height), diagonal)


@both("el-cy", "El-cy", 0x043B, 0x041B, ("T", "S"))
def el(S, w, height):
    v, h = S.vstem, S.hstem
    leg_x = round(w * 0.12)
    foot, center = hook_left(S, leg_x + v, -OVERSHOOT, ry=200 if height == X_HEIGHT else 240)
    return union(
        rect(w - v, 0, w, height),
        rect(leg_x, height - h, w - v, height),
        rect(leg_x, center - 1, leg_x + v, height),
        foot,
    )


@both("pe-cy", "Pe-cy", 0x043F, 0x041F, ("S", "S"))
def pe(S, w, height):
    v, h = S.vstem, S.hstem
    return union(rect(0, 0, v, height), rect(w - v, 0, w, height),
                 rect(0, height - h, w, height))


@both("tse-cy", "Tse-cy", 0x0446, 0x0426, ("S", "S"))
def tse(S, w, height):
    v, h = S.vstem, S.hstem
    x1 = w - round(v * 0.75)  # right edge of the right stem; the tail sticks out
    return union(rect(0, 0, v, height), rect(x1 - v, 0, x1, height),
                 rect(0, 0, w, h), rect(w - v, TAIL, w, h))


@both("che-cy", "Che-cy", 0x0447, 0x0427, ("S", "S"))
def che(S, w, height):
    v = S.vstem
    arch, center = arch_bottom(0, w, height * 0.30, height * 0.26, S)
    return union(rect(0, center - 1, v, height), rect(w - v, 0, w, height), arch)


@both("sha-cy", "Sha-cy", 0x0448, 0x0428, ("S", "S"))
def sha(S, w, height):
    v, h = S.vstem, S.hstem
    x1 = round((w - v) / 2)
    return union(rect(0, 0, v, height), rect(x1, 0, x1 + v, height),
                 rect(w - v, 0, w, height), rect(0, 0, w, h))


@both("shcha-cy", "Shcha-cy", 0x0449, 0x0429, ("S", "S"))
def shcha(S, w, height):
    v, h = S.vstem, S.hstem
    x2 = w - round(v * 0.75)
    x1 = round((x2 - v) / 2)
    return union(rect(0, 0, v, height), rect(x1, 0, x1 + v, height),
                 rect(x2 - v, 0, x2, height), rect(0, 0, w, h),
                 rect(w - v, TAIL, w, h))


def soft_sign(S, x_stem, w, height):
    """Stem at x_stem with a D bowl at the bottom, extending to x = w."""
    bowl_top = round(height * (0.60 if height == X_HEIGHT else 0.56))
    return rect(x_stem, 0, x_stem + S.vstem, height) | d_bowl(S, x_stem, w, 0, bowl_top)


@both("softsign-cy", "Softsign-cy", 0x044C, 0x042C, ("S", "R"))
def softsign(S, w, height):
    return soft_sign(S, 0, w, height)


@both("hardsign-cy", "Hardsign-cy", 0x044A, 0x042A, ("T", "R"))
def hardsign(S, w, height):
    x = round(w * 0.22)
    return soft_sign(S, x, w, height) | rect(0, height - S.hstem, x + S.vstem, height)


@both("yeru-cy", "Yeru-cy", 0x044B, 0x042B, ("S", "S"))
def yeru(S, w, height):
    return soft_sign(S, 0, round(w * 0.66), height) | rect(w - S.vstem, 0, w, height)


@both("e-cy", "E-cy", 0x044D, 0x042D, ("T", "R"))
def e_(S, w, height):
    if height == X_HEIGHT:
        S = S.tight
    h, v = S.hstem, S.round_vstem
    mid = height / 2
    shape = bowl(S, w, top=height + OVERSHOOT) - rect(-1, height * 0.32, w * 0.5, height * 0.68)
    return shape | rect(w * 0.36, mid - h / 2, w - v / 2, mid + h / 2)


@both("ie-ukr", "Ie-ukr", 0x0454, 0x0404, ("R", "T"))
def ie(S, w, height):
    if height == X_HEIGHT:
        S = S.tight
    h, v = S.hstem, S.round_vstem
    mid = height / 2
    shape = bowl(S, w, top=height + OVERSHOOT) - rect(w * 0.5, height * 0.32, w + 1, height * 0.68)
    return shape | rect(v / 2, mid - h / 2, w * 0.64, mid + h / 2)


@both("yu-cy", "Yu-cy", 0x044E, 0x042E, ("S", "R"))
def yu(S, w, height):
    v, h = S.vstem, S.hstem
    xb = round(w * 0.30)
    mid = height / 2
    return union(
        rect(0, 0, v, height),
        rect(v, mid - h / 2, xb + S.round_vstem / 2, mid + h / 2),
        ring(xb, -OVERSHOOT, w, height + OVERSHOOT, S.round_vstem, h),
    )


@both("ya-cy", "Ya-cy", 0x044F, 0x042F, ("D", "S"))
def ya(S, w, height):
    v, h = S.vstem, S.hstem
    x_stem = w - v
    bowl_bottom = round(height * 0.42)
    t = v * 0.95
    joint_x = x_stem * 0.48
    leg_hw = slant_half_width(joint_x, bowl_bottom, t)
    leg = slanted(leg_hw, 0, joint_x, bowl_bottom + h / 2, t) & rect(0, 0, x_stem, height)
    return union(rect(x_stem, 0, w, height), d_bowl_left(S, 0, x_stem + 1, bowl_bottom, height), leg)


@both("dzhe-cy", "Dzhe-cy", 0x045F, 0x040F, ("S", "S"))
def dzhe(S, w, height):
    v, h = S.vstem, S.hstem
    x0 = round((w - v) / 2)
    return union(rect(0, 0, v, height), rect(w - v, 0, w, height),
                 rect(0, 0, w, h), rect(x0, TAIL, x0 + v, h))


@both("lje-cy", "Lje-cy", 0x0459, 0x0409, ("T", "R"))
def lje(S, w, height):
    v, h = S.vstem, S.hstem
    x_stem = round(w * 0.52)
    leg_x = round(w * 0.08)
    foot, center = hook_left(S, leg_x + v, -OVERSHOOT, ry=200)
    return union(
        soft_sign(S, x_stem, w, height),
        rect(leg_x, height - h, x_stem + v, height),
        rect(leg_x, center - 1, leg_x + v, height),
        foot,
    )


@both("nje-cy", "Nje-cy", 0x045A, 0x040A, ("S", "R"))
def nje(S, w, height):
    v, h = S.vstem, S.hstem
    x_stem = round(w * 0.50)
    bar_y = height * 0.5 - h / 2
    return union(rect(0, 0, v, height), rect(v, bar_y, x_stem, bar_y + h),
                 soft_sign(S, x_stem, w, height))


# --- Lowercase only --------------------------------------------------------------

@glyph("be-cy", [0x0431], ("R", "R"))
def be_cy(S):
    w, v = S.widths["be-cy"], S.round_vstem
    # A bowl with a stroke rising from its left side to a flag at ascender height.
    hook, center = hook_up(S, 0, round(w * 0.88), ASCENDER + OVERSHOOT, ry=220)
    return union(bowl(S, w), rect(0, X_HEIGHT * 0.5, v, center + 1), hook)


@glyph("ve-cy", [0x0432], ("S", "R"))
def ve_cy(S):
    S = S.tight
    w, v, h = S.widths["ve-cy"], S.vstem, S.hstem
    mid = round(X_HEIGHT * 0.52)
    return union(
        rect(0, 0, v, X_HEIGHT),
        d_bowl(S, 0, round(w * 0.92), mid - h, X_HEIGHT),
        d_bowl(S, 0, w, 0, mid),
    )


@glyph("ka-cy", [0x043A, 0x0138], ("S", "D"))
def ka_cy(S):
    w, v = S.widths["ka-cy"], S.vstem
    return rect(0, 0, v, X_HEIGHT) | arm_and_leg(S, v, w, X_HEIGHT)


@glyph("em-cy", [0x043C], ("S", "S"))
def em_cy(S):
    return m_shape(S, S.widths["em-cy"], X_HEIGHT)


@glyph("en-cy", [0x043D], ("S", "S"))
def en_cy(S):
    w, v, h = S.widths["en-cy"], S.vstem, S.hstem
    bar_y = X_HEIGHT * 0.5 - h / 2
    return union(rect(0, 0, v, X_HEIGHT), rect(w - v, 0, w, X_HEIGHT),
                 rect(v, bar_y, w - v, bar_y + h))


@glyph("te-cy", [0x0442], ("T", "T"))
def te_cy(S):
    w, v, h = S.widths["te-cy"], S.vstem, S.hstem
    x0 = round((w - v) / 2)
    return rect(x0, 0, x0 + v, X_HEIGHT) | rect(0, X_HEIGHT - h, w, X_HEIGHT)


@glyph("ef-cy", [0x0444], ("R", "R"))
def ef_cy(S):
    w, v = S.widths["ef-cy"], S.vstem
    x0 = round((w - v) / 2)
    return bowl(S, w) | rect(x0, DESCENDER, x0 + v, ASCENDER)


def _tshe_body(S, w):
    """ћ: h with a bar across the ascender; returns (shape, arch center)."""
    v, h = S.vstem, S.hstem
    x = round(w * 0.16)  # the bar sticks out left of the stem
    arch, center = arch_top(x, w, X_HEIGHT + OVERSHOOT, X_HEIGHT * 0.5, S)
    bar_y = round(X_HEIGHT + (ASCENDER - X_HEIGHT) * 0.45)
    return union(
        rect(x, 0, x + v, ASCENDER),
        rect(0, bar_y, x + v + round((w - x) * 0.45), bar_y + h),
        arch,
    ), center


@glyph("tshe-cy", [0x045B], ("T", "S"))
def tshe_cy(S):
    w, v = S.widths["tshe-cy"], S.vstem
    body, center = _tshe_body(S, w)
    return body | rect(w - v, 0, w, center + 1)


@glyph("dje-cy", [0x0452], ("T", "S"))
def dje_cy(S):
    w, v = S.widths["tshe-cy"], S.vstem
    body, center = _tshe_body(S, w)
    # Right stem descends into a hook to the left, as in j.
    bottom = DESCENDER - OVERSHOOT
    hook = hook_left(S, w, bottom, ry=220)[0] & rect(w * 0.55, bottom, w, 0)
    return union(body, rect(w - v, bottom + 219, w, center + 1), hook)


# --- Uppercase only --------------------------------------------------------------

@glyph("Be-cy", [0x0411], ("S", "R"))
def Be_cy(S):
    w, v, h = S.widths["Be-cy"], S.vstem, S.hstem
    bowl_top = round(CAP_HEIGHT * 0.56)
    return union(
        rect(0, 0, v, CAP_HEIGHT),
        rect(0, CAP_HEIGHT - h, round(w * 0.9), CAP_HEIGHT),
        d_bowl(S, 0, w, 0, bowl_top),
    )


@glyph("U-cy", [0x0423], ("D", "D"))
def U_cy(S):
    w, v = S.widths["U-cy"], S.vstem
    t = v * 0.95
    # Right stroke from the top right down to the baseline at the left;
    # the left arm joins it a third of the way up.
    top_hw = slant_half_width(w * 0.7, CAP_HEIGHT, t)
    xb = w * 0.22
    right = slanted(xb, 0, w - top_hw, CAP_HEIGHT, t)
    join_y = CAP_HEIGHT * 0.32
    join_x = xb + (w - top_hw - xb) * join_y / CAP_HEIGHT
    left = slanted(join_x, join_y, top_hw, CAP_HEIGHT, t)
    return (right | left) & rect(0, 0, w, CAP_HEIGHT)


@glyph("Ef-cy", [0x0424], ("R", "R"))
def Ef_cy(S):
    w, v = S.widths["Ef-cy"], S.vstem
    x0 = round((w - v) / 2)
    oval = ring(0, CAP_HEIGHT * 0.14, w, CAP_HEIGHT * 0.86, S.round_vstem, S.hstem)
    return oval | rect(x0, 0, x0 + v, CAP_HEIGHT)


def _Tshe_body(S, w):
    """Ћ: a T-like bar over a stem with an arch to the right; returns (shape, center)."""
    v, h = S.vstem, S.hstem
    x = round(w * 0.30)
    arch_top_y = round(CAP_HEIGHT * 0.62)
    arch, center = arch_top(x, w, arch_top_y, arch_top_y * 0.42, S)
    return union(
        rect(0, CAP_HEIGHT - h, round(w * 0.72), CAP_HEIGHT),
        rect(x, 0, x + v, CAP_HEIGHT),
        arch,
    ), center


@glyph("Tshe-cy", [0x040B], ("T", "S"))
def Tshe_cy(S):
    w, v = S.widths["Tshe-cy"], S.vstem
    body, center = _Tshe_body(S, w)
    return body | rect(w - v, 0, w, center + 1)


@glyph("Dje-cy", [0x0402], ("T", "S"))
def Dje_cy(S):
    w, v = S.widths["Tshe-cy"], S.vstem
    body, center = _Tshe_body(S, w)
    hook = hook_left(S, w, -OVERSHOOT, ry=220)[0] & rect(w * 0.6, -OVERSHOOT, w, CAP_HEIGHT)
    return union(body, rect(w - v, 219 - OVERSHOOT, w, center + 1), hook)


# --- Letters of Kazakh, Uzbek, Tatar, Bashkir, Tajik ------------------------------

def with_tail(S, shape, x_right):
    """Short descender hanging right of a stem that ends at x_right (қ ң җ ...)."""
    v = S.vstem
    return shape | rect(x_right - v * 0.25, TAIL, x_right + v * 0.75, S.hstem)


def with_center_tail(S, shape):
    """Short descender under the middle of the glyph (ҙ ҫ)."""
    x0, _, x1, _ = shape.path.bounds
    cx, v = (x0 + x1) / 2, S.vstem
    return shape | rect(cx - v / 2, TAIL, cx + v / 2, S.hstem)


def with_bar(S, shape, y, x0, x1):
    return shape | rect(x0, y, x1, y + S.hstem)


def _ghayn(S, height, w):
    v = S.vstem
    y = round(height * 0.46 - S.hstem / 2)
    return with_bar(S, ge(S, w, height), y, -130, v + 230)


@glyph("uni0493", [0x0493], ("T", "T"))
def ghestroke(S):
    return _ghayn(S, X_HEIGHT, S.widths["ge-cy"])


@glyph("uni0492", [0x0492], ("T", "T"))
def Ghestroke(S):
    return _ghayn(S, CAP_HEIGHT, S.widths["Ge-cy"])


@glyph("uni049B", [0x049B], ("S", "S"))
def kadescender(S):
    return with_tail(S, ka_cy(S), S.widths["ka-cy"])


@glyph("uni049A", [0x049A], ("S", "S"))
def Kadescender(S):
    return with_tail(S, K(S), S.widths["K"])


@glyph("uni04A3", [0x04A3], ("S", "S"))
def endescender(S):
    return with_tail(S, en_cy(S), S.widths["en-cy"])


@glyph("uni04A2", [0x04A2], ("S", "S"))
def Endescender(S):
    return with_tail(S, H(S), S.widths["H"])


@glyph("uni04B3", [0x04B3], ("D", "S"))
def hadescender(S):
    return with_tail(S, x(S), S.widths["x"])


@glyph("uni04B2", [0x04B2], ("D", "S"))
def Hadescender(S):
    return with_tail(S, X(S), S.widths["X"])


@glyph("uni0497", [0x0497], ("D", "S"))
def zhedescender(S):
    w = S.widths["zhe-cy"]
    return with_tail(S, zhe(S, w, X_HEIGHT), w)


@glyph("uni0496", [0x0496], ("D", "S"))
def Zhedescender(S):
    w = S.widths["Zhe-cy"]
    return with_tail(S, zhe(S, w, CAP_HEIGHT), w)


@glyph("uni04B7", [0x04B7], ("S", "S"))
def chedescender(S):
    w = S.widths["che-cy"]
    return with_tail(S, che(S, w, X_HEIGHT), w)


@glyph("uni04B6", [0x04B6], ("S", "S"))
def Chedescender(S):
    w = S.widths["Che-cy"]
    return with_tail(S, che(S, w, CAP_HEIGHT), w)


@glyph("uni0499", [0x0499], ("T", "R"))
def zedescender(S):
    return with_center_tail(S, ze(S, S.widths["ze-cy"], X_HEIGHT))


@glyph("uni0498", [0x0498], ("T", "R"))
def Zedescender(S):
    return with_center_tail(S, ze(S, S.widths["Ze-cy"], CAP_HEIGHT))


@glyph("uni04AB", [0x04AB], ("R", "R"))
def esdescender(S):
    return with_center_tail(S, c(S))


@glyph("uni04AA", [0x04AA], ("R", "R"))
def Esdescender(S):
    return with_center_tail(S, C(S))


@glyph("uni04E9", [0x04E9], ("R", "R"))
def obarred(S):
    S = S.tight
    w, h, rv = S.widths["o"], S.hstem, S.round_vstem
    mid = X_HEIGHT / 2
    return bowl(S, w) | rect(rv / 2, mid - h / 2, w - rv / 2, mid + h / 2)


@glyph("uni04E8", [0x04E8], ("R", "R"))
def Obarred(S):
    w, h, rv = S.widths["O"], S.hstem, S.round_vstem
    mid = CAP_HEIGHT / 2
    return bowl(S, w, top=CAP_HEIGHT + OVERSHOOT) | rect(rv / 2, mid - h / 2, w - rv / 2, mid + h / 2)


def _straight_u(S, w):
    cx, v = w / 2, S.vstem
    return v_shape(S, w, X_HEIGHT) | rect(cx - v / 2, DESCENDER, cx + v / 2, 1)


@glyph("uni04AF", [0x04AF], ("D", "D"))
def ustraight(S):
    return _straight_u(S, S.widths["v"])


@glyph("uni04B1", [0x04B1], ("D", "D"))
def ustraightstroke(S):
    w = S.widths["v"]
    return with_bar(S, _straight_u(S, w), -200, w * 0.2, w * 0.8)


@glyph("uni04B0", [0x04B0], ("D", "D"))
def Ustraightstroke(S):
    w = S.widths["Y"]
    return with_bar(S, Y(S), round(CAP_HEIGHT * 0.30), w * 0.22, w * 0.78)


@glyph("uni04BA", [0x04BA], ("S", "S"))
def Shha(S):
    w, v = S.widths["H"], S.vstem
    arch, center = arch_top(0, w, round(CAP_HEIGHT * 0.62), CAP_HEIGHT * 0.26, S)
    return union(rect(0, 0, v, CAP_HEIGHT), rect(w - v, 0, w, center + 1), arch)


@glyph("uni04A1", [0x04A1], ("T", "D"))
def kabashkir(S):
    v = S.vstem
    return ka_cy(S) | rect(-200, X_HEIGHT - S.hstem, v, X_HEIGHT)


@glyph("uni04A0", [0x04A0], ("T", "D"))
def Kabashkir(S):
    v = S.vstem
    return K(S) | rect(-240, CAP_HEIGHT - S.hstem, v, CAP_HEIGHT)

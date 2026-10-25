"""Latin glyphs."""

from dataclasses import replace

from ..geometry import polygon, rect, ring, slant_half_width, slanted, union
from ..style import ASCENDER, CAP_HEIGHT, DESCENDER, OVERSHOOT, X_HEIGHT
from .common import (T_HEIGHT, arch_bottom, arch_top, arm_and_leg, bowl, d_bowl,
                     dot, glyph, hook_down, hook_left, hook_up)
from .marks import comma_shape

TOP = X_HEIGHT + OVERSHOOT
CAP_TOP = CAP_HEIGHT + OVERSHOOT


# --- Shapes shared by lowercase and uppercase ----------------------------------

def s_shape(S, w, height):
    h, v = S.hstem, S.round_vstem
    top = height + OVERSHOOT
    mid = height / 2
    cx = w / 2
    # Upper bowl: left half plus the top stroke up to the terminal.
    upper = ring(w * 0.03, mid - h / 2, w * 0.97, top, v, h)
    upper = upper & (rect(0, mid - h, cx, top) | rect(cx, height * 0.72, w, top))
    # Lower bowl: right half plus the bottom stroke up to the terminal.
    lower = ring(0, -OVERSHOOT, w, mid + h / 2, v, h)
    lower = lower & (rect(cx, -OVERSHOOT, w, mid + h) | rect(0, -OVERSHOOT, cx, height * 0.26))
    return upper | lower


def v_shape(S, w, height):
    t = S.vstem
    hw = slant_half_width(w / 2, height, t)
    left = slanted(w / 2, 0, hw, height, t)
    right = slanted(w / 2, 0, w - hw, height, t)
    return (left | right) & rect(0, 0, w, height)


def w_shape(S, w, height):
    t = S.vstem * 0.95
    b1, b2 = w * 0.27, w * 0.73
    hw = slant_half_width(b1, height, t)
    strokes = union(
        slanted(b1, 0, hw, height, t),
        slanted(b1, 0, w / 2, height, t),
        slanted(b2, 0, w / 2, height, t),
        slanted(b2, 0, w - hw, height, t),
    )
    return strokes & rect(0, 0, w, height)


def x_shape(S, w, height):
    t = S.vstem
    hw = slant_half_width(w, height, t)
    strokes = slanted(hw, 0, w - hw, height, t) | slanted(w - hw, 0, hw, height, t)
    return strokes & rect(0, 0, w, height)


def z_shape(S, w, height):
    h, t = S.hstem, S.vstem
    hw = slant_half_width(w, height - 2 * h, t)
    diagonal = slanted(hw, h, w - hw, height - h, t)
    return union(
        rect(round(w * 0.04), height - h, w, height),
        rect(0, 0, w, h),
        diagonal & rect(0, 0, w, height),
    )


def c_shape(S, w, height):
    top = height + OVERSHOOT
    return bowl(S, w, top=top) - rect(w * 0.5, height * 0.32, w + 1, height * 0.68)


def m_shape(S, w, height, apex_frac=0.18):
    """Two stems joined by a V whose point stops above the baseline (M м)."""
    v = S.vstem
    t = v * 0.95
    cx = w / 2
    apex = height * apex_frac
    left = slanted(cx, apex, v, height, t)
    right = slanted(cx, apex, w - v, height, t)
    return union(
        rect(0, 0, v, height),
        rect(w - v, 0, w, height),
        (left | right) & rect(v, 0, w - v, height),
    )


# --- Lowercase: n family -----------------------------------------------------

@glyph("n", [0x006E], ("S", "S"))
def n(S):
    w, v = S.widths["n"], S.vstem
    arch, center = arch_top(0, w, TOP, X_HEIGHT * 0.5, S)
    return union(rect(0, 0, v, X_HEIGHT), rect(w - v, 0, w, center + 1), arch)


@glyph("h", [0x0068, 0x04BB], ("S", "S"))
def h(S):
    w, v = S.widths["h"], S.vstem
    arch, center = arch_top(0, w, TOP, X_HEIGHT * 0.5, S)
    return union(rect(0, 0, v, ASCENDER), rect(w - v, 0, w, center + 1), arch)


@glyph("m", [0x006D], ("S", "S"))
def m(S):
    w, v = S.widths["m"], S.vstem
    mid = round((w + v) / 2)  # right edge of the middle stem
    left, center = arch_top(0, mid, TOP, X_HEIGHT * 0.5, S)
    right, _ = arch_top(mid - v, w, TOP, X_HEIGHT * 0.5, S)
    return union(
        rect(0, 0, v, X_HEIGHT),
        rect(mid - v, 0, mid, center + 1),
        rect(w - v, 0, w, center + 1),
        left, right,
    )


@glyph("u", [0x0075], ("S", "S"))
def u(S):
    w, v = S.widths["u"], S.vstem
    arch, center = arch_bottom(0, w, -OVERSHOOT, X_HEIGHT * 0.5, S)
    return union(rect(0, center - 1, v, X_HEIGHT), rect(w - v, 0, w, X_HEIGHT), arch)


@glyph("r", [0x0072], ("S", "T"))
def r(S):
    w, v = S.widths["r"], S.vstem
    arch, _ = arch_top(0, S.widths["n"], TOP, X_HEIGHT * 0.5, S)
    arm = arch & rect(0, X_HEIGHT * 0.5, w, TOP)
    return union(rect(0, 0, v, X_HEIGHT), arm)


# --- Lowercase: o family -----------------------------------------------------

@glyph("o", [0x006F, 0x043E], ("R", "R"))
def o(S):
    return bowl(S, S.widths["o"])


@glyph("b", [0x0062], ("S", "R"))
def b(S):
    w, v = S.widths["b"], S.vstem
    return union(rect(0, 0, v, ASCENDER), bowl(S, w))


@glyph("d", [0x0064], ("R", "S"))
def d(S):
    w, v = S.widths["d"], S.vstem
    return union(rect(w - v, 0, w, ASCENDER), bowl(S, w))


@glyph("p", [0x0070, 0x0440], ("S", "R"))
def p(S):
    w, v = S.widths["p"], S.vstem
    return union(rect(0, DESCENDER, v, X_HEIGHT), bowl(S, w))


@glyph("q", [0x0071], ("R", "S"))
def q(S):
    w, v = S.widths["q"], S.vstem
    return union(rect(w - v, DESCENDER, w, X_HEIGHT), bowl(S, w))


@glyph("c", [0x0063, 0x0441], ("R", "R"))
def c(S):
    return c_shape(S, S.widths["c"], X_HEIGHT)


def e_shape(S, w, height):
    v, h = S.round_vstem, S.hstem
    top = height + OVERSHOOT
    # The eye takes half of the inner height left free by the bar.
    inner_top = top - h
    inner_bottom = -OVERSHOOT + h
    eye = (inner_top - inner_bottom - h) * 0.5
    bar_y = inner_top - eye - h
    shape = bowl(S, w, top=top) - rect(w * 0.5, height * 0.24, w + 1, bar_y)
    return shape | rect(v / 2, bar_y, w - v / 2, bar_y + h)


@glyph("e", [0x0065, 0x0435], ("R", "R"))
def e(S):
    return e_shape(S.tight, S.widths["e"], X_HEIGHT)


@glyph("a", [0x0061, 0x0430], ("R", "S"))
def a(S):
    S = S.tight
    w, v, h = S.widths["a"], S.vstem, S.hstem
    terminal_y = X_HEIGHT * 0.72
    arch, _ = arch_top(0, w, TOP, X_HEIGHT * 0.5, S)
    arch = arch & rect(0, terminal_y, w, TOP)
    bowl_top = X_HEIGHT * (0.60 if S.is_bold else 0.56)
    return union(
        arch,
        rect(w - v, 0, w, terminal_y + 1),
        ring(0, -OVERSHOOT, w, bowl_top, S.round_vstem, h),
    )


@glyph("g", [0x0067], ("R", "S"))
def g(S):
    w, v = S.widths["g"], S.vstem
    hook, center = arch_bottom(0, w, DESCENDER - OVERSHOOT, 260, S)
    hook = hook & rect(w * 0.1, DESCENDER - OVERSHOOT, w, center)
    return union(bowl(S, w), rect(w - v, center - 1, w, X_HEIGHT), hook)


@glyph("s", [0x0073, 0x0455], ("R", "R"))
def s(S):
    return s_shape(S.tight, S.widths["s"], X_HEIGHT)


# --- Lowercase: stems with dots, hooks and tails -----------------------------

@glyph("i", [0x0069, 0x0456], ("S", "S"))
def i(S):
    return rect(0, 0, S.vstem, X_HEIGHT) | dot(S, 0)


@glyph("dotlessi", [0x0131], ("S", "S"))
def dotlessi(S):
    return rect(0, 0, S.vstem, X_HEIGHT)


@glyph("dotlessj", [0x0237], ("T", "S"))
def dotlessj(S):
    w, v = S.widths["j"], S.vstem
    hook, center = hook_left(S, w, DESCENDER - OVERSHOOT)
    return rect(w - v, center - 1, w, X_HEIGHT) | hook


@glyph("j", [0x006A, 0x0458], ("T", "S"))
def j(S):
    w, v = S.widths["j"], S.vstem
    hook, center = hook_left(S, w, DESCENDER - OVERSHOOT)
    return union(rect(w - v, center - 1, w, X_HEIGHT), hook, dot(S, w - v))


@glyph("l", [0x006C], ("S", "T"))
def l(S):
    w, v = S.widths["l"], S.vstem
    # A tail at the foot tells l apart from I and 1.
    tail, center = hook_down(S, 0, w, -OVERSHOOT)
    return rect(0, center - 1, v, ASCENDER) | tail


@glyph("t", [0x0074], ("T", "T"))
def t(S):
    w, v, h = S.widths["t"], S.vstem, S.hstem
    x = round(w * 0.24)  # stem position; the bar extends left of it
    tail, center = hook_down(S, x, w, -OVERSHOOT)
    return union(
        rect(x, center - 1, x + v, T_HEIGHT),
        rect(0, X_HEIGHT - h, w - round(w * 0.04), X_HEIGHT),
        tail,
    )


@glyph("f", [0x0066], ("T", "T"))
def f(S):
    w, v, h = S.widths["f"], S.vstem, S.hstem
    x = round(w * 0.24)
    hook, center = hook_up(S, x, w, ASCENDER + OVERSHOOT)
    return union(
        rect(x, 0, x + v, center + 1),
        rect(0, X_HEIGHT - h, w - round(w * 0.1), X_HEIGHT),
        hook,
    )


@glyph("k", [0x006B], ("S", "D"))
def k(S):
    w, v = S.widths["k"], S.vstem
    return rect(0, 0, v, ASCENDER) | arm_and_leg(S, v, w, X_HEIGHT)


# --- Lowercase: diagonals ----------------------------------------------------

@glyph("v", [0x0076], ("D", "D"))
def v(S):
    return v_shape(S, S.widths["v"], X_HEIGHT)


@glyph("y", [0x0079, 0x0443], ("D", "D"))
def y(S):
    w = S.widths["y"]
    t = S.vstem
    hw = slant_half_width(w / 2, X_HEIGHT, t)
    left = slanted(w / 2, 0, hw, X_HEIGHT, t)
    # The right stroke continues below the baseline at the same slope.
    slope = (w / 2 - hw) / X_HEIGHT
    xd = w / 2 + slope * DESCENDER
    right = slanted(xd, DESCENDER, w - hw, X_HEIGHT, t)
    return (left | right) & rect(0, DESCENDER, w, X_HEIGHT)


@glyph("w", [0x0077], ("D", "D"))
def w_(S):
    return w_shape(S, S.widths["w"], X_HEIGHT)


@glyph("x", [0x0078, 0x0445], ("D", "D"))
def x(S):
    return x_shape(S, S.widths["x"], X_HEIGHT)


@glyph("z", [0x007A], ("T", "T"))
def z(S):
    return z_shape(S, S.widths["z"], X_HEIGHT)


# --- Uppercase ---------------------------------------------------------------

@glyph("A", [0x0041, 0x0410], ("D", "D"))
def A(S):
    w, h, t = S.widths["A"], S.hstem, S.vstem
    hw = slant_half_width(w / 2, CAP_HEIGHT, t)
    apex = w / 2
    left = slanted(hw, 0, apex, CAP_HEIGHT, t)
    right = slanted(w - hw, 0, apex, CAP_HEIGHT, t)
    outline = polygon([(0, 0), (apex - hw, CAP_HEIGHT), (apex + hw, CAP_HEIGHT), (w, 0)])
    bar_y = round(CAP_HEIGHT * 0.28)
    bar = rect(0, bar_y, w, bar_y + h) & outline
    return ((left | right) & rect(0, 0, w, CAP_HEIGHT)) | bar


@glyph("B", [0x0042, 0x0412], ("S", "R"))
def B(S):
    w, v, h = S.widths["B"], S.vstem, S.hstem
    mid = round(CAP_HEIGHT * 0.53)
    return union(
        rect(0, 0, v, CAP_HEIGHT),
        d_bowl(S, 0, round(w * 0.9), mid - h, CAP_HEIGHT),
        d_bowl(S, 0, w, 0, mid),
    )


@glyph("C", [0x0043, 0x0421], ("R", "R"))
def C(S):
    return c_shape(S, S.widths["C"], CAP_HEIGHT)


@glyph("D", [0x0044], ("S", "R"))
def D(S):
    w, v = S.widths["D"], S.vstem
    return rect(0, 0, v, CAP_HEIGHT) | d_bowl(S, 0, w, 0, CAP_HEIGHT, k=0.62)


def e_bars(S, w, middle=0.9, bottom=True):
    """Stem with top, middle and (optionally) bottom bars: E F."""
    v, h = S.vstem, S.hstem
    mid = round(CAP_HEIGHT * 0.5 - h / 2)
    parts = [
        rect(0, 0, v, CAP_HEIGHT),
        rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT),
        rect(0, mid, round(w * middle), mid + h),
    ]
    if bottom:
        parts.append(rect(0, 0, w, h))
    return union(*parts)


@glyph("E", [0x0045, 0x0415], ("S", "T"))
def E(S):
    return e_bars(S, S.widths["E"])


@glyph("F", [0x0046], ("S", "T"))
def F(S):
    return e_bars(S, S.widths["F"], bottom=False)


@glyph("G", [0x0047], ("R", "S"))
def G(S):
    w, h = S.widths["G"], S.hstem
    bar_top = round(CAP_HEIGHT * 0.5)
    shape = bowl(S, w, top=CAP_TOP) - rect(w * 0.5, bar_top, w + 1, CAP_HEIGHT * 0.70)
    return shape | rect(round(w * 0.56), bar_top - h, w, bar_top)


@glyph("H", [0x0048, 0x041D], ("S", "S"))
def H(S):
    w, v, h = S.widths["H"], S.vstem, S.hstem
    bar_y = CAP_HEIGHT * 0.5 - h / 2 + 10
    return union(
        rect(0, 0, v, CAP_HEIGHT),
        rect(w - v, 0, w, CAP_HEIGHT),
        rect(v, bar_y, w - v, bar_y + h),
    )


@glyph("I", [0x0049, 0x0406], ("S", "S"))
def I_(S):
    return rect(0, 0, S.vstem, CAP_HEIGHT)


@glyph("J", [0x004A, 0x0408], ("T", "S"))
def J(S):
    w, v = S.widths["J"], S.vstem
    hook, center = hook_left(S, w, -OVERSHOOT, ry=300)
    return rect(w - v, center - 1, w, CAP_HEIGHT) | hook


@glyph("K", [0x004B, 0x041A], ("S", "D"))
def K(S):
    w, v = S.widths["K"], S.vstem
    return rect(0, 0, v, CAP_HEIGHT) | arm_and_leg(S, v, w, CAP_HEIGHT)


@glyph("L", [0x004C], ("S", "T"))
def L(S):
    w, v, h = S.widths["L"], S.vstem, S.hstem
    return rect(0, 0, v, CAP_HEIGHT) | rect(0, 0, w, h)


@glyph("M", [0x004D, 0x041C], ("S", "S"))
def M_(S):
    return m_shape(S, S.widths["M"], CAP_HEIGHT, apex_frac=0.12)


@glyph("N", [0x004E], ("S", "S"))
def N(S):
    w, v = S.widths["N"], S.vstem
    diagonal = slanted(w - v, 0, v, CAP_HEIGHT, v * 0.95) & rect(v, 0, w - v, CAP_HEIGHT)
    return union(rect(0, 0, v, CAP_HEIGHT), rect(w - v, 0, w, CAP_HEIGHT), diagonal)


@glyph("O", [0x004F, 0x041E], ("R", "R"))
def O(S):
    return bowl(S, S.widths["O"], top=CAP_TOP)


@glyph("P", [0x0050, 0x0420], ("S", "R"))
def P(S):
    w, v = S.widths["P"], S.vstem
    bowl_bottom = round(CAP_HEIGHT * 0.42)
    return rect(0, 0, v, CAP_HEIGHT) | d_bowl(S, 0, w, bowl_bottom, CAP_HEIGHT)


@glyph("Q", [0x0051], ("R", "R"))
def Q(S):
    w = S.widths["Q"]
    tail = slanted(w * 0.92, -220, w * 0.64, CAP_HEIGHT * 0.20, S.vstem)
    return bowl(S, w, top=CAP_TOP) | (tail & rect(0, -220, w, CAP_HEIGHT))


@glyph("R", [0x0052], ("S", "D"))
def R(S):
    w, v, h = S.widths["R"], S.vstem, S.hstem
    bowl_bottom = round(CAP_HEIGHT * 0.42)
    t = v * 0.95
    joint_x = w * 0.42
    hw = slant_half_width(w - joint_x, bowl_bottom, t)
    leg = slanted(w - hw, 0, joint_x, bowl_bottom + h / 2, t) & rect(v, 0, w, CAP_HEIGHT)
    return union(
        rect(0, 0, v, CAP_HEIGHT),
        d_bowl(S, 0, round(w * 0.96), bowl_bottom, CAP_HEIGHT),
        leg,
    )


@glyph("S", [0x0053, 0x0405], ("R", "R"))
def S_(S):
    return s_shape(S, S.widths["S"], CAP_HEIGHT)


@glyph("T", [0x0054, 0x0422], ("T", "T"))
def T(S):
    w, v, h = S.widths["T"], S.vstem, S.hstem
    x0 = round((w - v) / 2)
    return rect(x0, 0, x0 + v, CAP_HEIGHT) | rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT)


@glyph("U", [0x0055], ("S", "S"))
def U(S):
    w, v = S.widths["U"], S.vstem
    arch, center = arch_bottom(0, w, -OVERSHOOT, CAP_HEIGHT * 0.36, S)
    return union(rect(0, center - 1, v, CAP_HEIGHT), rect(w - v, center - 1, w, CAP_HEIGHT), arch)


@glyph("V", [0x0056], ("D", "D"))
def V(S):
    return v_shape(S, S.widths["V"], CAP_HEIGHT)


@glyph("W", [0x0057], ("D", "D"))
def W(S):
    return w_shape(S, S.widths["W"], CAP_HEIGHT)


@glyph("X", [0x0058, 0x0425], ("D", "D"))
def X(S):
    return x_shape(S, S.widths["X"], CAP_HEIGHT)


@glyph("Y", [0x0059, 0x04AE], ("D", "D"))
def Y(S):
    w, v = S.widths["Y"], S.vstem
    t = v * 0.95
    fork = CAP_HEIGHT * 0.45
    cx = w / 2
    hw = slant_half_width(cx, CAP_HEIGHT - fork, t)
    arms = slanted(cx, fork, hw, CAP_HEIGHT, t) | slanted(cx, fork, w - hw, CAP_HEIGHT, t)
    x0 = cx - v / 2
    return (arms & rect(0, fork, w, CAP_HEIGHT)) | rect(x0, 0, x0 + v, fork + 1)


@glyph("Z", [0x005A], ("T", "T"))
def Z(S):
    return z_shape(S, S.widths["Z"], CAP_HEIGHT)


# --- Letters that are not base + mark ---------------------------------------------

def _bar_across(shape, y, x0, x1, S):
    return shape | rect(x0, y, x1, y + S.hstem)


@glyph("germandbls", [0x00DF], ("S", "R"))
def germandbls(S):
    w, v, h, rv = S.widths["germandbls"], S.vstem, S.hstem, S.round_vstem
    top = ASCENDER + OVERSHOOT
    mid = round(X_HEIGHT * 0.66)
    wu = round(w * 0.86)
    upper = ring(0, mid - h / 2, wu, top, rv, h)
    cu = (mid - h / 2 + top) / 2
    upper = upper & (rect(0, cu, wu, top) | rect(wu / 2, mid - h / 2, wu, cu))
    lower = ring(round(w * 0.20), -OVERSHOOT, w, mid + h / 2, rv, h)
    cl = (mid + h / 2 - OVERSHOOT) / 2
    lower = lower & (rect(wu / 2, cl, w, mid + h / 2) | rect((w * 0.2 + w) / 2, -OVERSHOOT, w, cl)
                     | rect(v + 120, -OVERSHOOT, (w * 0.2 + w) / 2, X_HEIGHT * 0.2))
    return union(rect(0, 0, v, cu + 1), upper, lower)


@glyph("ae", [0x00E6, 0x04D5], ("R", "R"))
def ae(S):
    w = S.widths["ae"]
    wa = round(w * 0.50)
    left = a(replace_width(S, "a", wa))
    right = e(replace_width(S, "e", w - wa + S.vstem))
    return left | right.translate(wa - S.vstem * 1.5)


@glyph("oe", [0x0153], ("R", "R"))
def oe(S):
    w = S.widths["oe"]
    wo = round(w * 0.52)
    left = bowl(S, wo)
    right = e(replace_width(S, "e", w - wo + S.round_vstem))
    return left | right.translate(wo - S.round_vstem)


@glyph("AE", [0x00C6, 0x04D4], ("D", "T"))
def AE(S):
    w, v, h = S.widths["AE"], S.vstem, S.hstem
    xs = round(w * 0.46)
    hw = slant_half_width(xs, CAP_HEIGHT, v)
    top_x = xs + v * 0.5
    diagonal = slanted(hw, 0, top_x, CAP_HEIGHT, v) & rect(0, 0, xs + v, CAP_HEIGHT)
    bar_y = round(CAP_HEIGHT * 0.28)
    bar_x = hw + (top_x - hw) * bar_y / CAP_HEIGHT  # diagonal centre line at bar height
    mid = round(CAP_HEIGHT * 0.5 - h / 2)
    return union(
        diagonal,
        rect(bar_x, bar_y, xs, bar_y + h),
        rect(xs, 0, xs + v, CAP_HEIGHT),
        rect(xs, CAP_HEIGHT - h, w, CAP_HEIGHT),
        rect(xs, mid, round(w * 0.94), mid + h),
        rect(xs, 0, w, h),
    )


@glyph("OE", [0x0152], ("R", "T"))
def OE(S):
    w, v, h = S.widths["OE"], S.vstem, S.hstem
    xs = round(w * 0.52)
    half = ring(0, -OVERSHOOT, 2 * xs, CAP_TOP, S.round_vstem, h) & rect(0, -OVERSHOOT, xs, CAP_TOP)
    mid = round(CAP_HEIGHT * 0.5 - h / 2)
    return union(
        half,
        rect(xs - v, 0, xs, CAP_HEIGHT),
        rect(xs - v, CAP_HEIGHT - h, w, CAP_HEIGHT),
        rect(xs - v, mid, round(w * 0.94), mid + h),
        rect(xs - v, 0, w, h),
    )


@glyph("eth", [0x00F0], ("R", "R"))
def eth(S):
    w, v = S.widths["o"], S.vstem
    top = ASCENDER
    stroke = slanted(w - S.round_vstem * 0.5, X_HEIGHT * 0.5, w * 0.42, top, v) & rect(0, X_HEIGHT * 0.5, w, top)
    cross = slanted(w * 0.30, X_HEIGHT + 170, w * 0.88, X_HEIGHT + 330, S.hstem * 1.1)
    return union(bowl(S, w), stroke, cross & rect(0, 0, w, top))


@glyph("thorn", [0x00FE], ("S", "R"))
def thorn(S):
    w, v = S.widths["b"], S.vstem
    return rect(0, DESCENDER, v, ASCENDER) | bowl(S, w)


@glyph("Thorn", [0x00DE], ("S", "R"))
def Thorn(S):
    w, v = S.widths["P"], S.vstem
    return rect(0, 0, v, CAP_HEIGHT) | d_bowl(S, 0, w, round(CAP_HEIGHT * 0.20), round(CAP_HEIGHT * 0.80))


def _slashed(shape, S, x0, y0, x1, y1):
    return shape | slanted(x0, y0, x1, y1, S.vstem * 0.9)


@glyph("oslash", [0x00F8], ("R", "R"))
def oslash(S):
    w = S.widths["o"]
    return _slashed(bowl(S, w), S, w * 0.10, -90, w * 0.90, X_HEIGHT + 90)


@glyph("Oslash", [0x00D8], ("R", "R"))
def Oslash(S):
    w = S.widths["O"]
    return _slashed(O(S), S, w * 0.12, -110, w * 0.88, CAP_HEIGHT + 110)


@glyph("dcroat", [0x0111], ("R", "T"))
def dcroat(S):
    w, v = S.widths["d"], S.vstem
    y = X_HEIGHT + round((ASCENDER - X_HEIGHT) * 0.35)
    return _bar_across(d(S), y, w - v - 240, w + 80, S)


@glyph("Dcroat", [0x0110, 0x00D0], ("T", "R"))
def Dcroat(S):
    v = S.vstem
    y = round(CAP_HEIGHT * 0.5 - S.hstem / 2)
    return _bar_across(D(S), y, -130, v + 260, S)


@glyph("hbar", [0x0127], ("T", "S"))
def hbar(S):
    v = S.vstem
    y = X_HEIGHT + round((ASCENDER - X_HEIGHT) * 0.40)
    return _bar_across(h(S), y, -120, v + 300, S)


@glyph("Hbar", [0x0126], ("T", "T"))
def Hbar(S):
    w = S.widths["H"]
    return _bar_across(H(S), round(CAP_HEIGHT * 0.74), -100, w + 100, S)


def _stroke_across(shape, S, x, y, height):
    """Slanted bar of ł Ł across a stem centred at x."""
    return shape | slanted(x - 230, y, x + 230, y + height, S.hstem * 1.15)


@glyph("lslash", [0x0142], ("T", "T"))
def lslash(S):
    v = S.vstem
    return _stroke_across(l(S), S, v / 2, X_HEIGHT * 0.55, 320)


@glyph("Lslash", [0x0141], ("T", "T"))
def Lslash(S):
    v = S.vstem
    return _stroke_across(L(S), S, v / 2, CAP_HEIGHT * 0.36, 340)


@glyph("ldot", [0x0140], ("S", "S"))
def ldot(S):
    w, v = S.widths["l"], S.vstem
    p = round(S.vstem * 1.12)
    return l(S) | rect(w + 100, X_HEIGHT * 0.5, w + 100 + p, X_HEIGHT * 0.5 + p)


@glyph("Ldot", [0x013F], ("S", "T"))
def Ldot(S):
    v = S.vstem
    p = round(S.vstem * 1.12)
    return L(S) | rect(v + 260, CAP_HEIGHT * 0.45, v + 260 + p, CAP_HEIGHT * 0.45 + p)


@glyph("eng", [0x014B], ("S", "S"))
def eng(S):
    w, v = S.widths["n"], S.vstem
    arch, center = arch_top(0, w, TOP, X_HEIGHT * 0.5, S)
    hook, hc = hook_left(S, w, DESCENDER - OVERSHOOT)
    hook = hook & rect(w * 0.45, DESCENDER - OVERSHOOT, w, 0)
    return union(rect(0, 0, v, X_HEIGHT), rect(w - v, hc - 1, w, center + 1), arch, hook)


@glyph("Eng", [0x014A], ("S", "S"))
def Eng(S):
    w, v = S.widths["N"], S.vstem
    hook, hc = hook_left(S, w, DESCENDER - OVERSHOOT)
    hook = hook & rect(w * 0.5, DESCENDER - OVERSHOOT, w, 0)
    return union(N(S), rect(w - v, hc - 1, w, 1), hook)


@glyph("ij", [0x0133], ("S", "S"))
def ij(S):
    wi = S.vstem
    return i(S) | j(S).translate(wi + S.sb_straight * 2 - (S.widths["j"] - S.vstem) * 0.6)


@glyph("IJ", [0x0132], ("S", "S"))
def IJ(S):
    return I_(S) | J(S).translate(S.vstem + S.sb_straight * 2 - 60)


@glyph("napostrophe", [0x0149], ("S", "S"))
def napostrophe(S):
    p = round(S.vstem * 1.12)
    return comma_shape(S).translate(0, CAP_HEIGHT - p) | n(S).translate(p + 200)


@glyph("longs", [0x017F], ("S", "T"))
def longs(S):
    w, v = S.widths["f"], S.vstem
    hook, center = hook_up(S, 0, round(w * 0.76), ASCENDER + OVERSHOOT)
    return rect(0, 0, v, center + 1) | hook


@glyph("florin", [0x0192], ("T", "T"))
def florin(S):
    w, v, h = S.widths["f"] + 120, S.vstem, S.hstem
    x = round(w * 0.42)
    top_hook, tc = hook_up(S, x, w, ASCENDER + OVERSHOOT)
    bottom_hook, bc = hook_left(S, x + v, DESCENDER - OVERSHOOT)
    return union(rect(x, bc - 1, x + v, tc + 1), top_hook, bottom_hook,
                 rect(round(w * 0.18), X_HEIGHT - h, round(w * 0.82), X_HEIGHT))


@glyph("schwa", [0x0259, 0x04D9], ("R", "R"))
def schwa(S):
    w = S.widths["e"]
    return e_shape(S.tight, w, X_HEIGHT).rotate180(w / 2, X_HEIGHT / 2)


@glyph("Schwa", [0x018F, 0x04D8], ("R", "R"))
def Schwa(S):
    w = S.widths["O"] - 120
    return e_shape(S, w, CAP_HEIGHT).rotate180(w / 2, CAP_HEIGHT / 2)


def replace_width(S, name, w):
    return replace(S, widths={**S.widths, name: w})


@glyph("Tbar", [0x0166], ("T", "T"))
def Tbar(S):
    w, v = S.widths["T"], S.vstem
    x = (w - v) / 2
    return _bar_across(T(S), round(CAP_HEIGHT * 0.45), x - 220, x + v + 220, S)


@glyph("tbar", [0x0167], ("T", "T"))
def tbar(S):
    w, v = S.widths["t"], S.vstem
    x = round(w * 0.24)
    return _bar_across(t(S), round(X_HEIGHT * 0.45), x - 140, x + v + 200, S)

"""Greek glyphs (modern monotonic).

Capitals identical to Latin or Cyrillic ones are mapped to those glyphs
(see the code point lists in latin.py and below). Letters with tonos and
dialytika are generated in `composites.py`.
"""

from ..geometry import rect, ring, slant_half_width, slanted, union
from ..style import ASCENDER, CAP_HEIGHT, DESCENDER, OVERSHOOT, X_HEIGHT
from .common import (GLYPHS, arch_bottom, arch_top, bowl, d_bowl, glyph,
                     hook_down)
from .cyrillic import ze
from .latin import c_shape, v_shape, x_shape

TOP = X_HEIGHT + OVERSHOOT
CAP_TOP = CAP_HEIGHT + OVERSHOOT


def _add_codes(name, *codes):
    GLYPHS[name].unicodes.extend(codes)


# Shared shapes: Γ = Г, Π = П, Φ = Ф, κ = к, ο = o, ν = v, φ = ф,
# Greek question mark = semicolon, ano teleia = middle dot.
for _name, _codes in {
    "Ge-cy": [0x0393], "Pe-cy": [0x03A0], "Ef-cy": [0x03A6], "ka-cy": [0x03BA],
    "o": [0x03BF], "v": [0x03BD], "ef-cy": [0x03C6],
    "A": [0x0391], "B": [0x0392], "E": [0x0395], "Z": [0x0396], "H": [0x0397],
    "I": [0x0399], "K": [0x039A], "M": [0x039C], "N": [0x039D], "O": [0x039F],
    "P": [0x03A1], "T": [0x03A4], "Y": [0x03A5], "X": [0x03A7],
}.items():
    _add_codes(_name, *_codes)


# --- Lowercase -----------------------------------------------------------------------

@glyph("alpha", [0x03B1], ("R", "S"))
def alpha(S):
    w, v = S.widths["o"], S.vstem
    return bowl(S, w) | rect(w - v, 0, w, X_HEIGHT)


@glyph("beta", [0x03B2], ("S", "R"))
def beta(S):
    S = S.tight
    w, v, h = S.widths["b"] - 60, S.vstem, S.hstem
    mid = round(X_HEIGHT * 0.62)
    return union(
        rect(0, DESCENDER, v, ASCENDER),
        d_bowl(S, 0, round(w * 0.86), mid - h, ASCENDER),
        d_bowl(S, 0, w, -OVERSHOOT, mid),
    )


@glyph("gamma", [0x03B3], ("D", "D"))
def gamma(S):
    w, v = S.widths["v"], S.vstem
    cx = w / 2
    fork = -60
    arms = v_shape(S, w, X_HEIGHT - fork).translate(0, fork) & rect(0, fork, w, X_HEIGHT)
    loop = ring(cx - 120, DESCENDER, cx + 120, fork + 60, v * 0.8, S.hstem * 0.8)
    return arms | loop


@glyph("delta", [0x03B4], ("R", "R"))
def delta(S):
    w, v, h = S.widths["o"], S.vstem, S.hstem
    stroke = slanted(w * 0.32, ASCENDER - h * 0.5, w * 0.58, X_HEIGHT, v) & rect(0, X_HEIGHT - 40, w, ASCENDER)
    return union(bowl(S, w), stroke, rect(w * 0.22, ASCENDER - h, w * 0.86, ASCENDER))


@glyph("epsilon", [0x03B5], ("R", "T"))
def epsilon(S):
    w = S.widths["ze-cy"]
    return ze(S, w, X_HEIGHT).mirror_x(w / 2)


@glyph("zeta", [0x03B6], ("R", "T"))
def zeta(S):
    w, v, h = S.widths["z"], S.vstem, S.hstem
    hw = slant_half_width(w * 0.7, ASCENDER, v)
    diagonal = slanted(hw, h, w * 0.86 - hw, ASCENDER - h, v) & rect(0, 0, w, ASCENDER)
    return union(
        rect(w * 0.18, ASCENDER - h, w, ASCENDER),
        diagonal,
        rect(0, 0, w * 0.86, h),
        rect(w * 0.86 - v, -300, w * 0.86, h),
    )


@glyph("eta", [0x03B7], ("S", "S"))
def eta(S):
    w, v = S.widths["n"], S.vstem
    arch, center = arch_top(0, w, TOP, X_HEIGHT * 0.5, S)
    return union(rect(0, 0, v, X_HEIGHT), rect(w - v, DESCENDER, w, center + 1), arch)


@glyph("theta", [0x03B8], ("R", "R"))
def theta(S):
    S = S.tight
    w, h, rv = S.widths["o"] - 80, S.hstem, S.round_vstem
    mid = (ASCENDER - OVERSHOOT) / 2
    return bowl(S, w, top=ASCENDER + OVERSHOOT) | rect(rv / 2, mid - h / 2, w - rv / 2, mid + h / 2)


@glyph("iota", [0x03B9], ("S", "T"))
def iota(S):
    v = S.vstem
    tail, center = hook_down(S, 0, 340 if not S.is_bold else 420, -OVERSHOOT)
    return rect(0, center - 1, v, X_HEIGHT) | tail


@glyph("lambda", [0x03BB], ("D", "D"))
def lambda_(S):
    w, v = S.widths["v"], S.vstem
    hw = slant_half_width(w * 0.7, ASCENDER, v)
    long = slanted(w - hw, 0, w * 0.22, ASCENDER, v)
    leg = slanted(hw, 0, w * 0.56, X_HEIGHT * 0.64, v)
    return (long | leg) & rect(0, 0, w, ASCENDER)


@glyph("mu", [0x03BC, 0x00B5], ("S", "S"))
def mu(S):
    w, v = S.widths["u"], S.vstem
    arch, center = arch_bottom(0, w, -OVERSHOOT, X_HEIGHT * 0.5, S)
    return union(rect(0, DESCENDER, v, X_HEIGHT), rect(w - v, 0, w, X_HEIGHT), arch)


@glyph("xi", [0x03BE], ("R", "T"))
def xi(S):
    w, h = S.widths["ze-cy"], S.hstem
    body = ze(S.tight, w, X_HEIGHT + 220).mirror_x(w / 2)
    return union(body, rect(w * 0.2, ASCENDER - h, w, ASCENDER),
                 rect(w * 0.12, X_HEIGHT + 60, w * 0.12 + S.vstem, ASCENDER),
                 rect(w * 0.7, -300, w * 0.7 + S.vstem, h))


@glyph("pi", [0x03C0], ("T", "T"))
def pi(S):
    w, v, h = S.widths["n"] + 120, S.vstem, S.hstem
    x1, x2 = round(w * 0.16), round(w * 0.84) - v
    return union(rect(0, X_HEIGHT - h, w, X_HEIGHT), rect(x1, 0, x1 + v, X_HEIGHT),
                 rect(x2, 0, x2 + v, X_HEIGHT))


@glyph("rho", [0x03C1], ("S", "R"))
def rho(S):
    w, v = S.widths["p"], S.vstem
    return bowl(S, w) | rect(0, DESCENDER, v, X_HEIGHT * 0.5)


@glyph("sigma", [0x03C3], ("R", "T"))
def sigma(S):
    w, h = S.widths["o"] + 80, S.hstem
    wb = round(w * 0.86)
    return bowl(S, wb) | rect(wb * 0.5, X_HEIGHT - h, w, X_HEIGHT)


@glyph("sigmafinal", [0x03C2], ("R", "T"))
def sigmafinal(S):
    w, v, h = S.widths["c"], S.vstem, S.hstem
    x = round(w * 0.52)
    return c_shape(S, w, X_HEIGHT) | rect(x, -300, x + v, h)


@glyph("tau", [0x03C4], ("T", "T"))
def tau(S):
    w, v, h = S.widths["t"] + 120, S.vstem, S.hstem
    x = round(w * 0.42)
    tail, center = hook_down(S, x, x + 240, -OVERSHOOT)
    return union(rect(0, X_HEIGHT - h, w, X_HEIGHT), rect(x, center - 1, x + v, X_HEIGHT), tail)


def _upsilon(S, w):
    v, rv = S.vstem, S.round_vstem
    arch, center = arch_bottom(0, w, -OVERSHOOT, X_HEIGHT * 0.5, S)
    return union(rect(0, center - 1, v, X_HEIGHT), rect(w - rv, center - 1, w, X_HEIGHT), arch)


@glyph("upsilon", [0x03C5], ("S", "R"))
def upsilon(S):
    return _upsilon(S, S.widths["u"])


@glyph("chi", [0x03C7], ("D", "D"))
def chi(S):
    w = S.widths["x"]
    depth = round(DESCENDER * 0.8)
    return x_shape(S, w, X_HEIGHT - depth).translate(0, depth)


@glyph("psi", [0x03C8], ("S", "R"))
def psi(S):
    w, v = S.widths["u"] + 160, S.vstem
    x = (w - v) / 2
    return _upsilon(S, w) | rect(x, DESCENDER, x + v, ASCENDER)


@glyph("omega", [0x03C9], ("R", "R"))
def omega(S):
    w, v, rv = S.widths["w"] - 120, S.vstem, S.round_vstem
    mid = (w + v) / 2
    left, center = arch_bottom(0, mid, -OVERSHOOT, X_HEIGHT * 0.55, S)
    right, _ = arch_bottom(mid - v, w, -OVERSHOOT, X_HEIGHT * 0.55, S)
    return union(left, right, rect(0, center - 1, rv, X_HEIGHT), rect(w - rv, center - 1, w, X_HEIGHT),
                 rect(mid - v, center - 1, mid, X_HEIGHT * 0.62))


# --- Uppercase -----------------------------------------------------------------------

def _lambda_shape(S, w):
    return v_shape(S, w, CAP_HEIGHT).transform(1, 0, 0, -1, 0, CAP_HEIGHT)


@glyph("Lambda", [0x039B], ("D", "D"))
def Lambda(S):
    return _lambda_shape(S, S.widths["A"])


@glyph("Delta", [0x0394], ("D", "D"))
def Delta(S):
    w = S.widths["A"]
    return _lambda_shape(S, w) | rect(0, 0, w, S.hstem)


@glyph("Theta", [0x0398], ("R", "R"))
def Theta(S):
    w, h = S.widths["O"], S.hstem
    mid = CAP_HEIGHT / 2
    return bowl(S, w, top=CAP_TOP) | rect(w * 0.30, mid - h / 2, w * 0.70, mid + h / 2)


@glyph("Xi", [0x039E], ("T", "T"))
def Xi(S):
    w, h = S.widths["E"] + 100, S.hstem
    mid = round(CAP_HEIGHT / 2 - h / 2)
    return union(rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT), rect(w * 0.12, mid, w * 0.88, mid + h),
                 rect(0, 0, w, h))


@glyph("Sigma", [0x03A3], ("T", "T"))
def Sigma(S):
    w, v, h = S.widths["E"] + 120, S.vstem, S.hstem
    mid = CAP_HEIGHT / 2
    hw = slant_half_width(w * 0.5, mid, v)
    upper = slanted(w * 0.52, mid, hw + 20, CAP_HEIGHT - h / 2, v)
    lower = slanted(hw + 20, h / 2, w * 0.52, mid, v)
    return union(rect(0, CAP_HEIGHT - h, w, CAP_HEIGHT), rect(0, 0, w, h),
                 (upper | lower) & rect(0, 0, w, CAP_HEIGHT))


@glyph("Psi", [0x03A8], ("S", "S"))
def Psi(S):
    w, v = S.widths["U"] + 140, S.vstem
    arch, center = arch_bottom(0, w, CAP_HEIGHT * 0.28, CAP_HEIGHT * 0.22, S)
    x = (w - v) / 2
    return union(arch, rect(0, center - 1, v, CAP_HEIGHT), rect(w - v, center - 1, w, CAP_HEIGHT),
                 rect(x, 0, x + v, CAP_HEIGHT))


@glyph("Omega", [0x03A9, 0x2126], ("T", "T"))
def Omega(S):
    w, v, h, rv = S.widths["O"], S.vstem, S.hstem, S.round_vstem
    bottom = round(CAP_HEIGHT * 0.12)
    center = (bottom + CAP_TOP) / 2
    body = ring(0, bottom, w, CAP_TOP, rv, h)
    # Open at the bottom: keep the upper half and the outer lower quarters.
    body = body & (rect(0, center, w, CAP_TOP) | rect(0, bottom, w * 0.30, center)
                   | rect(w * 0.70, bottom, w, center))
    return union(body,
                 rect(w * 0.30 - v, 0, w * 0.30, bottom + h), rect(w * 0.70, 0, w * 0.70 + v, bottom + h),
                 rect(0, 0, w * 0.30, h), rect(w * 0.70, 0, w, h))

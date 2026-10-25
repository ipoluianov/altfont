"""Automatic kerning from outline profiles.

Spacing is designed per side (straight, round, diagonal, ...), which works
for most pairs. Kerning is computed only where that cannot work:

* both facing sides are open (A V, L T, T A), or
* a short glyph stands next to an open side of a taller one (T o, P .,
  quotes A, Г о).

The optical gap of a pair is the mean distance from each side's edge to the
nearest ink of the other glyph, searched within a vertical window, so an
overhang (the bar of T) counts as near. Kerning moves the pair towards the
gap of the straight reference pair (H H, H n, n n) over the same rows.

Profiles are measured on the upright unhinted fonts; italics reuse them.
Accented glyphs are kerned through classes of their base glyph.
"""

import io

import freetype
import numpy as np

from . import style as M
from .build import build_unhinted, metrics_glyph, production_name
from .glyphs import GLYPHS

PPEM = 128                    # profile resolution: 16 font units per row
UNITS = M.UPM / PPEM
DEPTH = 600                   # distances beyond this count as this far
WINDOW = 480                  # vertical search range for the nearest ink
OPEN = 380                    # a side whose edge varies more than this is open (5-95 %)
SHORT = 0.80                  # a glyph this much lower than its partner is short
STRENGTH = 0.45               # share of the optical difference that is kerned
MIN_KERN = 30                 # smaller values are dropped
MAX_TIGHTEN, MAX_LOOSEN = 220, 60

# Partners: glyphs with ordinary spacing classes on the facing side.
PARTNER_SPACING = {"S", "R", "T", "D"}  # tabular glyphs ("F") are never kerned
ROWS = int((M.LINE_ASCENT + M.LINE_DESCENT) / UNITS)
BASE_ROW = int(M.LINE_ASCENT / UNITS)


def _profiles(font):
    """{glyph: (left x per row, right x per row, advance)}, rows top to bottom."""
    buf = io.BytesIO()
    font.save(buf)
    face = freetype.Face(io.BytesIO(buf.getvalue()))
    face.set_pixel_sizes(0, PPEM)
    out = {}
    for gid, name in enumerate(font.getGlyphOrder()):
        face.load_glyph(gid, freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER)
        g = face.glyph
        bm = g.bitmap
        left = np.full(ROWS, np.nan)
        right = np.full(ROWS, np.nan)
        if bm.width and bm.rows:
            data = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)[:, :bm.width]
            for r in range(bm.rows):
                cols = np.nonzero(data[r] > 96)[0]
                idx = BASE_ROW - (g.bitmap_top - r)
                if len(cols) and 0 <= idx < ROWS:
                    left[idx] = (g.bitmap_left + cols[0]) * UNITS
                    right[idx] = (g.bitmap_left + cols[-1] + 1) * UNITS
        out[name] = (left, right, g.linearHoriAdvance / 65536 * UNITS)
    return out


def _shifted(a, k):
    """Rows of a (last axis) shifted by k (positive: down), NaN filled."""
    out = np.full_like(a, np.nan)
    if k > 0:
        out[..., k:] = a[..., :-k]
    elif k < 0:
        out[..., :k] = a[..., -k:]
    else:
        out[...] = a
    return out


OFFSETS = range(-int(WINDOW / UNITS), int(WINDOW / UNITS) + 1)


def _nearest(edge, other_edge, sign):
    """Per row of `edge`: distance to the nearest point of `other_edge` within the window.

    Horizontal distances are sign * (other_edge - edge); arrays broadcast
    over leading axes (one row per right-hand glyph).
    """
    best = np.full(np.broadcast_shapes(edge.shape, other_edge.shape), np.inf)
    for k in OFFSETS:
        dx = sign * (_shifted(other_edge, k) - edge)
        d = np.hypot(np.maximum(dx, 0), k * UNITS)
        best = np.fmin(best, np.where(np.isnan(dx), np.inf, d))
    return np.minimum(best, DEPTH)


def _masked_mean(values, mask):
    n = mask.sum(axis=-1)
    total = np.where(mask, values, 0).sum(axis=-1)
    return np.where(n > 0, total / np.maximum(n, 1), np.nan)


def _gaps(pl, rights, rows):
    """Optical gaps of one left glyph against several right glyphs.

    pl: (left, right, advance) profiles; rights: (left edges (N, R)); rows:
    (N, R) masks of the rows to measure.
    """
    l_right = pl[1][None, :]
    r_left = rights + pl[2]
    a = _masked_mean(_nearest(l_right, r_left, 1), rows & ~np.isnan(l_right))
    b = _masked_mean(_nearest(r_left, l_right, -1), rows & ~np.isnan(r_left))
    both = np.stack([a, b])
    n = (~np.isnan(both)).sum(axis=0)
    return np.where(n > 0, np.nansum(both, axis=0) / np.maximum(n, 1), DEPTH)


def _ink_rows(prof):
    return ~np.isnan(prof[0])


def _height(prof):
    rows = np.nonzero(_ink_rows(prof))[0]
    return (rows[-1] - rows[0]) * UNITS if len(rows) else 0


def _side_open(prof, side):
    edge = prof[0] if side == "L" else prof[1]
    e = edge[~np.isnan(edge)]
    # Percentiles ignore the few extreme rows at the top and bottom of rounds.
    return len(e) > 0 and (np.percentile(e, 95) - np.percentile(e, 5)) > OPEN


def _is_upper(name):
    defn = GLYPHS.get(name)
    return bool(defn and defn.unicodes and chr(defn.unicodes[0]).isupper())


def compute(S):
    """{(left base, right base): kern} for one upright style."""
    font = build_unhinted(S)
    prof = _profiles(font)
    names = [n for n, d in GLYPHS.items()
             if d.base is None and d.spacing[0] in PARTNER_SPACING and d.unicodes]
    p = {n: prof[production_name(n)] for n in names}
    lefts = np.stack([p[n][0] for n in names])
    ink = ~np.isnan(lefts)
    height = np.array([_height(p[n]) for n in names])
    open_l = np.array([_side_open(p[n], "L") for n in names])
    open_r = np.array([_side_open(p[n], "R") for n in names])
    upper = np.array([_is_upper(n) for n in names])
    refs = {True: p["H"], False: p["n"]}

    pairs = {}
    for i, left in enumerate(names):
        right_short = height < SHORT * height[i]
        left_short = height[i] < SHORT * height
        both_open = open_r[i] & open_l
        eligible = both_open | (open_r[i] & right_short) | (open_l & left_short)
        eligible[i] = False
        idx = np.nonzero(eligible)[0]
        if not len(idx):
            continue
        # Rows: both glyphs where both sides are open, else the shorter glyph.
        rows = np.where(both_open[idx, None], ink[i] | ink[idx],
                        np.where(right_short[idx, None], ink[idx], ink[i]))
        actual = _gaps(p[left], lefts[idx], rows)
        # Reference: an open side is replaced by H (capitals) or n, other
        # sides stay as they are, so only the open sides' effect is kerned.
        ref_left = refs[bool(upper[i])] if open_r[i] else p[left]
        ref_rights = np.stack([refs[bool(upper[j])][0] if open_l[j] else lefts[j] for j in idx])
        wanted = _gaps(ref_left, ref_rights, rows)
        values = np.round((wanted - actual) * STRENGTH / 10) * 10
        short = right_short[idx] | left_short[idx]
        for j, value, is_short in zip(idx, values, short):
            if np.isnan(value) or abs(value) < MIN_KERN or (is_short and value > 0):
                continue
            pairs[left, names[j]] = int(max(-MAX_TIGHTEN, min(MAX_LOOSEN, value)))
    return pairs


def feature_text(pairs):
    """A `kern` feature using one class per base glyph and side."""
    members = {}
    for name in GLYPHS:
        members.setdefault(metrics_glyph(name), []).append(production_name(name))
    used = {a for a, _ in pairs} | {b for _, b in pairs}
    lines = []
    for base in sorted(used):
        glyphs = " ".join(sorted(set(members.get(base, [production_name(base)]))))
        cls = production_name(base).replace(".", "_")
        lines.append(f"@L_{cls} = [{glyphs}];")
        lines.append(f"@R_{cls} = [{glyphs}];")
    lines.append("feature kern {")
    for (a, b), v in sorted(pairs.items()):
        ca, cb = production_name(a).replace(".", "_"), production_name(b).replace(".", "_")
        lines.append(f"    pos @L_{ca} @R_{cb} {v};")
    lines.append("} kern;")
    return "\n".join(lines) + "\n"

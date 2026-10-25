"""Pixel fitting of vertical stems.

FreeType's v40 TrueType interpreter (and light hinting in general) ignores
horizontal hints, so the x position of a vertical stem edge on the pixel
grid is fixed by the outline itself. Toolkits that use hinted (rounded)
advances start every glyph on a whole pixel, so an edge at x font units
lands at x * ppem / UPM pixels from a pixel boundary.

For every glyph this module searches small changes of the left side
bearing, the glyph width and the right side bearing that move vertical
edges closer to pixel boundaries at the core UI sizes, while keeping the
rendered side bearings close to their nominal values.
"""

import numpy as np

from . import style as M
from .build import draw_glyph, is_tabular, side_bearings
from .glyphs import GLYPHS

# ppem -> weight. Fitting only matters where glyphs start on whole pixels
# and x hints are ignored: Qt (KDE default 10 pt = 13 px) and GTK3 (GNOME
# default 11 pt = 14.67 px, rendered as 15 ppem because head.flags bit 3 is
# set). Windows GDI applies x hints, and DirectWrite and GTK4 position glyphs
# fractionally, so the Windows default of 12 px (9 pt) gets a low weight.
SIZES = {11: 0.5, 12: 1.0, 13: 4.0, 14: 1.0, 15: 3.0, 16: 2.0, 17: 0.5, 18: 0.5}

LSB_RANGE = range(-80, 81, 2)
WIDTH_RANGE = range(-96, 97, 8)
RSB_RANGE = range(-80, 81, 2)

MIN_EDGE = 60             # shortest straight vertical segment considered
CURVE_EDGE_FACTOR = 0.35  # effective length of a round extremum, per contour height
SPACING_WEIGHT = 5.0      # cost per px^2 of side bearing deviation
WIDTH_WEIGHT = 1.0        # cost per px^2 of width change
ADVANCE_WEIGHT = 5.0      # cost per px^2 of rendered advance deviation


def vertical_edges(g):
    """Return [(x, length)] of vertical stem edges in a simple TrueType glyph.

    Straight edges are vertical segments between two on-curve points. Round
    edges are on-curve x-extrema with a vertical tangent; their length is an
    estimate of the near-vertical part of the curve. Cut round edges are
    curves that turn near-vertical where they meet a horizontal bar (inside
    of e), counted with half that length.
    """
    edges = []
    if not g.numberOfContours:
        return edges
    coords, flags = g.coordinates, g.flags
    start = 0
    for end in g.endPtsOfContours:
        pts = [(coords[i][0], coords[i][1], flags[i] & 1) for i in range(start, end + 1)]
        start = end + 1
        n = len(pts)
        height = max(p[1] for p in pts) - min(p[1] for p in pts)
        for i, (x, y, on) in enumerate(pts):
            if not on:
                continue
            px, py, pon = pts[i - 1]
            nx, ny, non = pts[(i + 1) % n]
            if non and abs(nx - x) <= 1 and abs(ny - y) >= MIN_EDGE:
                edges.append((x, abs(ny - y)))
            elif not pon and not non and abs(px - x) <= 2 and abs(nx - x) <= 2:
                edges.append((x, height * CURVE_EDGE_FACTOR))
            else:
                for (ax, ay, aon), (bx, by, bon) in (((px, py, pon), (nx, ny, non)),
                                                     ((nx, ny, non), (px, py, pon))):
                    if (aon and abs(ay - y) <= 1 and not bon
                            and abs(bx - x) <= 0.15 * abs(by - y)):
                        edges.append((x, height * CURVE_EDGE_FACTOR * 0.5))
                        break
    return edges


def _blur(edges, shifts, scales):
    """Edge blur cost for each (shift, size): sum of length_px * t * (1 - t)."""
    if not edges:
        return np.zeros((len(shifts), len(scales)))
    x = np.array([e[0] for e in edges], dtype=float)
    length = np.array([e[1] for e in edges], dtype=float)
    pos = (x[None, None, :] + shifts[:, None, None]) * scales[None, :, None]
    t = pos - np.floor(pos)
    return (length[None, None, :] * scales[None, :, None] * t * (1 - t)).sum(axis=2)


def fit_glyph(S, name):
    """Return the best (lsb delta, width delta, rsb delta) and its cost gain."""
    if is_tabular(name):
        return fit_tabular(S, name)
    lsb, rsb = side_bearings(S, name)
    sizes = np.array(list(SIZES), dtype=float)
    weights = np.array(list(SIZES.values()))
    scales = sizes / M.UPM
    dls = np.array(LSB_RANGE, dtype=float)
    drs = np.array(RSB_RANGE, dtype=float)

    _, draw_width = draw_glyph(S, name)
    best, baseline = None, None
    # Glyphs without a width parameter (i) can only move.
    for dw in (WIDTH_RANGE if name in S.widths else [0]):
        g, width = draw_glyph(S, name, dw)
        blur = _blur(vertical_edges(g), lsb + dls, scales)           # (L, K)
        lsb_cost = SPACING_WEIGHT * (dls[:, None] * scales) ** 2      # (L, K)
        # Rendered right side bearing: rounded advance minus ink extent.
        ink = (lsb + dls[:, None, None] + width) * scales             # (L, 1, K)
        adv = (lsb + dls[:, None, None] + width + rsb + drs[None, :, None]) * scales
        rsb_px = np.floor(adv + 0.5) - ink                           # (L, R, K)
        rsb_cost = SPACING_WEIGHT * (rsb_px - rsb * scales) ** 2
        # Keep the rendered advance near the unfitted one, so that fitting
        # does not systematically tighten or loosen the text.
        nominal_adv = (lsb + draw_width + rsb) * scales
        rsb_cost += ADVANCE_WEIGHT * (np.floor(adv + 0.5) - nominal_adv) ** 2
        width_cost = WIDTH_WEIGHT * (dw * scales) ** 2                # (K,)
        total = (blur + lsb_cost + width_cost)[:, None, :] + rsb_cost
        total = (total * weights).sum(axis=2) / weights.sum()         # (L, R)
        i, j = np.unravel_index(np.argmin(total), total.shape)
        if best is None or total[i, j] < best[0]:
            best = (total[i, j], int(dls[i]), dw, int(drs[j]))
        if dw == 0:
            baseline = total[list(dls).index(0), list(drs).index(0)]
    return best[1:], baseline - best[0]


def fit_tabular(S, name):
    """Tabular glyphs keep their advance and width; only the ink can move."""
    g, width = draw_glyph(S, name)
    lsb, _ = side_bearings(S, name, width)
    sizes = np.array(list(SIZES), dtype=float)
    weights = np.array(list(SIZES.values()))
    scales = sizes / M.UPM
    dls = np.array(LSB_RANGE, dtype=float)
    # Moving the ink off-center is penalized like a side bearing change.
    cost = _blur(vertical_edges(g), lsb + dls, scales) + SPACING_WEIGHT * (dls[:, None] * scales) ** 2
    cost = (cost * weights).sum(axis=1) / weights.sum()
    i = int(np.argmin(cost))
    return (int(dls[i]), 0, -int(dls[i])), cost[list(dls).index(0)] - cost[i]


def fit_style(S):
    # Accented glyphs reuse the fit of their base glyph; combining marks have
    # no advance to fit.
    return {name: fit_glyph(S, name) for name, d in GLYPHS.items()
            if d.base is None and d.spacing != ("Z", "Z")}

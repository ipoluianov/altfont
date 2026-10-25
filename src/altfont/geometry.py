"""Shape primitives built on skia-pathops.

Glyphs are composed from simple filled shapes (rectangles, polygons,
superellipses) combined with boolean operations, then converted to
overlap-free quadratic TrueType outlines.
"""

import pathops
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

# Bezier handle length relative to the radius. 0.5523 draws a circle;
# larger values give squarer curves with longer straight-ish sides, which
# rasterize more crisply at small sizes.
DEFAULT_SQUARENESS = 0.60


class Shape:
    """A filled region. Supports | (union), - (difference), & (intersection)."""

    def __init__(self, path=None):
        self.path = path if path is not None else pathops.Path()

    def _op(self, other, op):
        return Shape(pathops.op(self.path, other.path, op))

    def __or__(self, other):
        return union(self, other)

    def __sub__(self, other):
        return self._op(other, pathops.PathOp.DIFFERENCE)

    def __and__(self, other):
        return self._op(other, pathops.PathOp.INTERSECTION)

    def draw(self, pen):
        self.path.draw(pen)

    def transform(self, a=1, b=0, c=0, d=1, e=0, f=0):
        """Affine transform (x, y) -> (a*x + c*y + e, b*x + d*y + f)."""
        return Shape(self.path.transform(a, b, c, d, e, f))

    def translate(self, dx, dy=0):
        return self.transform(e=dx, f=dy)

    def rotate180(self, cx, cy):
        """Point reflection around (cx, cy); used to make 9 from 6."""
        return self.transform(-1, 0, 0, -1, 2 * cx, 2 * cy)

    def mirror_x(self, axis):
        """Mirror horizontally around x = axis."""
        return self.transform(-1, 0, 0, 1, 2 * axis, 0)


def union(*shapes):
    """Union of shapes.

    pathops' binary UNION fails on some coincident edges (e.g. a stem edge
    lying on the tangent of a curve end). Normalizing every operand to one
    orientation, concatenating and simplifying with the non-zero rule is
    robust against that.
    """
    paths = [pathops.simplify(s.path, clockwise=True) for s in shapes]
    combined = pathops.Path()
    pen = combined.getPen()
    for p in paths:
        p.draw(pen)
    try:
        return Shape(pathops.simplify(combined, clockwise=True))
    except pathops.PathOpsError:
        pass
    # Rare numerical failures: fall back to an OpBuilder, then to pairwise ops.
    try:
        builder = pathops.OpBuilder(fix_winding=True)
        for p in paths:
            builder.add(p, pathops.PathOp.UNION)
        return Shape(builder.resolve())
    except pathops.PathOpsError:
        result = paths[0]
        for p in paths[1:]:
            result = pathops.op(result, p, pathops.PathOp.UNION)
        return Shape(result)


def rect(x0, y0, x1, y1):
    p = pathops.Path()
    p.moveTo(x0, y0)
    p.lineTo(x0, y1)
    p.lineTo(x1, y1)
    p.lineTo(x1, y0)
    p.close()
    return Shape(p)


def polygon(points):
    p = pathops.Path()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    return Shape(p)


def slanted(xb, yb, xt, yt, thickness):
    """Straight stroke along the centre line (xb, yb)-(xt, yt), yb < yt.

    The ends are cut horizontally, so the stroke sits flat on alignment
    lines. `thickness` is measured perpendicular to the stroke.
    """
    dx, dy = xt - xb, yt - yb
    hw = thickness * (dx * dx + dy * dy) ** 0.5 / dy / 2
    return polygon([(xb - hw, yb), (xt - hw, yt), (xt + hw, yt), (xb + hw, yb)])


def slant_half_width(dx, dy, thickness):
    """Half of the horizontal width of a stroke with slope dx/dy."""
    return thickness * (dx * dx + dy * dy) ** 0.5 / abs(dy) / 2


def ellipse(x0, y0, x1, y1, k=DEFAULT_SQUARENESS):
    """Superellipse-like oval inscribed in the box (x0, y0)-(x1, y1)."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    hx, hy = rx * k, ry * k
    p = pathops.Path()
    p.moveTo(cx, y0)
    p.cubicTo(cx - hx, y0, x0, cy - hy, x0, cy)
    p.cubicTo(x0, cy + hy, cx - hx, y1, cx, y1)
    p.cubicTo(cx + hx, y1, x1, cy + hy, x1, cy)
    p.cubicTo(x1, cy - hy, cx + hx, y0, cx, y0)
    p.close()
    return Shape(p)


def ring(x0, y0, x1, y1, vstem, hstem, k=DEFAULT_SQUARENESS, k_inner=None):
    """Oval stroke: vertical sides `vstem` thick, top/bottom `hstem` thick."""
    if k_inner is None:
        k_inner = k
    outer = ellipse(x0, y0, x1, y1, k)
    inner = ellipse(x0 + vstem, y0 + hstem, x1 - vstem, y1 - hstem, k_inner)
    return outer - inner


def to_ttglyph(shape, max_err=1.0):
    """Convert a shape to an overlap-free quadratic TrueType glyph."""
    # TrueType expects clockwise outer contours (y-up).
    path = pathops.simplify(shape.path, fix_winding=True, clockwise=True)
    tt_pen = TTGlyphPen(None)
    path.draw(Cu2QuPen(tt_pen, max_err, all_quadratic=True))
    return tt_pen.glyph()

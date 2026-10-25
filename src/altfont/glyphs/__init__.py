"""Parametric glyph definitions.

Each glyph function takes a Style and returns a Shape drawn with its left
extreme at x = 0. Side bearings are added by the builder from the spacing
classes given in the registry (see `common.glyph`).
"""

from . import latin, cyrillic, greek, symbols, signs, mathsym, shapes, composites  # noqa: F401  (registration order = glyph order)
from .common import GLYPHS, SPACE_WIDTH  # noqa: F401

composites.register_marks()
composites.generate()

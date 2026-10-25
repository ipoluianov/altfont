"""Letters with diacritics, generated from Unicode canonical decompositions.

Every code point in RANGES whose NFD form is a base letter present in the
font followed by supported marks becomes an accented glyph. Spacing and
combining forms of the marks are registered here as well.
"""

import unicodedata

from fontTools.agl import UV2AGL

from ..style import CAP_HEIGHT, X_HEIGHT
from .common import GLYPHS, accented, glyph
from .marks import (ABOVE, APOSTROPHE_EXTRA, BELOW, HORN, HORN_EXTRA, caron_apostrophe,
                    mark_acute, mark_level, place_marks, turned_comma_above)

RANGES = [
    range(0x00C0, 0x0250),   # Latin-1 letters, Latin Extended-A and -B
    range(0x1E00, 0x1F00),   # Latin Extended Additional (Vietnamese)
    range(0x0400, 0x0530),   # Cyrillic and Cyrillic Supplement
    range(0x0370, 0x0400),   # Greek
]

ACUTE = 0x0301
GREEK_CAPITALS = range(0x0391, 0x03AA)
TONOS_GAP = 90  # between the tonos and a Greek capital, which carries it at its left

CARON = 0x030C
CEDILLA = 0x0327
COMMA_BELOW = 0x0326

# Above marks replace the dot of i and j.
DOTLESS = {"i": "dotlessi", "j": "dotlessj"}
# ď ľ ť Ľ: the caron becomes an apostrophe right of the ascender.
APOSTROPHE_CARON = {"d", "l", "t", "L"}
# Latvian ķ ļ ņ ŗ Ķ Ļ Ņ Ŗ Ģ decompose with a cedilla but use a comma below.
COMMA_CEDILLA = {"k", "l", "n", "r", "K", "L", "N", "R", "G"}


def glyph_name(cp):
    if cp < 0x0250 or 0x0370 <= cp < 0x0400 or 0x1E00 <= cp < 0x1F00:
        name = UV2AGL.get(cp)
        if name:
            return name
    return f"uni{cp:04X}"


def _tonos(S):
    tonos = mark_acute(S, 0, CAP_HEIGHT - 260, cap=True)
    return tonos.translate(-tonos.path.bounds[0])


def tonos_space(S):
    return round(_tonos(S).path.bounds[2]) + TONOS_GAP


def _greek_tonos(S, shape):
    """Tonos of a Greek capital, left of the letter, which moves right."""
    return shape.translate(tonos_space(S)) | _tonos(S)


def _decorator(base, marks, greek_capital=False):
    def decorate(S, shape):
        if greek_capital and ACUTE in marks:
            return _greek_tonos(S, place_marks(S, shape, base, [m for m in marks if m != ACUTE]))
        if base in APOSTROPHE_CARON and CARON in marks:
            rest = [m for m in marks if m != CARON]
            return place_marks(S, shape, base, rest) | caron_apostrophe(S, shape.path.bounds)
        if base == "g" and CEDILLA in marks:
            return shape | turned_comma_above(S, shape.path.bounds)
        fixed = [COMMA_BELOW if (m == CEDILLA and base in COMMA_CEDILLA) else m for m in marks]
        return place_marks(S, shape, base, fixed)
    return decorate


def generate():
    by_code = {u: name for name, d in GLYPHS.items() for u in d.unicodes}
    for r in RANGES:
        for cp in r:
            if cp in by_code:
                continue
            nfd = unicodedata.normalize("NFD", chr(cp))
            if len(nfd) < 2:
                continue
            base = by_code.get(ord(nfd[0]))
            marks = [ord(c) for c in nfd[1:]]
            if base is None or not all(m in ABOVE or m in BELOW or m == HORN for m in marks):
                continue
            if any(m in ABOVE for m in marks):
                base = DOTLESS.get(base, base)
            extra = 0
            if HORN in marks:
                extra = HORN_EXTRA
            if base in APOSTROPHE_CARON and CARON in marks:
                extra = APOSTROPHE_EXTRA
            greek_capital = ord(nfd[0]) in GREEK_CAPITALS
            if greek_capital and ACUTE in marks:
                extra = tonos_space
            name = glyph_name(cp)
            accented(name, [cp], base, _decorator(base, marks, greek_capital), extra)
            by_code[cp] = name


# --- Spacing and combining marks ---------------------------------------------------

SPACING = {
    0x00A8: 0x0308, 0x00AF: 0x0304, 0x00B4: 0x0301, 0x02C6: 0x0302,
    0x02C7: 0x030C, 0x02C9: 0x0304, 0x02D8: 0x0306, 0x02D9: 0x0307,
    0x02DA: 0x030A, 0x02DC: 0x0303, 0x02DD: 0x030B,
    0x0384: 0x0301,  # Greek tonos
}
SPACING_BELOW = {0x00B8: 0x0327, 0x02DB: 0x0328}


def _mark_alone(m):
    def fn(S):
        if m in ABOVE:
            y, cap = mark_level(S, X_HEIGHT)
            return ABOVE[m](S, 0, y, cap)
        return BELOW[m](S, (-250, 0, 250, X_HEIGHT), None)
    return fn


def register_marks():
    for cp, m in {**SPACING, **SPACING_BELOW}.items():
        glyph(glyph_name(cp), [cp], ("T", "T"))(_mark_alone(m))
    # Zero-width combining marks, drawn over the preceding letter.
    for m in list(ABOVE) + list(BELOW):
        glyph(f"uni{m:04X}", [m], ("Z", "Z"))(_mark_alone(m))

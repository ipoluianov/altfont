#!/usr/bin/env python3
"""Check the built fonts: declared coverage, empty glyphs, metrics, style consistency.

Exits with status 1 if any check fails. Run after scripts/build.py.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / ".pydeps")]

from fontTools.ttLib import TTFont  # noqa: E402

FONTS = ["Regular", "Bold", "Italic", "BoldItalic"]


def chars(*ranges):
    out = set()
    for r in ranges:
        if isinstance(r, str):
            out |= set(map(ord, r))
        else:
            out |= set(range(r[0], r[1] + 1))
    return out


# Coverage declared in docs/spec.md, section 5.
REQUIRED = {
    "ASCII": chars((0x20, 0x7E)),
    "Latin-1": chars((0xA0, 0xAC), (0xAE, 0xFF)),
    "Latin Extended-A": chars((0x100, 0x17F)),
    "Romanian, Azerbaijani, others (Ext-B)": chars("ȘșȚțƏəƒȷ"),
    "Vietnamese": chars("ăâđêôơưĂÂĐÊÔƠƯ"
                        "ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ"
                        "ẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸ"),
    "Cyrillic": chars((0x400, 0x45F), "ҐґҒғҖҗҘҙҚқҠҡҢңҪҫҮүҰұҲҳҶҷҺһӘәӢӣӨөӮӯ"),
    "Greek": chars((0x391, 0x3A1), (0x3A3, 0x3A9), (0x3B1, 0x3C9),
                   "ΆΈΉΊΌΎΏΪΫάέήίόύώϊϋΐΰ΄΅·;"),
    "Punctuation": chars("‐‑‒–—‘’‚“”„†‡•…‰′″‹›‼⁄"),
    "Super- and subscripts, fractions": chars("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉¼½¾⅓⅔⅛⅜⅝⅞"),
    "Currency": chars("¢£¤¥€₽₴₸₺₩₫₹₮"),
    "Letterlike": chars("№™Ω"),
    "Arrows": chars("←↑→↓↔↕↖↗↘↙⇐⇒⇔↵"),
    "Math": chars("−×÷±≤≥≠≈≡∞√∫∂∑∏∆∈∉∩∪⊂⊃∅∧∨¬⋅∙∕∗∼"),
    "Geometric shapes": chars("■□▪▫▲△▶▷▼▽◀◁●○◦◆◇◊★☆"),
    "UI symbols": chars("✓✔✕✖✗✘☐☑☒⋮⋯"),
}

# Mapped characters that legitimately have no outline.
BLANK = chars((0x20, 0x20), (0xA0, 0xA0))


def check():
    problems = []
    fonts = {name: TTFont(ROOT / "build" / "fonts" / f"altfont-{name}.ttf") for name in FONTS}
    cmaps = {name: f.getBestCmap() for name, f in fonts.items()}

    base = cmaps["Regular"]
    for name, cmap in cmaps.items():
        if set(cmap) != set(base):
            problems.append(f"{name}: character set differs from Regular "
                            f"({len(set(cmap) ^ set(base))} code points)")

    for group, required in REQUIRED.items():
        missing = sorted(required - set(base))
        if missing:
            problems.append(f"missing {group}: " + "".join(chr(c) for c in missing))

    for name, f in fonts.items():
        glyf = f["glyf"]
        os2, hhea = f["OS/2"], f["hhea"]
        empty = [chr(c) for c, g in cmaps[name].items()
                 if c not in BLANK and not glyf[g].numberOfContours]
        if empty:
            problems.append(f"{name}: empty glyphs for " + "".join(empty))
        y_max = max(glyf[g].yMax for g in f.getGlyphOrder() if glyf[g].numberOfContours)
        y_min = min(glyf[g].yMin for g in f.getGlyphOrder() if glyf[g].numberOfContours)
        if os2.usWinAscent < y_max or os2.usWinDescent < -y_min:
            problems.append(f"{name}: glyphs exceed usWin metrics ({y_min}..{y_max})")
        if (os2.sTypoAscender, os2.sTypoDescender) != (hhea.ascent, hhea.descent):
            problems.append(f"{name}: typo and hhea line metrics differ")
        if not os2.fsSelection & (1 << 7):
            problems.append(f"{name}: USE_TYPO_METRICS not set")
        if not f["head"].flags & (1 << 3):
            problems.append(f"{name}: integer ppem flag not set")
        if "GPOS" not in f:
            problems.append(f"{name}: no kerning")

    for p in problems:
        print("FAIL", p)
    print(f"{len(base)} code points, {len(fonts['Regular'].getGlyphOrder())} glyphs, "
          f"{len(problems)} problems")
    return not problems


if __name__ == "__main__":
    sys.exit(0 if check() else 1)

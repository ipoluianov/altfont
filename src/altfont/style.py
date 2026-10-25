"""Font-wide metrics and per-style design parameters."""

from dataclasses import dataclass, field, replace

UPM = 2048

# Vertical metrics shared by all styles (font units, baseline = 0).
# Chosen so they round unambiguously at the priority sizes 13 and 15 ppem
# after ttfautohint has scaled everything to the rounded x-height:
# x-height 7 / 8 px, cap height 9 / 11 px, ascender 10 / 12 px.
X_HEIGHT = 1100
CAP_HEIGHT = 1500
ASCENDER = 1640       # b d h k l
DESCENDER = -420      # g p q y
OVERSHOOT = 24        # round shapes extend this far past flat alignment zones

# Line metrics: about 1.21 em, room for accented capitals.
LINE_ASCENT = 1950
LINE_DESCENT = 520


@dataclass(frozen=True)
class Style:
    name: str             # "Regular", "Bold", ...
    weight: int           # OS/2 usWeightClass
    vstem: int            # vertical stem thickness
    hstem: int            # horizontal stroke thickness
    hstem_tight: int      # horizontal strokes of glyphs with three of them (a e s)
    sb_straight: int      # side bearing next to a straight vertical stem
    sb_round: int         # side bearing next to a round side
    sb_terminal: int      # side bearing next to an open terminal (r, f, t)
    sb_diagonal: int      # side bearing next to a diagonal (v, w, x, y)
    figure_advance: int   # advance of tabular glyphs (digits)
    widths: dict = field(default_factory=dict)  # outer glyph widths
    slant: float = 0          # oblique angle in degrees (italic styles)

    @property
    def is_bold(self):
        return self.weight >= 700

    @property
    def is_italic(self):
        return self.slant != 0

    @property
    def upright(self):
        """Name of the upright style whose design and fit this style shares."""
        return "Bold" if self.is_bold else "Regular"

    @property
    def file_name(self):
        return self.name.replace(" ", "")

    @property
    def tight(self):
        """This style with thinner horizontals, for a e s."""
        return replace(self, hstem=self.hstem_tight)

    @property
    def round_vstem(self):
        # Curves look thinner than straight stems of equal width.
        return round(self.vstem * 1.06)


REGULAR = Style(
    name="Regular", weight=400,
    vstem=160, hstem=150,     # 1.0 px at 13 ppem
    hstem_tight=150,
    sb_straight=160, sb_round=120, sb_terminal=80, sb_diagonal=70,
    figure_advance=1180,
    widths={
        "n": 1000, "h": 1000, "m": 1600, "u": 1000, "r": 640,
        "o": 1060, "b": 1060, "d": 1060, "p": 1060, "q": 1060,
        "c": 960, "e": 1020, "a": 940, "g": 1000, "s": 880,
        "j": 380, "l": 380, "t": 640, "f": 640, "k": 980,
        "v": 1000, "y": 1000, "w": 1500, "x": 980, "z": 900,
        "be-cy": 1040, "ve-cy": 940, "ge-cy": 760, "de-cy": 1160, "zhe-cy": 1560,
        "ze-cy": 880, "i-cy": 1020, "ka-cy": 940, "el-cy": 1060, "em-cy": 1260,
        "en-cy": 1000, "pe-cy": 1000, "te-cy": 980, "ef-cy": 1420, "tse-cy": 1100,
        "che-cy": 960, "sha-cy": 1520, "shcha-cy": 1620, "hardsign-cy": 1160,
        "yeru-cy": 1340, "softsign-cy": 900, "e-cy": 960, "yu-cy": 1440,
        "ya-cy": 960, "ie-ukr": 960, "dzhe-cy": 1000, "lje-cy": 1560,
        "nje-cy": 1520, "tshe-cy": 1060,
        "germandbls": 1080, "ae": 1640, "oe": 1720, "AE": 1820, "OE": 1960,
        "A": 1300, "B": 1140, "C": 1300, "D": 1340, "E": 1000, "F": 960,
        "G": 1380, "H": 1200, "J": 760, "K": 1180, "L": 920, "M": 1540,
        "N": 1280, "O": 1420, "P": 1120, "Q": 1420, "R": 1160, "S": 1140,
        "T": 1140, "U": 1260, "V": 1280, "W": 1860, "X": 1240, "Y": 1220,
        "Z": 1140,
        "gheupturn-cy": 760,
        "Be-cy": 1120, "Ge-cy": 940, "Gheupturn-cy": 940, "De-cy": 1400,
        "Zhe-cy": 1900, "Ze-cy": 1120, "I-cy": 1300, "El-cy": 1300,
        "Pe-cy": 1260, "U-cy": 1240, "Ef-cy": 1560, "Tse-cy": 1420,
        "Che-cy": 1180, "Sha-cy": 1800, "Shcha-cy": 1920, "Hardsign-cy": 1400,
        "Yeru-cy": 1600, "Softsign-cy": 1120, "E-cy": 1300, "Yu-cy": 1860,
        "Ya-cy": 1180, "Ie-ukr": 1300, "Dzhe-cy": 1260, "Lje-cy": 1900,
        "Nje-cy": 1860, "Tshe-cy": 1360,
    },
)

BOLD = Style(
    name="Bold", weight=700,
    vstem=315, hstem=250,     # 2.0 px at 13 ppem; hstem 1 px at 11-12, 2 px from 13
    hstem_tight=220,          # 1 px up to 13 ppem, so counters stay open
    sb_straight=140, sb_round=100, sb_terminal=70, sb_diagonal=60,
    figure_advance=1300,
    widths={
        "n": 1180, "h": 1180, "m": 1860, "u": 1180, "r": 760,
        "o": 1220, "b": 1220, "d": 1220, "p": 1220, "q": 1220,
        "c": 1100, "e": 1170, "a": 1100, "g": 1180, "s": 1020,
        "j": 460, "l": 470, "t": 740, "f": 740, "k": 1140,
        "v": 1140, "y": 1140, "w": 1720, "x": 1120, "z": 1020,
        "be-cy": 1200, "ve-cy": 1100, "ge-cy": 880, "de-cy": 1320, "zhe-cy": 1800,
        "ze-cy": 1020, "i-cy": 1200, "ka-cy": 1100, "el-cy": 1220, "em-cy": 1460,
        "en-cy": 1180, "pe-cy": 1180, "te-cy": 1140, "ef-cy": 1640, "tse-cy": 1300,
        "che-cy": 1120, "sha-cy": 1820, "shcha-cy": 1940, "hardsign-cy": 1340,
        "yeru-cy": 1600, "softsign-cy": 1060, "e-cy": 1100, "yu-cy": 1660,
        "ya-cy": 1120, "ie-ukr": 1100, "dzhe-cy": 1180, "lje-cy": 1820,
        "nje-cy": 1780, "tshe-cy": 1240,
        "germandbls": 1240, "ae": 1860, "oe": 1940, "AE": 2060, "OE": 2200,
        "A": 1460, "B": 1300, "C": 1440, "D": 1500, "E": 1140, "F": 1100,
        "G": 1520, "H": 1380, "J": 880, "K": 1360, "L": 1060, "M": 1780,
        "N": 1460, "O": 1580, "P": 1280, "Q": 1580, "R": 1340, "S": 1300,
        "T": 1280, "U": 1420, "V": 1440, "W": 2100, "X": 1420, "Y": 1400,
        "Z": 1300,
        "gheupturn-cy": 880,
        "Be-cy": 1280, "Ge-cy": 1080, "Gheupturn-cy": 1080, "De-cy": 1580,
        "Zhe-cy": 2180, "Ze-cy": 1280, "I-cy": 1480, "El-cy": 1480,
        "Pe-cy": 1440, "U-cy": 1420, "Ef-cy": 1780, "Tse-cy": 1620,
        "Che-cy": 1360, "Sha-cy": 2080, "Shcha-cy": 2220, "Hardsign-cy": 1600,
        "Yeru-cy": 1860, "Softsign-cy": 1300, "E-cy": 1460, "Yu-cy": 2080,
        "Ya-cy": 1360, "Ie-ukr": 1460, "Dzhe-cy": 1440, "Lje-cy": 2180,
        "Nje-cy": 2120, "Tshe-cy": 1560,
    },
)

# Obliques: the upright design sheared around the middle of the x-height, so
# spacing and pixel fit stay those of the upright styles. A small angle keeps
# the stair-stepping of slanted stems low at small sizes.
ITALIC_ANGLE = 9
ITALIC = replace(REGULAR, name="Italic", slant=ITALIC_ANGLE)
BOLD_ITALIC = replace(BOLD, name="Bold Italic", slant=ITALIC_ANGLE)

STYLES = [REGULAR, BOLD, ITALIC, BOLD_ITALIC]
UPRIGHT_STYLES = [REGULAR, BOLD]

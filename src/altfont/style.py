"""Font-wide metrics and per-style design parameters."""

from dataclasses import dataclass, field

UPM = 2048

# Vertical metrics shared by all styles (font units, baseline = 0).
X_HEIGHT = 1100
CAP_HEIGHT = 1434
ASCENDER = 1500       # b d h k l
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
    sb_straight: int      # side bearing next to a straight vertical stem
    sb_round: int         # side bearing next to a round side
    widths: dict = field(default_factory=dict)  # outer glyph widths

    @property
    def is_bold(self):
        return self.weight >= 700

    @property
    def round_vstem(self):
        # Curves look thinner than straight stems of equal width.
        return round(self.vstem * 1.06)


REGULAR = Style(
    name="Regular", weight=400,
    vstem=180, hstem=160,
    sb_straight=160, sb_round=120,
    widths={
        "n": 1000, "o": 1060, "H": 1200, "O": 1420, "a": 940, "e": 1020,
        "g": 1000, "en-cy": 1000, "i-cy": 1020, "de-cy": 1160, "Be-cy": 1060,
    },
)

BOLD = Style(
    name="Bold", weight=700,
    vstem=300, hstem=250,
    sb_straight=140, sb_round=100,
    widths={
        "n": 1180, "o": 1220, "H": 1380, "O": 1580, "a": 1100, "e": 1170,
        "g": 1180, "en-cy": 1180, "i-cy": 1200, "de-cy": 1320, "Be-cy": 1220,
    },
)

STYLES = [REGULAR, BOLD]

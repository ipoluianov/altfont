# altfont — Technical Specification

Status: v0.1, all four styles built (2026-10-25)

## 1. Purpose

altfont is a general-purpose **user-interface font** for desktop applications:
menus, dialogs, lists, tables, toolbars, status bars, form controls, tooltips.
It is not a display or typesetting font. Success is measured by legibility and
crispness at small sizes on ordinary screens, not by appearance in headlines.

## 2. Key requirement: crisp rendering without device-specific tricks

The font must look sharp and evenly weighted when rasterized by a stock
FreeType build **without** subpixel (LCD/ClearType) rendering, and without
relying on any other device- or vendor-specific feature.

Rendering modes that must look good (priority order):

1. FreeType grayscale AA, `hintslight` (v40 interpreter / autohinter light) —
   the most common Linux desktop default. Hints act only vertically here, so
   horizontal crispness must come from the outlines themselves.
2. FreeType grayscale AA, `hintfull` (TrueType bytecode, v40).
3. FreeType monochrome (`FT_RENDER_MODE_MONO`, hinting on) — no AA at all.
4. Windows GDI / DirectWrite in grayscale mode.
5. Unhinted rendering (e.g. macOS, browsers with hinting disabled) — best
   effort, must stay readable but is not tuned for.

Subpixel rendering must not make things worse, but is never tuned for.

## 3. Size range

Sizes are given in pixels per em (ppem) at 96 dpi; 1 pt = 1.333 px.

| Range            | ppem    | pt @ 96 dpi | Priority                         |
|------------------|---------|-------------|----------------------------------|
| Minimum UI       | 11–12   | 8–9         | Must be fully legible            |
| Core UI          | 13–18   | 10–13.5     | Primary tuning target            |
| Large UI / HiDPI | 19–32   | 14–24       | Must look correct, less tuning   |
| Display          | > 32    | > 24        | Not a priority; no artefacts     |

HiDPI scaling (125 %, 150 %, 200 %) maps core UI sizes to roughly 16–36 ppem;
these must be covered by the ranges above.

## 4. Styles

- Regular (400)
- Bold (700)
- Italic (400)
- Bold Italic (700) — needed for correct RIBBI style linking in most toolkits.

Delivered as separate static TrueType fonts forming one family. No variable
font in v1 (hinting a variable font is much harder and gives worse results at
small sizes).

Italic: an oblique, the upright design sheared by 9° around the middle of the
x-height. Spacing, kerning and pixel fit are those of the upright styles. A
true italic (single-storey a, Cyrillic cursive forms) may come later; at UI
sizes the difference is barely visible, while a small angle keeps slanted
stems from stair-stepping.

Bold must stay distinguishable from Regular at 11–12 ppem, i.e. stems must
differ by at least one full pixel at those sizes.

## 5. Character coverage

v1 covers the European scripts and the symbols common in UI text:

- Latin: Basic Latin, Latin-1 Supplement, Latin Extended-A, plus the
  Latin Extended-B and Latin Extended Additional characters needed for
  Romanian, Vietnamese and pan-European use.
- Cyrillic: the Cyrillic block (U+0400–U+04FF) and the Cyrillic Supplement
  characters needed for modern languages (Russian, Ukrainian, Belarusian,
  Serbian, Macedonian, Bulgarian, Kazakh, Uzbek, Tatar, Bashkir, etc.).
- Greek: modern monotonic Greek.
- General Punctuation, currency signs, letterlike symbols, number forms
  (fractions), superscripts and subscripts.
- Arrows, common mathematical operators, geometric shapes and other UI
  symbols (check marks, ballot boxes, triangles, ellipsis, etc.).

Out of scope for v1: CJK, RTL scripts, Indic and other complex scripts,
emoji, box drawing for terminals. Missing characters are expected to come
from system font fallback.

## 6. Design principles

- Large x-height, open apertures, low stroke contrast, no hairlines.
- Unambiguous confusables: `I l 1 |`, `O 0`, `rn m`, `Б б 6`, `З 3`.
- Simple, grid-friendly shapes: straight stems, few diagonals and fine
  details; terminals cut horizontally or vertically where possible.
- Stem widths and key vertical metrics (baseline, x-height, cap height,
  ascender, descender) chosen so they snap cleanly at core UI sizes.
- Diacritics designed to stay separate from the base letter at 11–12 ppem,
  including stacked Vietnamese marks. Marks over capitals and ascenders are
  flatter. Vietnamese acute, grave and hook sit beside the circumflex;
  ď ľ ť Ľ use an apostrophe caron; Latvian ķ ļ ņ ŗ ģ use a comma; Greek
  capitals carry the tonos at their left.
- Slightly loose default spacing, suitable for UI text at small sizes.
- Tabular (fixed-width) figures by default, so numbers in tables, counters
  and progress indicators do not jitter. Proportional figures may be added
  later as `pnum`.
- Digits are told apart from letters: 0 is narrower and squarer than O,
  1 has a flag and a base bar (l has a tail, I is a plain stem), 3 has a
  flat top unlike З.

## 7. Metrics

- TrueType outlines (`glyf`, quadratic curves).
- UPM: 2048.
- Key values (font units → px at 13 / 15 ppem after hinting), chosen to
  round unambiguously at the priority sizes. ttfautohint first rounds the
  x-height and scales all other heights by the same factor, so values are
  verified on hinted renders, not just computed:

  | Metric                  | Units | 13 ppem | 15 ppem |
  |-------------------------|-------|---------|---------|
  | x-height                | 1100  | 7       | 8       |
  | Cap height              | 1500  | 9       | 11      |
  | Ascender                | 1640  | 10      | 12      |
  | Descender               | −420  | 3       | 3       |
  | Regular vertical stem   | 160   | 1.0     | 1.2     |
  | Regular horizontal stem | 150   | 1       | 1       |
  | Bold vertical stem      | 315   | 2.0     | 2.3     |
  | Bold horizontal stem    | 250   | 2       | 2       |
  | Bold horizontals of a e s | 220 | 1       | 2       |

  Horizontal stems and heights are snapped by hinting; vertical stems are
  not (see 8), hence stem widths are chosen to be whole pixels at 13 ppem.
  Bold horizontals are 1 px at 11–12 ppem (Bold is carried by its 2 px
  vertical stems there, as in DejaVu Sans Bold); glyphs with three
  horizontals in the x-height use thinner ones so their counters stay open.
- Vertical metrics consistent across all styles; `OS/2` typo metrics with
  `USE_TYPO_METRICS` set and equal to `hhea` (line spacing 1950 + 520, about
  1.2 em). `usWin*` metrics cover the tallest glyph of the family (stacked
  Vietnamese capitals), so nothing is clipped on Windows; they do not affect
  line spacing.
- Symbols in tables: figures and the common math operators (+ − = < > ± × ÷
  ≤ ≥ ≠ ≈ ≡ ¬ ~ ∈ ∉ ⊂ ⊃) share one advance.
- Line height suitable for UI (roughly 1.2–1.25 em).

## 8. Hinting

- TrueType hinting, initially via `ttfautohint` with per-size control
  instructions where needed; manual hinting only if autohinting proves
  insufficient.
- Outlines must render well even when hints are ignored horizontally
  (FreeType v40) or entirely (unhinted renderers).
- Pixel fitting: since x hints are ignored in grayscale FreeType, side
  bearings and glyph widths are adjusted per glyph (`scripts/fit.py`) so
  vertical stem edges land near pixel boundaries at the default UI sizes
  where glyphs start on whole pixels: 13 ppem (Qt/KDE, 10 pt) and 15 ppem
  (GTK3/GNOME, 11 pt). A single outline cannot be aligned at every size;
  fitting is a trade-off weighted towards these sizes.
- `head.flags` bit 3 (integer ppem) is set, so fractional pixel sizes such as
  13.33 px render as the integer ppem the outlines are fitted for.

## 9. Sources and toolchain

- Glyphs are defined parametrically in Python (`src/altfont/glyphs/`):
  each glyph is built from simple shapes (stems, bars, superellipse bowls)
  using per-style parameters (stem widths, glyph widths, side bearings), so
  Regular and Bold share one design. Shapes are merged with `skia-pathops`
  and converted to quadratic outlines with `fontTools`.
- Fonts are assembled with `fontTools.fontBuilder` and hinted with
  `ttfautohint`. UFO export may be added later if manual editing in a font
  editor becomes necessary.
- All build and test steps scripted and reproducible from the repository.
- Letters with diacritics are generated from Unicode canonical decompositions
  (base glyph + marks), so every precomposed letter whose base and marks are
  in the font is covered. Zero-width combining marks are included for
  decomposed text.
- Kerning is computed automatically (`scripts/kern.py`) from outline
  profiles, only for pairs whose facing sides are both open (A V, L T) or
  where a short glyph meets an open side (T o, P ., “ A). Accented glyphs
  are kerned through classes of their base glyph.
- All glyphs are original work, drawn from scratch for altfont. No outlines,
  metrics, kerning, anchors, hinting programs or OpenType feature code are
  taken from other fonts, neither directly nor through tracing or automated
  conversion. Other fonts may be used only as visual references and for
  side-by-side render comparisons. The design must not imitate a specific
  existing typeface closely enough to be recognised as a clone.

## 10. Quality assurance

- Automated render sheets via FreeType (Python `freetype-py`) for every style,
  for 11–32 ppem, in each rendering mode from section 2; output as PNG.
- Visual regression: compare render sheets against approved references.
- Real UI sample texts (menus, dialogs, tables) in English, Russian and other
  covered languages, rendered side by side with reference UI fonts.
- `fontbakery` checks (universal profile): no FAIL. Remaining WARNs are
  design decisions (alt_caron: the apostrophe caron is drawn, not a
  component; contour_count: β, §, ☑).
- `scripts/check.py`: coverage against section 5, empty glyphs, metrics,
  equal character sets across styles.
- Manual review in real applications: GTK and Qt on Linux, Windows.

## 11. Deliverables

- Hinted `TTF` files for the four styles.
- Render sheets and a short specimen.

## 12. Licensing

- Fonts (sources and binaries): SIL Open Font License 1.1, see `OFL.txt`.
  No Reserved Font Name is declared for altfont.
- Build scripts and tools: MIT, see `LICENSE`.

## 13. Known limitations

- Monochrome rendering at 11–12 ppem: ttfautohint applies x hints there and
  can close the gap between a stem and a following diagonal (и х), and Bold
  s g ж get dense. Fixing this needs manual hints or ttfautohint control
  instructions for individual glyphs.
- Vertical stems straddle pixels at sizes other than 13 and 15 ppem in
  grayscale; see section 8.
- & @ Ћ Ђ ₹ and some rare symbols are schematic and could be refined.

## 14. Open questions

1. Final family name (`altfont` is a working title, may become final);
   check for conflicts with existing fonts and trademarks before release.
2. CJK may be revisited after v1.

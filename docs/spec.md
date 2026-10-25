# altfont — Technical Specification (draft)

Status: draft, v0.1 (2026-10-25)

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


Italic: a real italic or a carefully corrected oblique (to be decided after
prototyping).

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
  including stacked Vietnamese marks.
- Slightly loose default spacing, suitable for UI text at small sizes.
- Tabular (fixed-width) figures by default or via `tnum`; to be decided.

## 7. Metrics

- TrueType outlines (`glyf`, quadratic curves).
- UPM: 2048 (preferred for TrueType hinting) — to be confirmed.
- Vertical metrics consistent across all styles; `OS/2` typo metrics with
  `USE_TYPO_METRICS` set, and `hhea`/`win` metrics chosen so that no glyph,
  including accented capitals, is clipped on Windows.
- Line height suitable for UI (roughly 1.2–1.25 em).

## 8. Hinting

- TrueType hinting, initially via `ttfautohint` with per-size control
  instructions where needed; manual hinting only if autohinting proves
  insufficient.
- Outlines must render well even when hints are ignored horizontally
  (FreeType v40) or entirely (unhinted renderers).

## 9. Sources and toolchain

- Glyph sources in UFO format, one master per style.
- Build with `fontmake` / `fontTools`, hint with `ttfautohint`.
- All build and test steps scripted and reproducible from the repository.
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
- `fontbakery` checks (universal profile) and coverage checks against the
  declared character set.
- Manual review in real applications: GTK and Qt on Linux, Windows.

## 11. Deliverables

- Hinted `TTF` files for the four styles.
- Render sheets and a short specimen.

## 12. Licensing

- Fonts (sources and binaries): SIL Open Font License 1.1, see `OFL.txt`.
  No Reserved Font Name is declared for altfont.
- Build scripts and tools: MIT, see `LICENSE`.

## 13. Open questions

1. Final family name (`altfont` is a working title, may become final);
   check for conflicts with existing fonts and trademarks before release.
2. Proportional or tabular figures by default.
3. CJK may be revisited after v1.

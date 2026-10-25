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
- Bold Italic (700) — needed for correct RIBBI style linking in most toolkits;
  see open questions.

Delivered as separate static TrueType fonts forming one family. No variable
font in v1 (hinting a variable font is much harder and gives worse results at
small sizes).

Italic: Latin, Cyrillic and Greek get a real italic or a carefully corrected
oblique (to be decided after prototyping). CJK glyphs stay upright in italic
styles, following common CJK practice.

Bold must stay distinguishable from Regular at 11–12 ppem, i.e. stems must
differ by at least one full pixel at those sizes.

## 5. Character coverage

v1 scope (tentative):

- Latin: Basic Latin, Latin-1 Supplement, Latin Extended-A.
- Cyrillic: full Russian, Ukrainian, Belarusian, Serbian, Bulgarian, Kazakh.
- Greek: modern monotonic.
- Punctuation, currency, common math, arrows, and UI symbols
  (check marks, ellipsis, triangles, etc.).
- CJK: ideographs plus kana and full-width forms. Exact standard is an open
  question (e.g. GB 2312 / JIS X 0208 level 1+2 / common Hangul).

Out of scope for v1: RTL scripts, Indic scripts, emoji, box drawing for
terminals.

## 6. Design principles

- Large x-height, open apertures, low stroke contrast, no hairlines.
- Unambiguous confusables: `I l 1 |`, `O 0`, `rn m`, `Б б 6`, `З 3`.
- Simple, grid-friendly shapes: straight stems, few diagonals and fine
  details; terminals cut horizontally or vertically where possible.
- Stem widths and key vertical metrics (baseline, x-height, cap height,
  ascender, descender) chosen so they snap cleanly at core UI sizes.
- Slightly loose default spacing, suitable for UI text at small sizes.
- Tabular (fixed-width) figures by default or via `tnum`; to be decided.
- CJK glyphs simplified where needed so that strokes do not merge at
  12–16 ppem; Latin and CJK must be visually balanced (weight, height).

## 7. Metrics

- TrueType outlines (`glyf`, quadratic curves).
- UPM: 2048 (preferred for TrueType hinting) — to be confirmed.
- Vertical metrics consistent across all styles; `OS/2` typo metrics with
  `USE_TYPO_METRICS` set, and `hhea`/`win` metrics chosen so that no common
  glyph is clipped on Windows.
- Line height suitable for UI (roughly 1.2–1.3 em incl. CJK).
- CJK ideographs on a full-width 1 em advance.

## 8. Hinting and bitmaps

- Latin/Cyrillic/Greek: TrueType hinting, initially via `ttfautohint` with
  per-size control instructions where needed; manual hinting only if
  autohinting proves insufficient.
- CJK: autohinting support for ideographs is weak, so the outlines themselves
  must be pixel-friendly. Optional embedded bitmap strikes (`EBDT`/`EBLC`)
  for the smallest sizes (e.g. 12, 14, 16 ppem) are a candidate, but the
  outlines must stand on their own: many renderers (DirectWrite, some
  cairo/fontconfig setups) ignore embedded bitmaps. Decision after a
  prototype.

## 9. Sources and toolchain

- Glyph sources in UFO format, one master per style.
- Build with `fontmake` / `fontTools`, hint with `ttfautohint`.
- All build and test steps scripted and reproducible from the repository.
- CJK and possibly Latin outlines may be derived from existing open-licensed
  fonts (e.g. OFL-licensed CJK families) instead of drawn from scratch. Any
  derived source must have a license compatible with redistribution under
  SIL OFL 1.1, and Reserved Font Names must be respected.

## 10. Quality assurance

- Automated render sheets via FreeType (Python `freetype-py`) for every style,
  for 11–32 ppem, in each rendering mode from section 2; output as PNG.
- Visual regression: compare render sheets against approved references.
- Real UI sample texts (menus, dialogs, tables) in English, Russian, Chinese,
  Japanese, rendered side by side with reference UI fonts.
- `fontbakery` checks (universal profile) and coverage checks against the
  declared character set.
- Manual review in real applications: GTK and Qt on Linux, Windows.

## 11. Deliverables

- `TTF` files for each style, hinted.
- Render sheets and a short specimen.
- Font license file (SIL OFL 1.1 expected).

## 12. Open questions

1. CJK scope: Simplified Chinese, Traditional Chinese, Japanese, Korean —
   which, and which character standard?
2. Is Bold Italic required (recommended for style linking)?
3. Draw CJK from scratch or derive from an existing OFL family?
   Drawing from scratch is several thousand glyphs per weight.
4. Embedded bitmaps for small CJK sizes: yes / no / after prototype.
5. Licensing: the repository is MIT now; fonts are normally SIL OFL 1.1, and
   OFL is mandatory if any OFL source is used. Proposed: OFL for fonts, MIT
   for build scripts.
6. Final family name (the repository name `altfont` is a working title).
7. Proportional or tabular figures by default.

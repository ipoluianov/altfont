# CLAUDE.md

## Project

altfont: a UI font for desktop applications (Regular, Bold, Italic,
Bold Italic; Latin, Cyrillic, Greek).
The main goal is crisp rendering at small UI sizes (11–18 ppem) with stock
FreeType grayscale or monochrome rendering, without subpixel AA.
Full requirements: [docs/spec.md](docs/spec.md). Read it before design or
tooling decisions; update it when a decision changes the requirements.

## Language

- Everything committed to the repository (code, comments, docs, commit
  messages) is in English.
- Talk to the user in Russian.

## Layout

- `src/altfont/` — the font source as Python code:
  `style.py` (metrics and per-style parameters), `glyphs.py` (parametric
  glyph definitions), `geometry.py` (shape primitives), `build.py`.
- `scripts/build.py` — builds `build/fonts/altfont-<Style>.ttf` (hinted) and
  `*-unhinted.ttf`.
- `scripts/render.py` — FreeType render sheets into `build/render/`
  (`sheet-<mode>.png`, 4x `zoom-<mode>.png`; modes light, full, mono,
  unhinted) with reference system fonts for comparison.
- `docs/` — specification and design notes.
- `build/` — generated, not committed.

## Toolchain

- Python 3 with `fontTools`, `skia-pathops`, `ttfautohint-py`, `freetype-py`,
  `pillow` (see `requirements.txt`).
- The system has no `python3-venv`; dependencies are installed into
  `.pydeps/` (`python3 -m pip install --target .pydeps -r requirements.txt`).
  Scripts add `src/` and `.pydeps/` to `sys.path` themselves, so run them
  with plain `python3 scripts/<name>.py`.

## Working rules

- Judge every outline change by rendered pixels at 11–18 ppem, not by how it
  looks zoomed in. Render sheets in grayscale `hintslight`, `hintfull` and
  mono modes are the source of truth.
- Keep builds reproducible: no manual steps outside `scripts/`.
- All glyphs are drawn from scratch. Never copy, trace or convert outlines,
  metrics, kerning, anchors, hinting or feature code from other fonts. Other
  fonts are allowed only as visual references and in comparison renders.
- Licensing: fonts are OFL 1.1 (`OFL.txt`), scripts are MIT (`LICENSE`).

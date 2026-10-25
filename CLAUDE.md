# CLAUDE.md

## Project

altfont: a UI font for desktop applications (Regular, Bold, Italic, with CJK).
The main goal is crisp rendering at small UI sizes (11–18 ppem) with stock
FreeType grayscale or monochrome rendering, without subpixel AA.
Full requirements: [docs/spec.md](docs/spec.md). Read it before design or
tooling decisions; update it when a decision changes the requirements.

## Language

- Everything committed to the repository (code, comments, docs, commit
  messages) is in English.
- Talk to the user in Russian.

## Layout (planned)

- `sources/` — UFO glyph sources, one per style.
- `scripts/` — build, hinting and render/test scripts (Python).
- `docs/` — specification and design notes.
- `build/` — generated fonts and render sheets; not committed.

## Toolchain

- Python 3 with `fontTools`, `fontmake`, `ufoLib2`, `freetype-py`,
  `fontbakery` (see `requirements.txt`; use a local `.venv`).
- `ttfautohint` for TrueType hinting.

## Working rules

- Judge every outline change by rendered pixels at 11–18 ppem, not by how it
  looks zoomed in. Render sheets in grayscale `hintslight`, `hintfull` and
  mono modes are the source of truth.
- Keep builds reproducible: no manual steps outside `scripts/`.
- Third-party glyph sources must be OFL-compatible; record origin and license
  of every imported source in `docs/`.

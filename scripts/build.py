#!/usr/bin/env python3
"""Build all styles into build/fonts/."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / ".pydeps")]

from altfont.build import build_family  # noqa: E402
from altfont.style import STYLES  # noqa: E402


def main():
    out = ROOT / "build" / "fonts"
    for paths in build_family(STYLES, out).values():
        for p in paths.values():
            print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()

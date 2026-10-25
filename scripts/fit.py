#!/usr/bin/env python3
"""Compute per-glyph pixel-fit adjustments into src/altfont/fit.json.

Run after changing glyph shapes, widths or spacing, then rebuild.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / ".pydeps")]

from altfont.build import FIT_FILE  # noqa: E402
from altfont.fit import fit_style  # noqa: E402
from altfont.style import UPRIGHT_STYLES  # noqa: E402


def main():
    data = {}
    for S in UPRIGHT_STYLES:
        result = fit_style(S)
        data[S.name] = {name: list(adj) for name, (adj, _) in result.items()}
        print(S.name)
        for name, (adj, gain) in result.items():
            print(f"  {name:8} lsb {adj[0]:+4} width {adj[1]:+4} rsb {adj[2]:+4}  gain {gain:.3f}")
    FIT_FILE.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(FIT_FILE.relative_to(ROOT))


if __name__ == "__main__":
    main()

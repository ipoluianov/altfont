#!/usr/bin/env python3
"""Compute automatic kerning into src/altfont/kern.json.

Run after changing glyph shapes or spacing (and after scripts/fit.py), then
rebuild.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / ".pydeps")]

from altfont.build import KERN_FILE  # noqa: E402
from altfont.kern import compute  # noqa: E402
from altfont.style import UPRIGHT_STYLES  # noqa: E402


def main():
    data = {}
    for S in UPRIGHT_STYLES:
        pairs = compute(S)
        data[S.name] = [[a, b, v] for (a, b), v in sorted(pairs.items())]
        print(f"{S.name}: {len(pairs)} pairs")
    KERN_FILE.write_text(json.dumps(data, indent=0, ensure_ascii=False) + "\n")
    print(KERN_FILE.relative_to(ROOT))


if __name__ == "__main__":
    main()

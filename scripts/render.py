#!/usr/bin/env python3
"""Render comparison sheets with FreeType into build/render/.

One sheet per rendering mode. Each size block shows altfont Regular and
Bold followed by reference system fonts. A 4x nearest-neighbour zoom of the
small sizes is written next to each sheet for pixel-level inspection.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / ".pydeps")]

import freetype  # noqa: E402
import uharfbuzz as hb  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

FONTS_DIR = ROOT / "build" / "fonts"
OUT_DIR = ROOT / "build" / "render"

SIZES = [11, 12, 13, 14, 15, 16, 18, 20, 24, 32]
ZOOM_SIZES = [11, 12, 13, 14, 16]
ZOOM = 4

TEXT = "File Edit View Help  Save file? (Ctrl+S) 12:45, 3.14% — «Да» / Нет  To AVATAR  Файл Правка Вид Справка  Ελληνικά  Tiếng Việt  Straße Żółć  Қазақ тілі  ← → ✓ ☑ €₽"

MODES = {
    # name: (load flags, render mode)
    "light": (freetype.FT_LOAD_TARGET_LIGHT, freetype.FT_RENDER_MODE_LIGHT),
    "full": (freetype.FT_LOAD_TARGET_NORMAL, freetype.FT_RENDER_MODE_NORMAL),
    "mono": (freetype.FT_LOAD_TARGET_MONO, freetype.FT_RENDER_MODE_MONO),
    "unhinted": (freetype.FT_LOAD_NO_HINTING, freetype.FT_RENDER_MODE_NORMAL),
}

REFERENCES = ["DejaVu Sans", "DejaVu Sans:bold", "DejaVu Sans:oblique", "Liberation Sans"]


def font_file(pattern):
    out = subprocess.run(["fc-match", "-f", "%{file}", pattern],
                         capture_output=True, text=True, check=True)
    return out.stdout


def faces():
    result = [(f"altfont {s}", str(FONTS_DIR / f"altfont-{s}.ttf"))
              for s in ("Regular", "Bold", "Italic", "BoldItalic")]
    result += [(ref, font_file(ref)) for ref in REFERENCES]
    return result


def bitmap_to_image(bitmap):
    w, h = bitmap.width, bitmap.rows
    img = Image.new("L", (w, h), 0)
    if w == 0 or h == 0:
        return img
    buf = bitmap.buffer
    pitch = bitmap.pitch
    if bitmap.pixel_mode == freetype.FT_PIXEL_MODE_MONO:
        px = img.load()
        for y in range(h):
            for x in range(w):
                if buf[y * pitch + x // 8] & (0x80 >> (x % 8)):
                    px[x, y] = 255
    else:
        data = bytes(b for y in range(h) for b in buf[y * pitch:y * pitch + w])
        img = Image.frombytes("L", (w, h), data)
    return img


def shape(path, text):
    """HarfBuzz shaping: [(glyph id, kerning in font units)], as applications do."""
    blob = hb.Blob.from_file_path(path)
    hb_face = hb.Face(blob)
    font = hb.Font(hb_face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})
    return [(info.codepoint, pos.x_advance - font.get_glyph_h_advance(info.codepoint))
            for info, pos in zip(buf.glyph_infos, buf.glyph_positions)]


def render_line(path, size, mode, text):
    """Render like an integer-positioning toolkit: hinted advances plus rounded kerning."""
    load_flags, render_mode = MODES[mode]
    face = freetype.Face(path)
    face.set_pixel_sizes(0, size)
    upem = face.units_per_EM
    # Room for stacked marks above the line ascent (usWinAscent).
    ascent = (face.size.ascender + 63) // 64 + size // 5
    descent = (-face.size.descender + 63) // 64
    glyphs = []
    for gid, kern in shape(path, text):
        face.load_glyph(gid, load_flags)
        face.glyph.render(render_mode)
        g = face.glyph
        glyphs.append((bitmap_to_image(g.bitmap), g.bitmap_left, g.bitmap_top,
                       (g.advance.x + 32) // 64 + round(kern * size / upem)))
    width = sum(max(adv, 0) for *_, adv in glyphs) + size * 2
    canvas = Image.new("L", (width, ascent + descent), 0)
    pen = 2
    for img, left, top, adv in glyphs:
        canvas.paste(255, (pen + left, ascent - top), img)
        pen += adv
    return canvas


def sheet(mode, sizes, text):
    label_font = ImageFont.load_default()
    rows = []
    for size in sizes:
        rows.append(("label", f"{size} px", None))
        for name, path in faces():
            rows.append((name, path, render_line(path, size, mode, text)))
    label_w = 150
    width = label_w + max(r[2].width for r in rows if r[2] is not None) + 10
    height = sum((r[2].height + 2) if r[2] else 16 for r in rows) + 10
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)
    y = 5
    for name, value, line in rows:
        if line is None:
            draw.text((5, y + 2), value, fill=0, font=label_font)
            y += 16
            continue
        draw.text((15, y), name, fill=110, font=label_font)
        img.paste(0, (label_w, y), line)
        y += line.height + 2
    return img


def blur_report(mode="light", sizes=range(11, 19)):
    """Print the share of partially covered ink, sum c(1-c) / sum c, per size.

    Lower is crisper. With light hinting rows are snapped, so the value is
    dominated by vertical stems that straddle pixel boundaries.
    """
    chars = sorted(set(TEXT.replace(" ", "")))
    load_flags, render_mode = MODES[mode]
    print("ppem  " + "  ".join(f"{name:>16}" for name, _ in faces()))
    for size in sizes:
        row = []
        for _, path in faces():
            face = freetype.Face(path)
            face.set_pixel_sizes(0, size)
            fuzz = ink = 0.0
            for ch in chars:
                face.load_char(ch, load_flags)
                face.glyph.render(render_mode)
                img = bitmap_to_image(face.glyph.bitmap)
                for v in img.get_flattened_data():
                    c = v / 255
                    fuzz += c * (1 - c)
                    ink += c
            row.append(fuzz / ink if ink else 0)
        print(f"{size:4}  " + "  ".join(f"{v:16.3f}" for v in row))


def main():
    if "--blur" in sys.argv:
        blur_report()
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for mode in MODES:
        img = sheet(mode, SIZES, TEXT)
        img.save(OUT_DIR / f"sheet-{mode}.png")
        zoom = sheet(mode, ZOOM_SIZES, TEXT)
        zoom = zoom.resize((zoom.width * ZOOM, zoom.height * ZOOM), Image.NEAREST)
        zoom.save(OUT_DIR / f"zoom-{mode}.png")
        print(f"build/render/sheet-{mode}.png, zoom-{mode}.png")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generic 4-bytes-per-row renderer for RTPS submessage diagrams.

Every row in the byte grid contains exactly four bytes.  Fields may span
several rows (for example an 8-byte sequence number occupies two rows).
The field table on the right is generated from the same field list, so the
two never disagree.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FIG = ROOT

S = 2
W = 1200

FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"

PALETTE = {
    "blue": "#D6DDF5",
    "yellow": "#F7E9A6",
    "pink": "#F2D2D2",
    "green": "#CDE8CD",
    "amber": "#F7D98D",
    "purple": "#E3D9F4",
    "teal": "#CDE9E9",
    "gray": "#E4E4E4",
    "white": "#FFFFFF",
}


SHORT = {
    "extraFlags": "XFL",
    "octetsToInlineQos": "OIQ",
    "readerId": "rId",
    "writerId": "wId",
    "writerSN": "SN",
    "serializedPayload": "payload",
    "fragmentStartingNum": "fragStart",
    "fragmentsInSubmessage": "nFrags",
    "fragmentSize": "fragSize",
    "lastFragmentNum": "lastFrag",
    "numLocators": "nLoc",
    "bitmapBase": "base",
    "numBits": "nBits",
    "bitmap[0]": "bm[0]",
}


@dataclass
class Field:
    name: str
    start: int
    length: int
    color: str = "blue"
    note: str = ""
    optional: bool = False


@dataclass
class Spec:
    name: str
    sub_id: str
    data: bytes
    fields: List[Field]
    flags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    subtitle: str = ""
    show_ascii: bool = False
    bit_row: Optional[List[Tuple[str, str, str, str]]] = None
    map_segments: Optional[List[Tuple[str, int, int, str]]] = None
    callouts: List[str] = field(default_factory=list)


def px(v):
    return int(round(v * S))


class Canvas:
    def __init__(self, height, width=W):
        self.height = height
        self.width = width
        self.img = Image.new("RGB", (px(width), px(height)), "#FFFFFF")
        self.d = ImageDraw.Draw(self.img)
        self.fonts = {}

    def font(self, path, size):
        key = (path, size)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(path, px(size))
        return self.fonts[key]

    def text(self, xy, text, size=14, bold=False, mono=False,
             fill="#1A1A1A", anchor="la"):
        path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REG)
        self.d.text((px(xy[0]), px(xy[1])), text,
                    font=self.font(path, size), fill=fill, anchor=anchor)

    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle([px(v) for v in box], fill=fill,
                         outline=outline, width=px(width))

    def rrect(self, box, fill=None, outline=None, radius=8, width=1):
        self.d.rounded_rectangle([px(v) for v in box], radius=px(radius),
                                 fill=fill, outline=outline, width=px(width))

    def line(self, xy, fill="#444444", width=1):
        self.d.line([px(v) for v in xy], fill=fill, width=px(width))


def color_for(offset, fields):
    for f in fields:
        if f.length and f.start <= offset < f.start + f.length:
            return PALETTE[f.color]
    return "#FAFAFA"


def check_fields(data, fields):
    covered = [0] * len(data)
    for f in fields:
        for off in range(f.start, f.start + f.length):
            if 0 <= off < len(data):
                covered[off] += 1
    bad = [(i, n) for i, n in enumerate(covered) if n != 1]
    assert not bad, f"field coverage error: {bad}"


def _wrap(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = w if not cur else cur + " " + w
    if cur:
        lines.append(cur)
    return lines


def render(spec: Spec, out_path: Path):
    check_fields(spec.data, spec.fields)
    rows = (len(spec.data) + 3) // 4

    grid_x = 130
    cell_w, cell_h, row_h = 88, 56, 66
    grid_y = 230 if spec.map_segments else 175
    grid_h = rows * row_h
    table_x = 600 if spec.show_ascii else 560
    table_w = 1160 - table_x
    table_y = grid_y
    table_row_h = 23
    table_h = 30 + len(spec.fields) * table_row_h
    callout_h = 24 * len(spec.callouts) + (36 if spec.callouts else 0)
    content_h = max(grid_h, table_h + callout_h)
    flags_y = grid_y + content_h + 28
    notes_h = 26 * len(spec.notes) + 18
    bit_h = (28 + 54 + 20) if spec.bit_row else 0
    height = flags_y + 54 + notes_h + bit_h + 40

    c = Canvas(height)
    c.text((40, 28), f"{spec.name} ({spec.sub_id})", size=25, bold=True)
    subtitle = spec.subtitle or "each row = 4 bytes"
    c.text((40, 66), subtitle, size=14, fill="#555555")

    # Optional message map (used by the full example).
    y = 100
    if spec.map_segments:
        total = len(spec.data)
        x0, x1 = 40, 1160
        for label, start, length, key in spec.map_segments:
            a = x0 + (x1 - x0) * start / total
            b = x0 + (x1 - x0) * (start + length) / total
            c.rect([a, y, b, y + 34], fill=PALETTE[key], outline="#444444", width=1)
            c.text(((a + b) / 2, y + 17), label, size=13, bold=True, anchor="mm")
        for off in [0] + [s for _, s, _, _ in spec.map_segments[1:]] + [total]:
            x = x0 + (x1 - x0) * off / total
            c.text((x, y + 40), f"0x{off:02X}", size=11, mono=True,
                   fill="#666666", anchor="la" if off < total else "ra")

    # Grid column headers.
    c.text((40, grid_y - 18), "offset", size=11, fill="#777777")
    for j in range(4):
        c.text((grid_x + j * cell_w + cell_w / 2, grid_y - 18),
               f"byte {j}", size=11, fill="#777777", anchor="mm")
    if spec.show_ascii:
        c.text((500, grid_y - 18), "ASCII", size=11, fill="#777777")

    # Byte grid.
    for row in range(rows):
        ry = grid_y + row * row_h
        c.text((40, ry + cell_h / 2), f"0x{row * 4:02X}", size=13,
               mono=True, fill="#666666", anchor="lm")
        for j in range(4):
            off = row * 4 + j
            x = grid_x + j * cell_w
            if off >= len(spec.data):
                c.rect([x, ry, x + cell_w - 4, ry + cell_h], fill="#FAFAFA",
                       outline="#E6E6E6", width=1)
                continue
            fill = color_for(off, spec.fields)
            c.rect([x, ry, x + cell_w - 4, ry + cell_h], fill=fill,
                   outline="#FFFFFF", width=1)
            c.text((x + (cell_w - 4) / 2, ry + cell_h / 2),
                   f"{spec.data[off]:02X}", size=16, mono=True, anchor="mm")
            if spec.show_ascii:
                b = spec.data[off]
                ch = chr(b) if 32 <= b <= 126 else "."
                c.text((500 + j * 15, ry + cell_h / 2), ch, size=14,
                       mono=True, fill="#333333" if 32 <= b <= 126 else "#A0A0A0",
                       anchor="lm")

    # Field outlines, per row segment.
    for row in range(rows):
        ry = grid_y + row * row_h
        base = row * 4
        for f in spec.fields:
            if not f.length:
                continue
            a = max(f.start, base)
            b = min(f.start + f.length - 1, base + 3)
            if a > b:
                continue
            x0 = grid_x + (a - base) * cell_w
            x1 = grid_x + (b - base + 1) * cell_w - 4
            c.rect([x0 - 1, ry - 1, x1 + 1, ry + cell_h + 1],
                   outline="#444444", width=1.5)

    # Field table.
    c.text((table_x, table_y - 20), "field", size=11, bold=True, fill="#555555")
    c.text((table_x + 250, table_y - 20), "offset", size=11, bold=True, fill="#555555")
    c.text((table_x + 335, table_y - 20), "len", size=11, bold=True, fill="#555555")
    c.text((table_x + 390, table_y - 20), "notes", size=11, bold=True, fill="#555555")
    for i, f in enumerate(spec.fields):
        ty = table_y + i * table_row_h
        c.rect([table_x, ty + 3, table_x + 15, ty + 18],
               fill=PALETTE[f.color], outline="#666666", width=1)
        label = f.name + ("*" if f.optional else "")
        c.text((table_x + 23, ty), label, size=12.5, bold=True)
        off = f"0x{f.start:02X}" if not f.length else f"0x{f.start:02X}"
        c.text((table_x + 250, ty), off, size=12, mono=True, fill="#444444")
        ln = f"{f.length} B" + ("*" if f.optional else "") if f.length else "0 B*"
        c.text((table_x + 335, ty), ln, size=12, fill="#444444")
        c.text((table_x + 390, ty), f.note, size=11, fill="#555555")

    # Flags panel.
    if spec.flags:
        c.rrect([40, flags_y, 1160, flags_y + 34], fill="#F7F7F7",
                outline="#DDDDDD", radius=6)
        c.text((54, flags_y + 8), "flags", size=12, bold=True, fill="#555555")
        c.text((110, flags_y + 8), "  |  ".join(spec.flags), size=13)

    # Notes.
    ny = flags_y + 52
    for note in spec.notes:
        c.text((40, ny), note, size=12, fill="#555555")
        ny += 24

    # Optional callouts below the field table (full example).
    if spec.callouts:
        cy = table_y + table_h + 20
        c.text((table_x, cy), "decoded values", size=13, bold=True, fill="#333333")
        cy += 24
        for line in spec.callouts:
            c.text((table_x, cy), line, size=11.5, mono=False, fill="#444444")
            cy += 22

    # Optional bit row (SubmessageHeader figure).
    if spec.bit_row:
        by = flags_y + 52 + notes_h
        c.text((40, by), "DATA flags = 0x05", size=14, bold=True)
        by += 28
        bw, bh = 66, 54
        for i, (bit_name, value, flag, key) in enumerate(spec.bit_row):
            x = 40 + i * (bw + 4)
            c.rect([x, by, x + bw, by + bh], fill=PALETTE[key],
                   outline="#444444", width=1)
            c.text((x + bw / 2, by + 10), bit_name, size=10, fill="#555555",
                   anchor="mm")
            c.text((x + bw / 2, by + 29), value, size=16, mono=True, anchor="mm")
            c.text((x + bw / 2, by + 45), flag, size=10, bold=True, anchor="mm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    c.img.save(out_path)
    print(f"wrote {out_path} ({c.img.size[0]}x{c.img.size[1]})")


DISPLAY = {
    "protocol": "RTPS",
    "FLG": "flags",
    "LEN": "length",
    "ID": "ID",
}


def _fit_font(c, text, max_w, max_h, base=15):
    for size in range(base, 8, -1):
        font = c.font(FONT_BOLD, size)
        w = c.d.textlength(text, font=font) / S
        if w <= max_w - 12 and size <= max_h - 6:
            return size
    return 9


def render_structure(spec: Spec, out_path: Path):
    """Render a structure-only diagram: 4-byte rows and field-name blocks.

    No example byte values, no field table and no explanatory notes.  Each
    field is drawn as one merged block containing its name; the article text
    after the figure lists offsets, lengths and meanings.
    """
    check_fields(spec.data, spec.fields)
    rows = (len(spec.data) + 3) // 4

    width = 900
    cell_w, cell_h, row_h, grid_y = 120, 60, 84, 70
    grid_x = 210
    offset_x = 110
    bit_h = (28 + 56 + 26) if spec.bit_row else 0
    height = grid_y + rows * row_h + bit_h + 30

    c = Canvas(height, width=width)

    # Offsets and the four byte-column headers.
    c.text((offset_x, grid_y - 30), "offset", size=11, fill="#777777")
    for j in range(4):
        c.text((grid_x + j * cell_w + cell_w / 2, grid_y - 30),
               f"byte {j}", size=11, fill="#777777", anchor="mm")

    # Rows: offsets only; fields are drawn as merged blocks below.
    for row in range(rows):
        ry = grid_y + row * row_h
        c.text((offset_x, ry + cell_h / 2), f"0x{row * 4:02X}", size=14,
               mono=True, fill="#666666", anchor="lm")

    # Field blocks.  Multi-row fields must occupy whole rows (true for all
    # examples in this article); each block gets its field name centered.
    for f in sorted(spec.fields, key=lambda x: x.start):
        if not f.length:
            continue
        start_row, start_col = divmod(f.start, 4)
        end_row, end_col = divmod(f.start + f.length - 1, 4)
        if end_row > start_row:
            assert start_col == 0 and end_col == 3, (
                f.name, f.start, f.length, start_row, start_col, end_row, end_col
            )
        x0 = grid_x + start_col * cell_w
        x1 = grid_x + (end_col + 1) * cell_w - 4
        y0 = grid_y + start_row * row_h
        y1 = grid_y + end_row * row_h + cell_h
        c.rect([x0, y0, x1, y1], fill=PALETTE[f.color],
               outline="#444444", width=1.5)
        label = DISPLAY.get(f.name, f.name)
        size = _fit_font(c, label, x1 - x0, y1 - y0)
        c.text(((x0 + x1) / 2, (y0 + y1) / 2), label,
               size=size, bold=True, anchor="mm")

    # Optional flags-bit structure (no 0/1 example values).
    if spec.bit_row:
        by = grid_y + rows * row_h + 22
        c.text((offset_x, by), "flags byte", size=13, bold=True)
        by += 26
        bw, bh = 80, 56
        for i, (bit_name, _value, flag, key) in enumerate(spec.bit_row):
            x = offset_x + i * (bw + 4)
            c.rect([x, by, x + bw, by + bh], fill=PALETTE[key],
                   outline="#444444", width=1)
            c.text((x + bw / 2, by + 14), bit_name, size=10,
                   fill="#555555", anchor="mm")
            c.text((x + bw / 2, by + 38), flag, size=14, bold=True, anchor="mm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    c.img.save(out_path)
    print(f"wrote {out_path} ({c.img.size[0]}x{c.img.size[1]})")

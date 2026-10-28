#!/usr/bin/env python3
"""Generate ditaa sources for RTPS article figures 1-6.

The generator keeps field widths proportional to byte length where possible
(2 characters per byte by default) and puts short English labels inside the
cells.  Longer explanations belong in the Chinese article text.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
SRC = ROOT

# ditaa in PlantUML only recognizes a small palette reliably.
COLORS = {
    "blue": "cBLU",
    "yellow": "cYEL",
    "pink": "cPNK",
    "green": "cGRE",
}


@dataclass
class Field:
    label: str
    nbytes: int
    value: str = ""
    color: str = "blue"
    optional: bool = False
    width: Optional[int] = None

    @property
    def display_label(self) -> str:
        return self.label + ("*" if self.optional else "")

    @property
    def display_length(self) -> str:
        return f"{self.nbytes}B" + ("*" if self.optional else "")


def _center(text: str, width: int) -> str:
    if len(text) > width:
        raise ValueError(f"text {text!r} ({len(text)}) does not fit width {width}")
    left = (width - len(text)) // 2
    right = width - len(text) - left
    return " " * left + text + " " * right


def _width(field: Field, per_byte: int, min_width: int) -> int:
    if field.width is not None:
        return field.width
    return max(
        min_width,
        field.nbytes * per_byte,
        len(field.display_label) + 2,
        len(field.value) + 2,
    )


def _bar_lines(fields, per_byte=2, min_width=4, offset_base=0):
    widths = [_width(f, per_byte, min_width) for f in fields]
    top = "+" + "+".join("-" * w for w in widths) + "+"
    rows = [
        "|" + "|".join(COLORS[f.color].ljust(w) for f, w in zip(fields, widths)) + "|",
        "|" + "|".join(_center(f.display_label, w) for f, w in zip(fields, widths)) + "|",
    ]
    if any(f.value for f in fields):
        rows.append(
            "|" + "|".join(_center(f.value, w) for f, w in zip(fields, widths)) + "|"
        )
    rows.append(
        "|" + "|".join(_center(f.display_length, w) for f, w in zip(fields, widths)) + "|"
    )
    bottom = top

    # Byte-offset ruler: put labels at the left border of each field.
    starts = []
    pos = 1
    offset = offset_base
    for f, w in zip(fields, widths):
        if f.nbytes > 0:
            starts.append((offset, pos))
        offset += f.nbytes
        pos += w + 1
    starts.append((offset, pos - 1))

    ruler = [" "] * len(top)
    occupied = [False] * len(top)
    for off, start in starts:
        text = str(off)
        if start + len(text) > len(top):
            start = len(top) - len(text)
        if any(occupied[start:start + len(text)]):
            continue
        for i, ch in enumerate(text):
            ruler[start + i] = ch
            occupied[start + i] = True

    return ["".join(ruler).rstrip(), top, *rows, bottom]


def _note(lines, width=None):
    width = width or (max(len(line) for line in lines) + 4)
    top = "+" + "-" * (width - 2) + "+"
    body = ["| " + line.ljust(width - 4) + " |" for line in lines]
    return [top, *body, top]


def _bit_row(names, values, labels=None, colors=None):
    """One row of single-bit cells; every cell gets a color line."""
    colors = colors or ["blue"] * len(names)
    fields = [
        Field(label=n, nbytes=1, value=v, color=c, width=max(5, len(n) + 2, len(v) + 2))
        for n, v, c in zip(names, values, colors)
    ]
    widths = [f.width for f in fields]
    top = "+" + "+".join("-" * w for w in widths) + "+"
    rows = [
        "|" + "|".join(COLORS[c].ljust(w) for c, w in zip(colors, widths)) + "|",
        "|" + "|".join(_center(n, w) for n, w in zip(names, widths)) + "|",
        "|" + "|".join(_center(v, w) for v, w in zip(values, widths)) + "|",
    ]
    if labels:
        rows.append("|" + "|".join(_center(l, w) for l, w in zip(labels, widths)) + "|")
    return [top, *rows, top]


def _figure(title, blocks, scale=2):
    lines = [f"@startditaa(scale={scale})", title, ""]
    for block in blocks:
        lines.extend(block)
        lines.append("")
    lines.append("@endditaa")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Figure definitions
# ---------------------------------------------------------------------------

def fig01():
    fields = [
        Field("HEADER", 20, "", "blue"),
        Field("SUBMSG 1", 8, "4B hdr + body", "green"),
        Field("SUBMSG 2", 8, "4B hdr + body", "green"),
        Field("... / PAD", 4, "", "pink"),
    ]
    bar = _bar_lines(fields, per_byte=1, min_width=7)
    note = _note([
        "UDP payload length is one RTPS message",
        "Each submessage starts on a 32 bit boundary",
        "SubmessageHeader is 4 B. rest is body",
    ])
    return _figure("RTPS message consists of header + N submessages", [bar, note], scale=2)


def fig02():
    header = [
        Field("proto", 4, '"RTPS"', "blue"),
        Field("ver", 2, "2.3", "yellow"),
        Field("vend", 2, "010F", "pink"),
        Field("guidPrefix", 12, "01 0F 2A ...", "green"),
    ]
    guid = [
        Field("guidPrefix", 12, "", "green"),
        Field("entityId", 4, "", "yellow"),
    ]
    entity = [
        Field("entityKey", 3, "", "green"),
        Field("kind", 1, "", "pink"),
    ]
    note = _note([
        "GUID is guidPrefix + entityId",
        "SPDP writer is 00 01 00 C2",
        "Participant is 00 00 01 C1",
        "User writer is 00 00 01 02",
        "proto is protocol. ver is version. vend is vendorId.",
    ])
    blocks = [
        _bar_lines(header, per_byte=2, min_width=5),
        _bar_lines(guid, per_byte=2, min_width=5),
        _bar_lines(entity, per_byte=2, min_width=5),
        note,
    ]
    return _figure("RTPS Header (20 B) and GUID/EntityId", blocks, scale=2)


def fig03():
    header = [
        Field("ID", 1, "0x15", "yellow"),
        Field("FLG", 1, "0x05", "pink"),
        Field("LEN", 2, "40", "blue"),
    ]
    bar = _bar_lines(header, per_byte=2, min_width=6)
    bits = _bit_row(
        ["bit7", "bit6", "bit5", "bit4", "bit3", "bit2", "bit1", "bit0"],
        ["X", "X", "X", "N", "K", "D", "Q", "E"],
        ["0", "0", "0", "0", "0", "1", "0", "1"],
        ["blue", "blue", "blue", "pink", "pink", "green", "pink", "yellow"],
    )
    note = _note([
        "E means endianness (0 big, 1 little)",
        "DATA flag Q is inline QoS, D is data, K is key, N is non standard",
        "HEARTBEAT flag F is final, L is liveliness",
        "ACKNACK flag F is final. INFO_TS flag I is invalidate",
        "LEN 0 means last submessage (PAD and INFO_TS special)",
    ])
    return _figure("SubmessageHeader (4 B) and DATA flags", [bar, bits, note], scale=2)


def fig04():
    fixed = [
        Field("ID", 1, "15", "yellow"),
        Field("FLG", 1, "05", "pink"),
        Field("LEN", 2, "40", "yellow"),
        Field("XFL", 2, "0000", "blue"),
        Field("OIQ", 2, "0010", "blue"),
        Field("rId", 4, "0", "green"),
        Field("wId", 4, "0102", "green"),
        Field("SN", 8, "1", "yellow"),
    ]
    tail = [
        Field("iQoS*", 0, "", "pink"),
        Field("payload", 20, "repr+CDR", "green"),
    ]
    note = _note([
        "XFL is extraFlags. OIQ is octetsToInlineQos.",
        "rId is readerId. wId is writerId. SN is writerSN.",
        "OIQ 16 means payload starts after writerSN",
        "inlineQoS is optional, 0 B in this example",
        "payload is 00 01 00 00 + CDR string 'Hello RTPS'",
    ])
    blocks = [
        _bar_lines(fixed, per_byte=2, min_width=4),
        _bar_lines(tail, per_byte=2, min_width=5, offset_base=24),
        note,
    ]
    return _figure("DATA submessage (44 B example)", blocks, scale=2)


def fig05():
    hb = [
        Field("ID", 1, "07", "yellow"),
        Field("FLG", 1, "01", "pink"),
        Field("LEN", 2, "28", "yellow"),
        Field("rId", 4, "0", "green"),
        Field("wId", 4, "0102", "green"),
        Field("firstSN", 8, "1", "blue"),
        Field("lastSN", 8, "3", "blue"),
        Field("count", 4, "1", "yellow"),
    ]
    ack = [
        Field("ID", 1, "06", "yellow"),
        Field("FLG", 1, "03", "pink"),
        Field("LEN", 2, "28", "yellow"),
        Field("rId", 4, "0", "green"),
        Field("wId", 4, "0102", "green"),
        Field("base", 8, "1", "blue"),
        Field("nBits", 4, "3", "yellow"),
        Field("bm[0]", 4, "40000000", "pink"),
        Field("count", 4, "1", "yellow"),
    ]
    bitrow = _bit_row(
        ["bit31", "bit30", "bit29"],
        ["0", "1", "0"],
        ["SN1", "SN2", "SN3"],
        ["blue", "pink", "blue"],
    )
    note = _note([
        "HEARTBEAT flag F is final, L is liveliness",
        "ACKNACK flag F is final",
        "base is bitmapBase. bm[0] is bitmap word.",
        "bitmap is MSB first and bit31 maps to base",
        "SN2 bit 1 means missing, so request retransmit",
        "count detects duplicate messages",
    ])
    blocks = [
        _bar_lines(hb, per_byte=2, min_width=4),
        _bar_lines(ack, per_byte=2, min_width=4),
        bitrow,
    ]
    return _figure("HEARTBEAT (32 B) and ACKNACK (32 B)", blocks, scale=2)


def fig06():
    ts = [
        Field("ID", 1, "09", "yellow"),
        Field("FLG", 1, "01", "pink"),
        Field("LEN", 2, "08", "yellow"),
        Field("sec", 4, "1792238400", "blue"),
        Field("frac", 4, "80000000", "blue"),
    ]
    dst = [
        Field("ID", 1, "0E", "yellow"),
        Field("FLG", 1, "01", "pink"),
        Field("LEN", 2, "0C", "yellow"),
        Field("guidPrefix", 12, "", "green"),
    ]
    df_fixed = [
        Field("ID", 1, "16", "yellow"),
        Field("FLG", 1, "01", "pink"),
        Field("LEN", 2, "...", "yellow"),
        Field("XFL", 2, "0000", "blue"),
        Field("OIQ", 2, "0010", "blue"),
        Field("rId", 4, "0", "green"),
        Field("wId", 4, "0102", "green"),
        Field("SN", 8, "...", "yellow"),
    ]
    df_frag = [
        Field("fragStart", 4, "1", "blue"),
        Field("nFrags", 2, "4", "yellow"),
        Field("fragSize", 2, "1024", "yellow"),
        Field("sampleSize", 4, "4096", "blue"),
        Field("payload", 20, "...", "green"),
    ]
    note = _note([
        "INFO_TS I flag 1 omits timestamp (4 B total)",
        "INFO_DST sets the destination guidPrefix",
        "DATA_FRAG fragStart begins at 1",
        "payload size is nFrags times fragSize",
        "DATA_FRAG K and N flag positions differ from DATA",
        "sec is seconds. frac is units of 1/4294967296 s.",
    ])
    blocks = [
        _bar_lines(ts, per_byte=2, min_width=4),
        _bar_lines(dst, per_byte=2, min_width=4),
        _bar_lines(df_fixed, per_byte=2, min_width=4),
        _bar_lines(df_frag, per_byte=2, min_width=5, offset_base=24),
        note,
    ]
    return _figure("INFO_TS / INFO_DST / DATA_FRAG", blocks, scale=2)


FIGURES = {
    "fig01-message-overview": fig01,
}


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGURES.items():
        path = SRC / f"{name}.puml"
        path.write_text(fn(), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()

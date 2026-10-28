#!/usr/bin/env python3
"""Build figures 2-17 as 4-bytes-per-row grids.

Figure 1 (overall composition) stays a ditaa diagram; figure 18 is a
PlantUML sequence diagram.  Everything else is generated here.
"""

from pathlib import Path

from grid_render import Field, Spec, render_structure, FIG


def h(text):
    return bytes.fromhex(" ".join(text.split()))


def F(name, start, length, color="blue", note="", optional=False):
    return Field(name, start, length, color, note, optional)


HEADER = h(
    "52 54 50 53 02 03 01 0F "
    "01 0F 2A 3B 4C 5D 6E 7F 80 91 A2 B3"
)
INFO_TS = h("09 01 08 00 40 63 D3 6A 00 00 00 80")
DATA = h(
    "15 05 28 00 00 00 10 00 "
    "00 00 00 00 00 00 01 02 "
    "00 00 00 00 01 00 00 00 "
    "00 01 00 00 0B 00 00 00 "
    "48 65 6C 6C 6F 20 52 54 50 53 00 00"
)


SPECS = []


def add(filename, spec):
    SPECS.append((filename, spec))


add("fig02-header-structure.png", Spec(
    name="RTPS Header",
    sub_id="20 B",
    data=HEADER,
    fields=[
        F("protocol", 0, 4, "blue", 'magic "RTPS"'),
        F("version", 4, 2, "yellow", "2.3"),
        F("vendorId", 6, 2, "pink", "eProsima 0x010F"),
        F("guidPrefix", 8, 12, "green", "participant prefix"),
    ],
    notes=[
        "GUID = guidPrefix (12 B) + EntityId (4 B)",
        "built-in EntityIds: SPDP writer 00 01 00 C2, participant 00 00 01 C1",
        "the first two guidPrefix bytes equal vendorId",
    ],
    subtitle="20 B | every row is 4 bytes",
))

add("fig03-submessage-header-structure.png", Spec(
    name="SubmessageHeader",
    sub_id="4 B",
    data=h("15 05 28 00"),
    fields=[
        F("ID", 0, 1, "yellow", "0x15 = DATA"),
        F("FLG", 1, 1, "pink", "E=1, D=1"),
        F("LEN", 2, 2, "blue", "40 (0x28)"),
    ],
    flags=[
        "E: 0 = big-endian, 1 = little-endian",
        "DATA: Q=inline QoS, D=data, K=key, N=non-standard",
    ],
    notes=[
        "octetsToNextHeader = 0 means the last submessage (PAD/INFO_TS special)",
        "unknown submessage IDs are skipped using this length",
    ],
    subtitle="4 B | flag bits shown below | every row is 4 bytes",
    bit_row=[
        ("bit7", "X", "", "blue"),
        ("bit6", "X", "", "blue"),
        ("bit5", "X", "", "blue"),
        ("bit4", "0", "N", "pink"),
        ("bit3", "0", "K", "pink"),
        ("bit2", "1", "D", "green"),
        ("bit1", "0", "Q", "pink"),
        ("bit0", "1", "E", "yellow"),
    ],
))

add("fig04-data-structure.png", Spec(
    name="DATA",
    sub_id="0x15",
    data=DATA,
    fields=[
        F("ID", 0, 1, "yellow", "0x15"),
        F("FLG", 1, 1, "pink", "E=1, D=1"),
        F("LEN", 2, 2, "blue", "40 (0x28)"),
        F("extraFlags", 4, 2, "teal", "0"),
        F("octetsToInlineQos", 6, 2, "teal", "16 (0x10)"),
        F("readerId", 8, 4, "green", "all readers"),
        F("writerId", 12, 4, "green", "user writer"),
        F("writerSN", 16, 8, "amber", "SN=1"),
        F("inlineQoS", 24, 0, "gray", "optional, omitted", optional=True),
        F("serializedPayload", 24, 20, "purple", "CDR_LE + string"),
    ],
    flags=["E=1", "Q=0", "D=1", "K=0", "N=0"],
    notes=[
        "octetsToInlineQos = 16 -> payload starts at 0x18",
        "payload = CDR_LE header + 11-byte string + 1-byte pad",
    ],
    subtitle="44 B | every row is 4 bytes",
))

add("fig05-data-frag-structure.png", Spec(
    name="DATA_FRAG",
    sub_id="0x16",
    data=h(
        "16 01 28 00 00 00 10 00 "
        "00 00 00 00 00 00 01 02 "
        "00 00 00 00 01 00 00 00 "
        "01 00 00 00 04 00 00 04 "
        "00 10 00 00 48 65 6C 6C "
        "6F 20 52 54"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x16"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "40 (0x28)"),
        F("extraFlags", 4, 2, "teal", "0"),
        F("octetsToInlineQos", 6, 2, "teal", "16"),
        F("readerId", 8, 4, "green", "all readers"),
        F("writerId", 12, 4, "green", "user writer"),
        F("writerSN", 16, 8, "amber", "SN=1"),
        F("fragmentStartingNum", 24, 4, "yellow", "1"),
        F("fragmentsInSubmessage", 28, 2, "yellow", "4"),
        F("fragmentSize", 30, 2, "yellow", "1024"),
        F("sampleSize", 32, 4, "blue", "4096"),
        F("serializedPayload", 36, 8, "purple", "fragment data"),
    ],
    flags=["E=1", "Q=0", "K=0", "N=0"],
    notes=[
        "fragments are numbered from 1",
        "sampleSize = fragmentsInSubmessage x fragmentSize",
    ],
    subtitle="44 B (36 B fixed + 8 B payload) | every row is 4 bytes",
))

add("fig06-gap-structure.png", Spec(
    name="GAP",
    sub_id="0x08",
    data=h(
        "08 01 1C 00 00 00 00 00 "
        "00 00 01 02 02 00 00 00 "
        "00 00 00 00 04 00 00 00 "
        "00 00 00 00 00 00 00 00"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x08"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "28 (0x1C)"),
        F("readerId", 4, 4, "green", "all readers"),
        F("writerId", 8, 4, "green", "user writer"),
        F("gapStart", 12, 8, "amber", "2"),
        F("bitmapBase", 20, 8, "amber", "4"),
        F("numBits", 28, 4, "yellow", "0"),
    ],
    flags=["E=1"],
    notes=[
        "gapStart=2, gapList.base=4, numBits=0: SN2 and SN3 are irrelevant",
        "gapList is a SequenceNumberSet",
    ],
    subtitle="32 B | every row is 4 bytes",
))

add("fig07-heartbeat-structure.png", Spec(
    name="HEARTBEAT",
    sub_id="0x07",
    data=h(
        "07 01 1C 00 00 00 00 00 "
        "00 00 01 02 01 00 00 00 "
        "00 00 00 00 03 00 00 00 "
        "00 00 00 00 01 00 00 00"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x07"),
        F("FLG", 1, 1, "pink", "E=1, F=0, L=0"),
        F("LEN", 2, 2, "blue", "28 (0x1C)"),
        F("readerId", 4, 4, "green", "all readers"),
        F("writerId", 8, 4, "green", "user writer"),
        F("firstSN", 12, 8, "amber", "1"),
        F("lastSN", 20, 8, "amber", "3"),
        F("count", 28, 4, "yellow", "1"),
    ],
    flags=["E=1", "F=0", "L=0"],
    notes=[
        "F=0: Reader must answer with ACKNACK",
        "L=1 refreshes manual liveliness",
    ],
    subtitle="32 B | every row is 4 bytes",
))

add("fig08-acknack-structure.png", Spec(
    name="ACKNACK",
    sub_id="0x06",
    data=h(
        "06 03 1C 00 00 00 00 00 "
        "00 00 01 02 01 00 00 00 "
        "00 00 00 00 03 00 00 00 "
        "00 00 00 40 01 00 00 00"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x06"),
        F("FLG", 1, 1, "pink", "E=1, F=1"),
        F("LEN", 2, 2, "blue", "28 (0x1C)"),
        F("readerId", 4, 4, "green", "all readers"),
        F("writerId", 8, 4, "green", "user writer"),
        F("bitmapBase", 12, 8, "amber", "1"),
        F("numBits", 20, 4, "yellow", "3"),
        F("bitmap[0]", 24, 4, "purple", "0x40000000"),
        F("count", 28, 4, "yellow", "1"),
    ],
    flags=["E=1", "F=1"],
    notes=[
        "bitmap 0x40000000: first 3 bits 010 -> SN2 missing",
        "bitmap is MSB-first (bit31 = bitmapBase)",
    ],
    subtitle="32 B | every row is 4 bytes",
))

add("fig09-heartbeat-frag-structure.png", Spec(
    name="HEARTBEAT_FRAG",
    sub_id="0x13",
    data=h(
        "13 01 18 00 00 00 00 00 "
        "00 00 01 02 01 00 00 00 "
        "00 00 00 00 04 00 00 00 "
        "01 00 00 00"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x13"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "24 (0x18)"),
        F("readerId", 4, 4, "green", "all readers"),
        F("writerId", 8, 4, "green", "user writer"),
        F("writerSN", 12, 8, "amber", "SN=1"),
        F("lastFragmentNum", 20, 4, "yellow", "4"),
        F("count", 24, 4, "yellow", "1"),
    ],
    flags=["E=1"],
    notes=[
        "lastFragmentNum=4: fragments 1..4 are available",
    ],
    subtitle="28 B | every row is 4 bytes",
))

add("fig10-nack-frag-structure.png", Spec(
    name="NACK_FRAG",
    sub_id="0x12",
    data=h(
        "12 01 20 00 00 00 00 00 "
        "00 00 01 02 01 00 00 00 "
        "00 00 00 00 01 00 00 00 "
        "04 00 00 00 00 00 00 40 "
        "01 00 00 00"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x12"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "32 (0x20)"),
        F("readerId", 4, 4, "green", "all readers"),
        F("writerId", 8, 4, "green", "user writer"),
        F("writerSN", 12, 8, "amber", "SN=1"),
        F("bitmapBase", 20, 4, "yellow", "1"),
        F("numBits", 24, 4, "yellow", "4"),
        F("bitmap[0]", 28, 4, "purple", "0x40000000"),
        F("count", 32, 4, "yellow", "1"),
    ],
    flags=["E=1"],
    notes=[
        "FragmentNumberSet: bitmapBase + numBits + bitmap",
        "bitmap 0x40000000 requests fragment 2",
    ],
    subtitle="36 B | every row is 4 bytes",
))

add("fig11-info-ts-structure.png", Spec(
    name="INFO_TS",
    sub_id="0x09",
    data=INFO_TS,
    fields=[
        F("ID", 0, 1, "yellow", "0x09"),
        F("FLG", 1, 1, "pink", "E=1, I=0"),
        F("LEN", 2, 2, "blue", "8"),
        F("seconds", 4, 4, "purple", "1792238400"),
        F("fraction", 8, 4, "purple", "0x80000000"),
    ],
    flags=["E=1", "I=0"],
    notes=[
        "I=1: timestamp omitted (4 B total)",
        "fraction unit is 2^-32 s; 0x80000000 = 0.5 s",
    ],
    subtitle="12 B | every row is 4 bytes",
))

add("fig12-info-dst-structure.png", Spec(
    name="INFO_DST",
    sub_id="0x0E",
    data=h("0E 01 0C 00 AA BB CC DD EE FF 00 11 22 33 44 55"),
    fields=[
        F("ID", 0, 1, "yellow", "0x0E"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "12"),
        F("guidPrefix", 4, 12, "green", "destination prefix"),
    ],
    flags=["E=1"],
    notes=[
        "changes the destination for following submessages",
        "does not carry user data",
    ],
    subtitle="16 B | every row is 4 bytes",
))

add("fig13-info-src-structure.png", Spec(
    name="INFO_SRC",
    sub_id="0x0C",
    data=h(
        "0C 01 14 00 00 00 00 00 "
        "02 03 01 0F 01 0F 2A 3B "
        "4C 5D 6E 7F 80 91 A2 B3"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x0C"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "20 (0x14)"),
        F("unused", 4, 4, "gray", "must be zero"),
        F("version", 8, 2, "yellow", "2.3"),
        F("vendorId", 10, 2, "pink", "0x010F"),
        F("guidPrefix", 12, 12, "green", "source prefix"),
    ],
    flags=["E=1"],
    notes=[
        "changes the logical source for following submessages",
        "unused field is reserved and must be zero",
    ],
    subtitle="24 B | every row is 4 bytes",
))

add("fig14-info-reply-structure.png", Spec(
    name="INFO_REPLY",
    sub_id="0x0F",
    data=h(
        "0F 01 1C 00 01 00 00 00 "
        "01 00 00 00 F4 1C 00 00 "
        "7F 00 00 01 00 00 00 00 "
        "00 00 00 00 00 00 00 00"
    ),
    fields=[
        F("ID", 0, 1, "yellow", "0x0F"),
        F("FLG", 1, 1, "pink", "E=1, M=0"),
        F("LEN", 2, 2, "blue", "28 (0x1C)"),
        F("numLocators", 4, 4, "yellow", "1"),
        F("kind", 8, 4, "teal", "UDPv4 = 1"),
        F("port", 12, 4, "teal", "7412 (0x1CF4)"),
        F("address", 16, 16, "green", "127.0.0.1 + zeros"),
    ],
    flags=["E=1", "M=0"],
    notes=[
        "one unicast LocatorUDPv4",
        "M=1 adds a multicast LocatorList",
    ],
    subtitle="32 B | every row is 4 bytes",
))

add("fig15-info-reply-ip4-structure.png", Spec(
    name="INFO_REPLY_IP4",
    sub_id="0x0D",
    data=h("0D 01 08 00 7F 00 00 01 F4 1C 00 00"),
    fields=[
        F("ID", 0, 1, "yellow", "0x0D"),
        F("FLG", 1, 1, "pink", "E=1, M=0"),
        F("LEN", 2, 2, "blue", "8"),
        F("address", 4, 4, "green", "127.0.0.1"),
        F("port", 8, 4, "teal", "7412 (0x1CF4)"),
    ],
    flags=["E=1", "M=0"],
    notes=[
        "compact UDP/IPv4 locator",
        "M=1 adds a multicast address/port pair",
    ],
    subtitle="12 B | every row is 4 bytes",
))

add("fig16-pad-structure.png", Spec(
    name="PAD",
    sub_id="0x01",
    data=h("01 01 04 00 00 00 00 00"),
    fields=[
        F("ID", 0, 1, "yellow", "0x01"),
        F("FLG", 1, 1, "pink", "E=1"),
        F("LEN", 2, 2, "blue", "4"),
        F("padding", 4, 4, "gray", "ignored"),
    ],
    flags=["E=1"],
    notes=[
        "used to align the next submessage to a 32-bit boundary",
        "LEN=0: next header starts immediately (PAD special case)",
    ],
    subtitle="8 B | every row is 4 bytes",
))

def main():
    FIG.mkdir(parents=True, exist_ok=True)
    for filename, spec in SPECS:
        render_structure(spec, FIG / filename)


if __name__ == "__main__":
    main()

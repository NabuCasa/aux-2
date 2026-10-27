"""Compare a rebuilt unsigned app image with the published signed one.

Usage: compare_app.py <rebuilt firmware.ota.bin> <published signed ota.bin>

The signed image is the unsigned image followed by the signature sector, so
the rebuilt image should match the start of it byte for byte except where the
build time is embedded (and the image hash that covers it).
"""

import struct
import sys


def app_desc(image: bytes) -> dict[str, str]:
    # esp_app_desc_t follows the 24-byte image header and the 8-byte header
    # of the first segment
    off = 0x20
    magic, secure_version = struct.unpack_from("<II", image, off)
    fields = struct.unpack_from("<8x32s32s16s16s32s32s", image, off)
    names = ("version", "project_name", "time", "date", "idf_ver", "app_elf_sha256")
    desc = {"magic": hex(magic), "secure_version": str(secure_version)}
    for name, raw in zip(names, fields):
        desc[name] = raw.hex() if name == "app_elf_sha256" else raw.split(b"\0")[0].decode()
    return desc


def diff_ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = None
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y and start is None:
            start = i
        elif x == y and start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, min(len(a), len(b))))
    return ranges


def main() -> None:
    rebuilt = open(sys.argv[1], "rb").read()
    published = open(sys.argv[2], "rb").read()
    print(f"rebuilt {len(rebuilt)} bytes, published (signed) {len(published)} bytes")
    if len(rebuilt) > len(published):
        print("REBUILT IS LARGER THAN PUBLISHED: inputs differ")
    ranges = diff_ranges(rebuilt, published[: len(rebuilt)])
    differing = sum(end - start for start, end in ranges)
    print(f"differing bytes: {differing} in {len(ranges)} range(s)")
    for start, end in ranges[:20]:
        print(f"  0x{start:06x}-0x{end:06x} ({end - start} bytes)")
    a, b = app_desc(rebuilt), app_desc(published)
    for key in a:
        mark = "  " if a[key] == b[key] else "!="
        print(f"{mark} {key:15} rebuilt={a[key]}  published={b[key]}")


if __name__ == "__main__":
    main()

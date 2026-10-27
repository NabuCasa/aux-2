"""Check that a rebuilt app holds the same text as the published one.

Usage: verify_strings.py <rebuilt firmware.ota.bin> <published signed ota.bin>

Byte offsets differ between the two because ESP-IDF embeds source paths with
a prefix that depends on the build directory ("/./" in CI, "/../" locally),
which shifts everything after them. So compare the NUL-terminated text
strings instead, with that prefix and the embedded build time normalized. Any
change in ESPHome, a component or a library version shows up as a differing
log, version or format string.

Exits 0 when the only differences are strings split differently by a shifted
neighbouring byte (same message text present in both), 1 otherwise.
"""

from collections import Counter
import re
import sys

PATH_PREFIX = re.compile(rb"^(/\.\./|/\./|\./build/|\.\./|\./|/)")
BUILD_TIME = re.compile(rb"20\d\d-\d\d-\d\d \d\d:\d\d:\d\d [+-]\d{4}")
STRING = re.compile(rb"(?<=\x00)([ -~\n\t]{8,})(?=\x00)")


def texts(image: bytes) -> Counter[bytes]:
    found: Counter[bytes] = Counter()
    for match in STRING.finditer(image):
        text = match.group(1)
        # Address constants can look printable; real text has a word in it
        if not re.search(rb"[a-z]{3}", text):
            continue
        text = BUILD_TIME.sub(b"<BUILD TIME>", PATH_PREFIX.sub(b"", text))
        found[text] += 1
    return found


def main() -> int:
    rebuilt = open(sys.argv[1], "rb").read()
    published = open(sys.argv[2], "rb").read()
    a, b = texts(rebuilt), texts(published)
    only_rebuilt, only_published = a - b, b - a
    print(f"text strings: rebuilt={sum(a.values())} published={sum(b.values())}")
    print(f"only in rebuilt={sum(only_rebuilt.values())} only in published={sum(only_published.values())}")
    unexplained = []
    for text in only_rebuilt:
        # A string merged with or split from its neighbour still has the same tail
        tail = text.split(b": ")[-1].rstrip(b" ")
        if len(tail) < 8 or published.count(tail) != rebuilt.count(tail):
            unexplained.append(text)
    for text in unexplained:
        print("  UNEXPLAINED:", text[:160])
    print("RESULT:", "MATCH" if not unexplained else "MISMATCH")
    return 0 if not unexplained else 1


if __name__ == "__main__":
    sys.exit(main())

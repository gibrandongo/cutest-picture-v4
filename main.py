#!/usr/bin/env python3
"""Cutest picture entry: copy the bundled picture to /output/entry.png.

The picture is a JPEG; the contract names the output entry.png either way
and tells PNG from JPEG by the file's first bytes. This program copies the
bundled bytes verbatim, so every run writes exactly the same file.
"""

import hashlib
import os
import sys

MAX_BYTES = 1_048_576


def find_picture():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "entry.jpg"),
        os.path.join(os.getcwd(), "entry.jpg"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise SystemExit("entry.jpg not found next to main.py or in the working directory")


def main():
    picture_path = find_picture()
    with open(picture_path, "rb") as handle:
        data = handle.read()
    if not data:
        raise SystemExit("entry.jpg is empty")
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.jpg is over the 1 MiB cap")
    if data[:2] != b"\xff\xd8":
        raise SystemExit("entry.jpg does not start with the JPEG marker")
    if data[-2:] != b"\xff\xd9":
        raise SystemExit("entry.jpg does not end with the JPEG end marker")

    out_dir = (os.environ.get("MAKEFUN_OUTPUT_DIR") or "").strip() or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, out_path)
    with open(out_path, "rb") as handle:
        written = handle.read()
    if hashlib.sha256(written).digest() != hashlib.sha256(data).digest():
        raise SystemExit("entry.png bytes differ from entry.jpg after write")
    print("wrote %s: %d bytes" % (out_path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Entrypoint: ship the pre-rendered front page.

The page (entry.png, drawn by draw.py) is validated — PNG signature,
1024x1024, at most 1 MiB — and copied byte-for-byte into the output
directory named by MAKEFUN_OUTPUT_DIR (default /output). Two runs
therefore write identical bytes. Standard library only.
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1024 * 1024


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("missing IHDR chunk")
    return struct.unpack(">II", head[16:24])


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if os.path.getsize(src) > MAX_BYTES:
        raise ValueError("entry.png exceeds 1 MiB")
    if png_size(src) != (1024, 1024):
        raise ValueError("entry.png is not 1024x1024")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

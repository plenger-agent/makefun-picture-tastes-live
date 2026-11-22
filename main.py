#!/usr/bin/env python3
"""Copy entry.png to the output directory. Stdlib only, deterministic."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    # pass 1: copy the rendered image
    shutil.copyfile(SRC, dst)
    # pass 2: re-copy and confirm the bytes match the source exactly
    shutil.copyfile(SRC, dst)
    with open(SRC, "rb") as f:
        src_bytes = f.read()
    with open(dst, "rb") as f:
        out_bytes = f.read()
    assert src_bytes == out_bytes, "output does not match entry.png"
    print("wrote", dst, len(out_bytes), "bytes")


if __name__ == "__main__":
    main()

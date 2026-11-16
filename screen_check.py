#!/usr/bin/env python3
"""Analyse QEMU screendumps (PPM). Converts to PNG for artifacts and applies HEURISTIC checks.
 - early: a frame was captured and is not entirely black (firmware/bootloader drew something)
 - final: not blank/uniform and different from early frame (system progressed past the boot menu)
HEURISTIC ONLY: a human must look at final.png to confirm a real desktop/login screen."""
import sys, struct, zlib, os
def read_ppm(p):
    d = open(p, "rb").read(); parts = d.split(None, 4)
    assert parts[0] == b"P6", "not P6 PPM"
    w, h = int(parts[1]), int(parts[2]); hdr = len(d) - len(parts[4]) if len(parts) > 4 else 0
    # header ends after the maxval token + a single whitespace
    idx = 0; tok = 0; i = 0
    while tok < 4:
        while d[i:i+1].isspace(): i += 1
        while not d[i:i+1].isspace(): i += 1
        tok += 1
    i += 1
    return w, h, d[i:i + w * h * 3]
def to_png(path, w, h, px):
    def ch(t, b): c = struct.pack(">I", len(b)) + t + b; return c + struct.pack(">I", zlib.crc32(t + b) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + px[y*w*3:(y+1)*w*3] for y in range(h))
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw, 6)) + ch(b"IEND", b""))
def stats(px):
    step = 3 * 7; s = px[::step]; n = max(1, len(px) // step)
    sample = [px[i:i+3] for i in range(0, len(px) - 2, step)]
    nonblack = sum(1 for c in sample if max(c) > 12) / max(1, len(sample))
    colors = len({(c[0] >> 3, c[1] >> 3, c[2] >> 3) for c in sample})
    return nonblack, colors, sample
def main(early, final):
    ok = True
    try:
        w, h, e = read_ppm(early); nb, cl, es = stats(e); to_png(early[:-4] + ".png", w, h, e)
        r = nb > 0.001
        print(("PASS" if r else "FAIL") + f": early frame has content (nonblack={nb:.3f}, colors={cl}) [heuristic]"); ok &= r
        w, h, f = read_ppm(final); nb2, cl2, fs = stats(f); to_png(final[:-4] + ".png", w, h, f)
        r = nb2 > 0.02 and cl2 > 12
        print(("PASS" if r else "FAIL") + f": final frame not blank/uniform (nonblack={nb2:.3f}, colors={cl2}) [heuristic]"); ok &= r
        diff = sum(1 for a, b in zip(es, fs) if a != b) / max(1, min(len(es), len(fs)))
        r = diff > 0.05
        print(("PASS" if r else "FAIL") + f": screen changed between early and final (diff={diff:.3f}) [heuristic]"); ok &= r
    except Exception as ex:
        print(f"FAIL: could not analyse screendumps: {ex}"); ok = False
    print("NOTE: open final.png from the artifact to confirm visually; this is not proof of a working desktop.")
    return 0 if ok else 1
if __name__ == "__main__": sys.exit(main(sys.argv[1], sys.argv[2]))

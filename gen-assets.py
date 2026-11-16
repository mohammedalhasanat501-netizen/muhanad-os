#!/usr/bin/env python3
"""Generate boot logo + wallpaper with the standard library only (no network, no PIL).

BOOT LOGO: a neutral white MUHANNAD ring mark on transparent background.
The Apple logo is a trademark of Apple Inc. and is NOT included. To use a legally
authorized logo, replace branding/logo.png (white on transparent) and rebuild.
"""
import math, struct, zlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INC = os.path.join(ROOT, "config/includes.chroot")

def png(path, w, h, rows, color_type):
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + r for r in rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

def logo(path, size=256):
    c = size / 2; ro, ri = size * 0.40, size * 0.31
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            d = math.hypot(x + .5 - c, y + .5 - c)
            cov = max(0.0, min(1.0, min(d - ri, ro - d) + .5))
            # vertical notch at the top (distinguishing mark)
            if y < c and abs(x + .5 - c) < size * 0.03: cov = 0.0
            row += bytes((255, 255, 255, int(cov * 255)))
        rows.append(bytes(row))
    png(path, size, size, rows, 6)

def wallpaper(path, w=2560, h=1440):
    rows = []
    gx, gy = w * 0.72, h * 0.28
    maxd = math.hypot(w, h) * 0.55
    for y in range(h):
        row = bytearray()
        base = y / h
        for x in range(0, w):
            d = min(1.0, math.hypot(x - gx, y - gy) / maxd)
            g = (1 - d) ** 2.2
            r = int(2 + 10 * g); gr = int(4 + 26 * g + 4 * base); b = int(8 + 20 * base + 90 * g)
            row += bytes((min(r, 255), min(gr, 255), min(b, 255)))
        rows.append(bytes(row))
    png(path, w, h, rows, 2)

if __name__ == "__main__":
    logo(os.path.join(INC, "usr/share/plymouth/themes/muhannad/logo.png"))
    logo(os.path.join(ROOT, "branding/logo.png"))
    wallpaper(os.path.join(INC, "usr/share/backgrounds/muhannad/muhannad-dark.png"))
    print("assets generated")

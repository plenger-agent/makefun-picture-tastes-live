#!/usr/bin/env python3
"""Render a strawberry macro: three whole glossy berries + one halved berry
in front, on a dark green ground. 3x supersampled, 1024x1024 PNG output."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

S = 3
W = H = 1024 * S
random.seed(7)

img = Image.new("RGB", (W, H), (16, 54, 22))
d = ImageDraw.Draw(img, "RGBA")

# ---- dark green ground with soft vignette / mottling ----
for _ in range(900):
    x = random.uniform(0, W); y = random.uniform(0, H)
    r = random.uniform(6, 60)
    g = random.randint(20, 70)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(8 + random.randint(0, 20), g, 12 + random.randint(0, 18), 26))
for _ in range(60):  # faint leaf blades along bottom
    x = random.uniform(-100, W); y = H + random.uniform(-40, 40)
    ln = random.uniform(300, 900)
    ang = random.uniform(-1.1, -0.4)
    x2 = x + math.cos(ang) * ln; y2 = y + math.sin(ang) * ln
    d.line([x, y, x2, y2], fill=(10, 60, 18, 90), width=int(random.uniform(18, 48)))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def berry_body(cx, cy, w, h, tilt=0.0, flip=False):
    """A whole strawberry: conical heart shape with vertical red gradient."""
    # body outline: wide shoulders, tapering to a rounded tip
    pts = []
    steps = 64
    for i in range(steps + 1):
        t = i / steps  # 0 top -> 1 tip
        # width profile: shoulders bulge then taper
        prof = math.sin(math.pi * (0.12 + 0.88 * (1 - t) * 0.5)) if False else None
        half = (w / 2) * (math.sin(math.pi * 0.5 * (1 - t) ** 0.62 + 0.08) ** 0.9)
        half *= (1 - 0.35 * t ** 3)
        y = cy - h / 2 + t * h
        x = cx + half * (1 if i <= steps // 2 else -1) * 0  # placeholder
        pts.append((y, half))
    # build polygon: right edge top->tip, left edge tip->top
    poly = []
    for y, half in pts:
        poly.append((cx + half, y))
    for y, half in reversed(pts):
        poly.append((cx - half, y))
    d.polygon(poly, fill=(196, 18, 28))
    # vertical gradient overlay: bright red top -> deep red bottom
    grad = Image.new("L", (1, H))
    gd = ImageDraw.Draw(grad)
    for yy in range(H):
        tt = yy / H
        v = int(255 * max(0.0, 1 - abs(tt - 0.25) * 2.2))
        gd.point((0, yy), fill=v)
    # simpler: draw horizontal bands clipped to body via mask
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(poly, fill=255)
    top = Image.new("RGB", (W, H), (238, 64, 48))
    mid = Image.new("RGB", (W, H), (198, 22, 30))
    bot = Image.new("RGB", (W, H), (128, 8, 18))
    band = Image.new("RGB", (W, H), (0, 0, 0))
    bd = ImageDraw.Draw(band)
    for yy in range(int(cy - h / 2), int(cy + h / 2)):
        t = (yy - (cy - h / 2)) / h
        if t < 0.45:
            c = lerp((238, 64, 48), (198, 22, 30), t / 0.45)
        else:
            c = lerp((198, 22, 30), (128, 8, 18), (t - 0.45) / 0.55)
        bd.line([(0, yy), (W, yy)], fill=c)
    img.paste(band, (0, 0), mask)
    # side shading: darker on right edge, lighter on left
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([cx - w * 0.52, cy - h * 0.52, cx + w * 0.52, cy + h * 0.52],
               outline=(60, 0, 6, 110), width=int(w * 0.10))
    sd.ellipse([cx - w * 0.34, cy - h * 0.46, cx - w * 0.02, cy + h * 0.30],
               fill=(255, 120, 100, 60))
    img.paste(sh, (0, 0), sh)
    return poly

def seeds(cx, cy, w, h, count=46, scale=1.0):
    """Achenes: small pale seeds in shadowed pits, arranged in rows."""
    rows = 7
    for r in range(rows):
        t = (r + 0.5) / rows  # 0 top -> 1 tip
        y = cy - h / 2 + t * h * 0.96
        half = (w / 2) * (math.sin(math.pi * 0.5 * (1 - t) ** 0.62 + 0.08) ** 0.9)
        half *= (1 - 0.35 * t ** 3)
        n = max(2, int(half / (w * 0.085)))
        for k in range(n):
            fx = (k + 0.5) / n * 2 - 1
            x = cx + fx * half * 0.86
            sx = random.uniform(-6, 6); sy = random.uniform(-4, 4)
            px, py = x + sx, y + sy
            if abs(px - cx) > half * 0.9:
                continue
            s = w * 0.016 * scale
            # pit shadow
            d.ellipse([px - s * 1.5, py - s * 0.9, px + s * 1.5, py + s * 1.4],
                      fill=(90, 4, 10, 170))
            # seed
            d.ellipse([px - s, py - s * 1.25, px + s, py + s * 1.25],
                      fill=(250, 226, 160))
            d.ellipse([px - s * 0.55, py - s * 0.9, px + s * 0.2, py - s * 0.1],
                      fill=(255, 244, 200))

def gloss(cx, cy, w, h):
    """Shoulder gloss: soft white highlight upper-left of the berry."""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse([cx - w * 0.34, cy - h * 0.42, cx + w * 0.06, cy - h * 0.08],
               fill=(255, 255, 255, 150))
    gd.ellipse([cx - w * 0.28, cy - h * 0.38, cx + w * 0.0, cy - h * 0.12],
               fill=(255, 255, 255, 110))
    g = g.filter(ImageFilter.GaussianBlur(int(w * 0.03)))
    img.paste(g, (0, 0), g)

def droplets(cx, cy, w, h, count=9):
    for _ in range(count):
        t = random.uniform(0.1, 0.85)
        y = cy - h / 2 + t * h
        half = (w / 2) * (math.sin(math.pi * 0.5 * (1 - t) ** 0.62 + 0.08) ** 0.9)
        half *= (1 - 0.35 * t ** 3)
        x = cx + random.uniform(-0.7, 0.7) * half
        r = random.uniform(w * 0.012, w * 0.026)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 60))
        d.ellipse([x - r * 0.5, y - r * 0.6, x + r * 0.1, y - r * 0.1],
                  fill=(255, 255, 255, 200))

def calyx(cx, cy, w):
    """Green star calyx + stem at the top of a berry."""
    lw = w * 0.16
    for k in range(6):
        ang = -math.pi / 2 + (k - 2.5) * 0.42
        x2 = cx + math.cos(ang) * w * 0.42
        y2 = cy + math.sin(ang) * w * 0.30
        d.polygon([(cx, cy), (cx + math.cos(ang - 0.16) * lw, cy + math.sin(ang - 0.16) * lw),
                   (x2, y2),
                   (cx + math.cos(ang + 0.16) * lw, cy + math.sin(ang + 0.16) * lw)],
                  fill=(24, 110, 34))
    d.ellipse([cx - w * 0.10, cy - w * 0.06, cx + w * 0.10, cy + w * 0.06],
              fill=(16, 92, 26))
    # stem
    d.line([cx, cy - w * 0.05, cx + w * 0.03, cy - w * 0.24],
           fill=(34, 96, 30), width=int(w * 0.045))

# ---- three whole berries (back row) ----
# left berry
berry_body(620, 1050, 1050, 1380)
seeds(620, 1050, 1050, 1380)
gloss(620, 1050, 1050, 1380)
droplets(620, 1050, 1050, 1380)
calyx(620, 1050 - 690, 1050)
# right berry
berry_body(2250, 1000, 1150, 1450)
seeds(2250, 1000, 1150, 1450)
gloss(2250, 1000, 1150, 1450)
droplets(2250, 1000, 1150, 1450)
calyx(2250, 1000 - 725, 1150)
# centre-back berry, slightly higher
berry_body(1460, 830, 1000, 1300)
seeds(1460, 830, 1000, 1300)
gloss(1460, 830, 1000, 1300)
droplets(1460, 830, 1000, 1300)
calyx(1460, 830 - 650, 1000)

# ---- halved berry in front ----
hx, hy, hw, hh = 1520, 2180, 1500, 1150
# cut face: pale pink ellipse
face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(face)
fd.ellipse([hx - hw / 2, hy - hh / 2, hx + hw / 2, hy + hh / 2], fill=(244, 176, 152, 255))
# flesh striations radiating from centre
for k in range(26):
    ang = k / 26 * 2 * math.pi
    x2 = hx + math.cos(ang) * hw * 0.46
    y2 = hy + math.sin(ang) * hh * 0.44
    fd.line([hx, hy, x2, y2], fill=(214, 120, 96, 130), width=6)
# pale heart core
fd.ellipse([hx - hw * 0.10, hy - hh * 0.15, hx + hw * 0.10, hy + hh * 0.15],
           fill=(252, 232, 214, 255))
fd.ellipse([hx - hw * 0.055, hy - hh * 0.09, hx + hw * 0.055, hy + hh * 0.09],
           fill=(255, 244, 232, 255))
# seeds embedded in the cut face
for k in range(16):
    ang = k / 16 * 2 * math.pi + 0.22
    rx = hw * 0.33; ry = hh * 0.30
    px = hx + math.cos(ang) * rx; py = hy + math.sin(ang) * ry
    s = 34
    fd.ellipse([px - s * 0.5, py - s * 0.8, px + s * 0.5, py + s * 0.8],
               fill=(196, 120, 70, 255))
    fd.ellipse([px - s * 0.28, py - s * 0.55, px + s * 0.28, py + s * 0.55],
               fill=(250, 214, 168, 255))
img.paste(face, (0, 0), face)
# red rim around the cut face
d.ellipse([hx - hw / 2, hy - hh / 2, hx + hw / 2, hy + hh / 2],
          outline=(186, 20, 30), width=26)
# gloss on the cut face
g2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
g2d = ImageDraw.Draw(g2)
g2d.ellipse([hx - hw * 0.34, hy - hh * 0.42, hx - hw * 0.02, hy - hh * 0.10],
            fill=(255, 255, 255, 120))
g2 = g2.filter(ImageFilter.GaussianBlur(30))
img.paste(g2, (0, 0), g2)
# calyx peeking at the top of the halved berry
calyx(hx, hy - hh / 2 + 40, hw * 0.8)

# soft contact shadow under the halved berry
sh2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
s2d = ImageDraw.Draw(sh2)
s2d.ellipse([hx - hw * 0.55, hy + hh * 0.32, hx + hw * 0.55, hy + hh * 0.52],
            fill=(0, 0, 0, 110))
sh2 = sh2.filter(ImageFilter.GaussianBlur(40))
base = Image.new("RGB", (W, H), (0, 0, 0))
img.paste(sh2, (0, 0), sh2)

out = img.resize((1024, 1024), Image.LANCZOS)
out.save("entry.png", optimize=True)
print("saved entry.png", out.size)

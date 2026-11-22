#!/usr/bin/env python3
"""Fresh render of a strawberry macro: three whole glossy berries plus one
halved berry in the foreground, on a dark green ground. Supersampled 3x and
downscaled to a 1024x1024 PNG. No text anywhere in the image."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

SS = 3
SIZE = 1024 * SS
rng = random.Random(20261123)

canvas = Image.new("RGB", (SIZE, SIZE), (14, 48, 20))
pen = ImageDraw.Draw(canvas, "RGBA")


def mix(c1, c2, t):
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ---------- dark green ground ----------
for _ in range(1100):
    x = rng.uniform(0, SIZE)
    y = rng.uniform(0, SIZE)
    r = rng.uniform(8, 70)
    pen.ellipse([x - r, y - r, x + r, y + r],
                fill=(rng.randint(6, 26), rng.randint(22, 72),
                      rng.randint(10, 30), 24))
for _ in range(70):
    x = rng.uniform(-80, SIZE)
    y = SIZE + rng.uniform(-30, 60)
    length = rng.uniform(350, 950)
    ang = rng.uniform(-1.05, -0.45)
    pen.line([x, y, x + math.cos(ang) * length, y + math.sin(ang) * length],
             fill=(12, 64, 20, 85), width=int(rng.uniform(20, 52)))


def half_width(t):
    """Berry width profile: t=0 at the shoulders, t=1 at the tip."""
    return (math.sin(math.pi * 0.5 * (1 - t) ** 0.6 + 0.07) ** 0.85) * (1 - 0.38 * t ** 3)


def outline(cx, cy, w, h):
    """Closed polygon of a strawberry body."""
    pts = []
    n = 72
    for i in range(n + 1):
        t = i / n
        pts.append((cx + half_width(t) * w / 2, cy - h / 2 + t * h))
    for i in range(n, -1, -1):
        t = i / n
        pts.append((cx - half_width(t) * w / 2, cy - h / 2 + t * h))
    return pts


def whole_berry(cx, cy, w, h):
    poly = outline(cx, cy, w, h)
    # red body: horizontal gradient bands clipped to the body mask
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    bands = Image.new("RGB", (SIZE, SIZE))
    bd = ImageDraw.Draw(bands)
    top_y, bot_y = int(cy - h / 2), int(cy + h / 2)
    for yy in range(top_y, bot_y + 1):
        t = (yy - top_y) / h
        if t < 0.42:
            col = mix((240, 66, 50), (200, 22, 32), t / 0.42)
        else:
            col = mix((200, 22, 32), (126, 8, 18), (t - 0.42) / 0.58)
        bd.line([(0, yy), (SIZE, yy)], fill=col)
    canvas.paste(bands, (0, 0), mask)
    # soft side shading: warm light left, deep shadow right
    shade = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.ellipse([cx - w * 0.52, cy - h * 0.52, cx + w * 0.52, cy + h * 0.52],
               outline=(70, 0, 8, 105), width=int(w * 0.09))
    sd.ellipse([cx - w * 0.36, cy - h * 0.44, cx - w * 0.04, cy + h * 0.28],
               fill=(255, 118, 96, 55))
    canvas.paste(shade, (0, 0), shade)
    # achenes: golden-angle scatter inside the body, each in a pit shadow
    golden = math.pi * (3 - math.sqrt(5))
    for k in range(64):
        t = 0.06 + 0.88 * (k / 64) ** 0.9
        ang = k * golden
        reach = half_width(t) * w / 2 * 0.86
        px = cx + math.cos(ang) * reach * rng.uniform(0.55, 1.0)
        py = cy - h / 2 + t * h + rng.uniform(-8, 8)
        if abs(px - cx) > half_width(t) * w / 2 * 0.9:
            continue
        s = w * 0.017
        pen.ellipse([px - s * 1.6, py - s, px + s * 1.6, py + s * 1.5],
                    fill=(96, 4, 12, 175))
        pen.ellipse([px - s, py - s * 1.3, px + s, py + s * 1.3],
                    fill=(251, 228, 162))
        pen.ellipse([px - s * 0.5, py - s * 0.95, px + s * 0.25, py - s * 0.15],
                    fill=(255, 245, 202))
    # shoulder gloss
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - w * 0.36, cy - h * 0.44, cx + w * 0.04, cy - h * 0.10],
               fill=(255, 255, 255, 150))
    gd.ellipse([cx - w * 0.28, cy - h * 0.40, cx - w * 0.02, cy - h * 0.14],
               fill=(255, 255, 255, 105))
    glow = glow.filter(ImageFilter.GaussianBlur(int(w * 0.03)))
    canvas.paste(glow, (0, 0), glow)
    # water droplets
    for _ in range(10):
        t = rng.uniform(0.12, 0.85)
        y = cy - h / 2 + t * h
        x = cx + rng.uniform(-0.65, 0.65) * half_width(t) * w / 2
        r = rng.uniform(w * 0.013, w * 0.027)
        pen.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 55))
        pen.ellipse([x - r * 0.55, y - r * 0.65, x + r * 0.1, y - r * 0.1],
                    fill=(255, 255, 255, 205))
    # green calyx star + stem
    top = cy - h / 2
    leaf_w = w * 0.15
    for k in range(6):
        ang = -math.pi / 2 + (k - 2.5) * 0.44
        tip = (cx + math.cos(ang) * w * 0.44, top + math.sin(ang) * w * 0.32)
        pen.polygon([(cx, top),
                     (cx + math.cos(ang - 0.17) * leaf_w,
                      top + math.sin(ang - 0.17) * leaf_w),
                     tip,
                     (cx + math.cos(ang + 0.17) * leaf_w,
                      top + math.sin(ang + 0.17) * leaf_w)],
                    fill=(26, 112, 36))
    pen.ellipse([cx - w * 0.10, top - w * 0.06, cx + w * 0.10, top + w * 0.06],
                fill=(18, 94, 28))
    pen.line([cx, top - w * 0.04, cx + w * 0.03, top - w * 0.26],
             fill=(36, 98, 32), width=int(w * 0.05))


def halved_berry(cx, cy, w, h):
    # contact shadow first, under the fruit
    sh = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [cx - w * 0.56, cy + h * 0.30, cx + w * 0.56, cy + h * 0.52],
        fill=(0, 0, 0, 115))
    sh = sh.filter(ImageFilter.GaussianBlur(42))
    canvas.paste(sh, (0, 0), sh)
    # cut face
    face = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    fd.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
               fill=(245, 178, 154, 255))
    for k in range(28):
        ang = k / 28 * 2 * math.pi
        fd.line([cx, cy,
                 cx + math.cos(ang) * w * 0.46,
                 cy + math.sin(ang) * h * 0.44],
                fill=(216, 122, 98, 130), width=6)
    fd.ellipse([cx - w * 0.105, cy - h * 0.15, cx + w * 0.105, cy + h * 0.15],
               fill=(252, 233, 215, 255))
    fd.ellipse([cx - w * 0.058, cy - h * 0.09, cx + w * 0.058, cy + h * 0.09],
               fill=(255, 245, 233, 255))
    for k in range(16):
        ang = k / 16 * 2 * math.pi + 0.2
        px = cx + math.cos(ang) * w * 0.33
        py = cy + math.sin(ang) * h * 0.30
        s = 36
        fd.ellipse([px - s * 0.5, py - s * 0.8, px + s * 0.5, py + s * 0.8],
                   fill=(198, 122, 72, 255))
        fd.ellipse([px - s * 0.28, py - s * 0.55, px + s * 0.28, py + s * 0.55],
                   fill=(251, 215, 170, 255))
    canvas.paste(face, (0, 0), face)
    pen.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                outline=(188, 20, 30), width=28)
    sheen = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(sheen).ellipse(
        [cx - w * 0.34, cy - h * 0.42, cx - w * 0.02, cy - h * 0.10],
        fill=(255, 255, 255, 120))
    sheen = sheen.filter(ImageFilter.GaussianBlur(32))
    canvas.paste(sheen, (0, 0), sheen)


# ---------- composition: three whole berries, halved one in front ----------
whole_berry(600, 1020, 1060, 1400)    # left
whole_berry(2280, 990, 1160, 1460)    # right
whole_berry(1450, 820, 1010, 1310)    # centre back
halved_berry(1520, 2190, 1520, 1160)  # foreground, cut face up

final = canvas.resize((1024, 1024), Image.LANCZOS)
final.save("entry.png", optimize=True)
print("saved entry.png", final.size)

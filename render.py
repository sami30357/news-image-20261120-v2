#!/usr/bin/env python3
"""Render the V3 front page for news-image-20261120: 'The Friday Edition'.

40 verified Friday 20 November 2026 stories on one 1024x1024 page.
Drawn entirely with PIL primitives — every panel is an original drawing.
V3 vs V2: taller heroes + in-panel headline chips, denser mid panels with
label chips, bigger headlines, cream map, proportional region bar,
RECORDS OF THE DAY strip (the one thing no leader has).
Run: python3 render.py  (writes entry.png next to this file)
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 243, 232)
PAPER = (250, 247, 238)
NAVY = (20, 38, 74)
NAVY_D = (13, 27, 51)
GOLD = (201, 162, 39)
GOLD_L = (232, 197, 94)
RED = (176, 42, 42)
RED_D = (140, 28, 28)
INK = (24, 24, 24)
GREY = (110, 110, 105)
GREY_L = (210, 206, 194)
BLUE = (52, 96, 148)
SKY = (168, 205, 225)
TAN = (214, 196, 158)
GREEN = (46, 110, 72)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def F(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = FL + "LiberationSerif-Bold.ttf"
SERIF = FL + "LiberationSerif-Regular.ttf"
SERIF_I = FL + "LiberationSerif-Italic.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"


def wrap(d, text, font, maxw):
    """Greedy word wrap by pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(d, x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def para(d, x, y, s, font, maxw, fill=INK, leading=None):
    """Draw wrapped paragraph; returns y after the last line."""
    lh = leading or int(font.size * 1.22)
    for line in wrap(d, s, font, maxw):
        d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def one_line(d, s, font, maxw):
    """Truncate to a single line with an ellipsis if it overflows."""
    while d.textlength(s, font=font) > maxw and " " in s:
        s = s.rsplit(" ", 1)[0] + "…"
    return s


def rrect(d, box, fill=None, outline=None, width=1, radius=3):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def burst(d, cx, cy, r, color, spikes=10):
    """Starburst: alternating outer/inner points."""
    pts = []
    for i in range(spikes * 2):
        ang = math.pi * i / spikes - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


def dashed(d, pts, fill, width=2, dash=6):
    """Dashed polyline through pts."""
    for a, b in zip(pts, pts[1:]):
        x0, y0 = a
        x1, y1 = b
        dist = math.hypot(x1 - x0, y1 - y0)
        if dist == 0:
            continue
        n = max(1, int(dist / dash))
        for i in range(n):
            if i % 2 == 0:
                t0, t1 = i / n, (i + 1) / n
                d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                        (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                       fill=fill, width=width)


def tag(d, x, y, s, font, bg, fg=WHITE):
    """Small filled label; returns width used."""
    w = int(d.textlength(s, font=font)) + 10
    h = font.size + 6
    rrect(d, [x, y, x + w, y + h], fill=bg, radius=2)
    d.text((x + 5, y + 3), s, font=font, fill=fg)
    return w


def panel_chip(d, x, y, s, font, bg=RED, fg=WHITE):
    """Bold label chip drawn ON a panel; returns (width, height)."""
    w = int(d.textlength(s, font=font)) + 12
    h = font.size + 8
    d.rectangle([x, y, x + w, y + h], fill=bg)
    d.text((x + 6, y + 4), s, font=font, fill=fg)
    return w, h


def rule(d, x0, y, x1, color=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def segbar(d, x, y, w, h, regions):
    """Proportional region bar: adjacent coloured blocks, white labels inside."""
    total = sum(n for _, n, _ in regions)
    widths = [max(55, int(n / total * w)) for _, n, _ in regions]
    over = sum(widths) - w
    order = sorted(range(len(widths)), key=lambda i: -widths[i])
    i = 0
    while over > 0:
        j = order[i % len(order)]
        if widths[j] > 60:
            widths[j] -= 1
            over -= 1
        i += 1
    cx = x
    f = F(SANS_B, 8)
    for (label, num, col), bw in zip(regions, widths):
        d.rectangle([cx, y, cx + bw, y + h], fill=col)
        s = f"{label} {num}"
        tw = int(d.textlength(s, font=f))
        if tw + 6 <= bw:
            d.text((cx + (bw - tw) / 2, y + 4), s, font=f, fill=WHITE)
        cx += bw


# ---------------------------------------------------------------- heroes
def panel_kyiv(d, x, y, w, h):
    """Night skyline, bridge over the Dnipro, missile trails, blasts."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY_D)
    for i in range(38):  # stars
        sx = x + (i * 53) % w
        sy = y + (i * 29) % (h // 2)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 210, 230))
    # skyline
    for bx, bw, bh in [(6, 26, 34), (36, 18, 46), (58, 30, 28), (92, 16, 40),
                       (112, 24, 52), (140, 20, 36), (164, 28, 44), (196, 22, 30),
                       (222, 18, 38), (240, 6, 26)]:
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26], fill=(8, 16, 32))
        for wy in range(3):
            for wx in range(bw // 9):
                if (bx + wy + wx) % 3 == 0:
                    d.rectangle([x + bx + 4 + wx * 9, y + h - 22 - bh + wy * 10,
                                 x + bx + 7 + wx * 9, y + h - 19 - bh + wy * 10],
                                fill=(232, 197, 94))
    # river + bridge
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(28, 58, 96))
    for ax in (28, 92, 156):
        d.arc([x + ax, y + h - 44, x + ax + 56, y + h - 4], 180, 360, fill=GOLD_L, width=3)
    d.line([(x, y + h - 26), (x + w, y + h - 26)], fill=GOLD_L, width=2)
    # missile trails (dashed arcs from sky)
    dashed(d, [(x + 30, y + 4), (x + 55, y + 26), (x + 72, y + 52)], fill=(255, 220, 150), width=2)
    dashed(d, [(x + 150, y + 2), (x + 140, y + 30), (x + 128, y + 58)], fill=(255, 220, 150), width=2)
    dashed(d, [(x + 215, y + 6), (x + 205, y + 28), (x + 198, y + 50)], fill=(255, 220, 150), width=2)
    # blasts on the bridge
    burst(d, x + 72, y + h - 30, 13, (230, 120, 30), 9)
    burst(d, x + 72, y + h - 30, 7, (255, 220, 120), 9)
    burst(d, x + 130, y + h - 28, 9, (230, 120, 30), 9)
    burst(d, x + 130, y + h - 28, 5, (255, 220, 120), 9)
    burst(d, x + 198, y + h - 34, 10, (230, 120, 30), 9)
    burst(d, x + 198, y + h - 34, 5, (255, 220, 120), 9)
    d.ellipse([x + 62, y + h - 52, x + 84, y + h - 38], fill=(90, 90, 95))


def panel_akvan(d, x, y, w, h):
    """Odisha coast map with the cyclone spiral and landfall track."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 224, 238))
    # land (east coast of India, schematic)
    land = [(x + 8, y + 6), (x + 78, y + 2), (x + 118, y + 14), (x + 108, y + 34),
            (x + 96, y + 52), (x + 104, y + 78), (x + 88, y + h - 4), (x + 30, y + h - 6),
            (x + 12, y + 66), (x + 22, y + 40), (x + 6, y + 22)]
    d.polygon(land, fill=TAN)
    d.line(land + [land[0]], fill=(120, 100, 70), width=1)
    d.text((x + 16, y + 72), "ODISHA", font=F(SANS_B, 9), fill=(90, 70, 40))
    d.text((x + 16, y + 84), "INDIA", font=F(SANS, 8), fill=(90, 70, 40))
    d.text((x + 176, y + 4), "BAY OF", font=F(SANS_B, 9), fill=BLUE)
    d.text((x + 176, y + 15), "BENGAL", font=F(SANS_B, 9), fill=BLUE)
    # cyclone spiral: concentric arcs
    cx, cy = x + 152, y + 70
    for r, col in [(40, (255, 255, 255)), (31, (90, 140, 190)), (22, (255, 255, 255)),
                   (13, (40, 90, 150))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    # dashed track from sea to landfall
    dashed(d, [(cx + 58, cy - 30), (cx + 22, cy - 10), (cx - 2, cy + 6)], fill=RED, width=2)
    d.ellipse([x + 96, y + 44, x + 104, y + 52], fill=RED)
    d.text((x + 92, y + 42), "GOPALPUR", font=F(SANS_B, 8), fill=RED_D, anchor="ra")
    # rain bands
    for rx, ry in [(x + 196, y + 88), (x + 210, y + 92), (x + 224, y + 86), (x + 236, y + 92),
                   (x + 240, y + 78), (x + 206, y + 100)]:
        d.line([(rx, ry), (rx - 4, ry + 8)], fill=(90, 140, 190), width=2)


def panel_ai(d, x, y, w, h):
    """Dark market panel: plunging chart plus index table."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 18, 24))
    # faint gridlines
    for gy in (y + 44, y + 62):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(48, 48, 58), width=1)
    pts = [(x + 12, y + 36), (x + 48, y + 42), (x + 84, y + 40), (x + 118, y + 50),
           (x + 152, y + 58), (x + 186, y + 66), (x + 218, y + 74)]
    d.line(pts, fill=(230, 60, 60), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 120, 120))
    d.line([(x + 8, y + h - 36), (x + w - 8, y + h - 36)], fill=(70, 70, 78), width=1)
    rows = [("TAIEX", "-6.2%"), ("NIKKEI", "-5.1%"), ("KOSPI", "-5.2%"), ("HANG SENG", "-1.9%")]
    # two-column index table along the bottom
    fy = y + h - 32
    for i, (name, val) in enumerate(rows):
        cx0 = x + 10 + (i % 2) * (w // 2)
        cy0 = fy + (i // 2) * 15
        d.text((cx0, cy0), name, font=F(SANS_B, 9), fill=(200, 200, 205))
        d.text((cx0 + 92, cy0), val, font=F(SANS_B, 9), fill=(255, 100, 100))
    d.text((x + w - 8, y + 8), "-6.2%", font=F(SANS_B, 22), fill=(255, 80, 80), anchor="ra")


def panel_mercury(d, x, y, w, h):
    """Black space, cratered Mercury, BepiColombo on approach."""
    d.rectangle([x, y, x + w, y + h], fill=BLACK)
    for i in range(30):
        sx = x + (i * 47) % w
        sy = y + (i * 31) % (h - 20)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(220, 220, 220))
    cx, cy, r = x + w - 82, y + h - 48, 52
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 162, 150))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 114, 102), width=2)
    for ox, oy, orr in [(-16, -12, 9), (10, -18, 6), (14, 8, 11), (-8, 14, 7), (22, -4, 5),
                        (26, 10, 6), (-22, 4, 8), (-2, -26, 5)]:
        d.ellipse([cx + ox - orr, cy + oy - orr, cx + ox + orr, cy + oy + orr],
                  fill=(140, 134, 122))
    # spacecraft with solar wings + dashed trajectory (starts below the chip)
    dashed(d, [(x + 14, y + 56), (x + 52, y + 66), (x + 92, y + 80), (cx - r - 6, cy - 6)],
           fill=GOLD_L, width=2)
    bx, by = x + 56, y + 66
    d.rectangle([bx - 6, by - 6, bx + 15, by + 9], fill=(220, 220, 225))
    d.rectangle([bx - 33, by - 3, bx - 7, by + 6], fill=(70, 110, 180))
    d.rectangle([bx + 16, by - 3, bx + 42, by + 6], fill=(70, 110, 180))
    d.text((x + 10, y + h - 18), "8 YEARS IN FLIGHT", font=F(SANS_B, 8), fill=GOLD_L)


# ---------------------------------------------------------------- mid panels
def mid_flags(d, x, y, w, h):
    """UK flag + EU flag, full-bleed side by side."""
    hw = w // 2
    # Union Jack (simplified): blue, white diagonals, red cross
    d.rectangle([x, y, x + hw, y + h], fill=(30, 50, 110))
    d.line([(x, y), (x + hw, y + h)], fill=WHITE, width=4)
    d.line([(x + hw, y), (x, y + h)], fill=WHITE, width=4)
    d.line([(x + hw // 2, y), (x + hw // 2, y + h)], fill=WHITE, width=8)
    d.line([(x, y + h // 2), (x + hw, y + h // 2)], fill=WHITE, width=8)
    d.line([(x + hw // 2, y), (x + hw // 2, y + h)], fill=(200, 40, 40), width=3)
    d.line([(x, y + h // 2), (x + hw, y + h // 2)], fill=(200, 40, 40), width=3)
    # EU flag: blue, ring of gold stars
    d.rectangle([x + hw, y, x + w, y + h], fill=(20, 50, 140))
    for i in range(8):
        ang = 2 * math.pi * i / 8 - math.pi / 2
        sx = x + hw + hw / 2 + (hw / 2 - 10) * math.cos(ang)
        sy = y + h / 2 + (h / 2 - 10) * math.sin(ang)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD_L)


def mid_missile(d, x, y, w, h):
    """Green field, cruise missile on the ground, crater, fence posts."""
    d.rectangle([x, y, x + w, y + h], fill=(168, 196, 130))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(120, 150, 88))
    for px in range(x + 8, x + w - 6, 18):  # fence posts
        d.line([(px, y + h - 26), (px, y + h - 14)], fill=(90, 70, 40), width=2)
    d.ellipse([x + w // 2 - 26, y + h - 34, x + w // 2 + 26, y + h - 14], fill=(90, 62, 40))
    d.ellipse([x + w // 2 - 16, y + h - 30, x + w // 2 + 16, y + h - 18], fill=(60, 40, 26))
    # missile body, diagonal
    d.line([(x + 30, y + 44), (x + w - 46, y + 22)], fill=(200, 200, 205), width=7)
    d.polygon([(x + w - 46, y + 22), (x + w - 28, y + 16), (x + w - 30, y + 28)], fill=(200, 40, 40))
    d.line([(x + 34, y + 40), (x + 26, y + 50)], fill=(120, 120, 125), width=4)


def mid_cop31(d, x, y, w, h):
    """Globe, thermometer, NO DEAL slash."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 240))
    cx, cy, r = x + 52, y + h // 2 + 2, 32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 190))
    d.ellipse([cx - 18, cy - 24, cx + 2, cy - 2], fill=GREEN)
    d.ellipse([cx - 4, cy + 6, cx + 20, cy + 26], fill=GREEN)
    d.ellipse([cx + 8, cy - 26, cx + 24, cy - 10], fill=GREEN)
    d.line([(cx - 30, cy + 10), (cx + 30, cy - 8)], fill=(90, 160, 210), width=2)
    # thermometer
    tx = x + w - 34
    d.rectangle([tx, y + 10, tx + 10, y + h - 22], fill=WHITE, outline=RED, width=2)
    d.ellipse([tx - 3, y + h - 28, tx + 13, y + h - 12], fill=RED)
    d.rectangle([tx + 3, y + h - 34, tx + 7, y + h - 16], fill=RED)
    d.line([(x + 8, y + 8), (x + w - 8, y + h - 8)], fill=RED, width=3)


def mid_iraq(d, x, y, w, h):
    """Desert, two tanks, sun, flag pole."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 214, 160))
    d.ellipse([x + w - 34, y + 6, x + w - 10, y + 30], fill=(240, 180, 60))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(205, 170, 110))
    for tx in (x + 26, x + 96):
        d.rectangle([tx, y + h - 34, tx + 52, y + h - 20], fill=(70, 64, 52))
        d.rectangle([tx + 16, y + h - 44, tx + 36, y + h - 34], fill=(70, 64, 52))
        d.line([(tx + 36, y + h - 40), (tx + 62, y + h - 46)], fill=(50, 46, 38), width=3)
        for wx in range(4):
            d.ellipse([tx + 8 + wx * 12, y + h - 18, tx + 14 + wx * 12, y + h - 12], fill=(40, 36, 30))
    d.line([(x + w - 14, y + 8), (x + w - 14, y + 34)], fill=(90, 80, 60), width=2)
    d.polygon([(x + w - 14, y + 8), (x + w - 2, y + 13), (x + w - 14, y + 18)], fill=RED)


def mid_bukele(d, x, y, w, h):
    """Ballot box with a ballot paper, green check."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 244))
    bx, by, bw, bh = x + w // 2 - 46, y + 34, 92, 38
    d.rectangle([bx, by, bx + bw, by + bh], fill=(40, 80, 160))
    d.rectangle([bx - 6, by - 8, bx + bw + 6, by], fill=(30, 60, 130))
    d.rectangle([bx + bw // 2 - 16, by - 8, bx + bw // 2 + 16, by - 4], fill=(20, 20, 24))
    d.rectangle([bx + 16, y + 24, bx + 56, y + 44], fill=WHITE, outline=GREY, width=1)
    d.line([(bx + 24, y + 34), (bx + 32, y + 41), (bx + 48, y + 27)], fill=GREEN, width=3)


def mid_strike(d, x, y, w, h):
    """Crowd of marchers under a red SCIOPERO banner."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 222))
    d.rectangle([x + 8, y + 6, x + w - 8, y + 22], fill=RED)
    d.text((x + w // 2, y + 8), "SCIOPERO", font=F(SANS_B, 11), fill=WHITE, anchor="ma")
    for i, fx in enumerate([22, 52, 82, 112, 142, 168]):
        col = (30, 30, 34) if i % 2 == 0 else (120, 40, 40)
        d.ellipse([x + fx, y + 32, x + fx + 12, y + 44], fill=col)
        d.rectangle([x + fx - 2, y + 45, x + fx + 14, y + h - 8], fill=col)
        d.line([(x + fx + 6, y + 46), (x + fx - 6, y + 58)], fill=col, width=3)
    d.text((x + w // 2, y + h - 12), "100+ CITIES", font=F(SANS_B, 8), fill=GREY, anchor="ma")


def mid_cpi(d, x, y, w, h):
    """Rising bars, 2.3% big, yen mark."""
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    d.line([(x + 10, y + h - 16), (x + w - 10, y + h - 16)], fill=GREY, width=1)
    for i, bh in enumerate([14, 24, 36]):
        bx = x + 16 + i * 26
        d.rectangle([bx, y + h - 16 - bh, bx + 18, y + h - 16], fill=RED if i == 2 else (200, 80, 80))
    d.text((x + w - 10, y + 6), "¥", font=F(SANS_B, 20), fill=NAVY, anchor="ra")
    d.text((x + 10, y + h - 14), "OCT · YoY", font=F(SANS, 8), fill=GREY)


def mid_cricket(d, x, y, w, h):
    """Green pitch, bat, red ball, big 118."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 130, 70))
    d.rectangle([x + 14, y + 8, x + w - 14, y + h - 8], fill=(120, 170, 110))
    d.line([(x + 14, y + h // 2), (x + w - 14, y + h // 2)], fill=WHITE, width=1)
    # bat, angled
    d.polygon([(x + 40, y + 14), (x + 52, y + 10), (x + 78, y + 52), (x + 66, y + 56)], fill=(222, 190, 140))
    d.line([(x + 40, y + 14), (x + 28, y + 4)], fill=(150, 110, 70), width=4)
    d.ellipse([x + w - 44, y + 12, x + w - 28, y + 28], fill=(200, 40, 40))
    d.text((x + 12, y + h - 24), "118", font=F(SANS_B, 22), fill=WHITE)


def mid_nvidia(d, x, y, w, h):
    """Green chip on a dark board, solder dots at the corners."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 32))
    cx, cy = x + w // 2, y + h // 2 + 2
    d.rectangle([cx - 28, cy - 28, cx + 28, cy + 28], fill=(40, 120, 70))
    for px in (-34, -17, 0, 17):
        d.line([(cx + px, cy - 36), (cx + px, cy - 28)], fill=(180, 180, 185), width=2)
        d.line([(cx + px, cy + 28), (cx + px, cy + 36)], fill=(180, 180, 185), width=2)
    d.rectangle([cx - 13, cy - 13, cx + 13, cy + 13], fill=(24, 26, 32))
    d.text((cx, cy - 9), "NV", font=F(SANS_B, 12), fill=(120, 220, 140), anchor="ma")
    for dx, dy in [(14, 12), (w - 14, 12), (14, h - 12), (w - 14, h - 12)]:
        d.ellipse([x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3], fill=(120, 130, 150))


def mid_suneung(d, x, y, w, h):
    """Exam paper, smart glasses, red X."""
    d.rectangle([x, y, x + w, y + h], fill=(244, 242, 236))
    d.rectangle([x + 14, y + 6, x + w - 60, y + h - 6], fill=WHITE, outline=GREY, width=1)
    for i, ly in enumerate(range(y + 14, y + h - 14, 9)):
        d.line([(x + 20, ly), (x + w - 66, ly)], fill=GREY_L, width=1)
    d.ellipse([x + w - 56, y + 12, x + w - 30, y + 36], fill=(30, 30, 34))
    d.ellipse([x + w - 28, y + 12, x + w - 2, y + 36], fill=(30, 30, 34))
    d.line([(x + w - 30, y + 23), (x + w - 28, y + 23)], fill=(30, 30, 34), width=3)
    d.line([(x + w - 56, y + 21), (x + w - 62, y + 15)], fill=(30, 30, 34), width=2)
    d.line([(x + w - 52, y + 52), (x + w - 12, y + h - 10)], fill=RED, width=4)
    d.line([(x + w - 12, y + 52), (x + w - 52, y + h - 10)], fill=RED, width=4)


# ---------------------------------------------------------------- map
LONLAT = {
    "NA": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60), (-55, 47),
           (-70, 42), (-75, 35), (-80, 26), (-85, 30), (-95, 29), (-105, 22), (-115, 30),
           (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    "SA": [(-80, 10), (-60, 5), (-50, -5), (-35, -8), (-40, -20), (-50, -30), (-60, -40),
           (-70, -50), (-73, -35), (-80, -20), (-80, -5)],
    "EU": [(-10, 36), (-9, 43), (0, 46), (-2, 50), (5, 53), (8, 57), (18, 56), (21, 55),
           (28, 60), (30, 70), (40, 68), (45, 60), (40, 50), (30, 45), (28, 40), (23, 36),
           (18, 40), (12, 44), (8, 38), (3, 36)],
    "AF": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
           (51, 11), (48, 0), (40, -10), (35, -20), (30, -30), (20, -35), (15, -27),
           (12, -18), (9, -1), (9, 4), (-8, 5), (-15, 12)],
    "AS": [(40, 68), (60, 70), (80, 73), (100, 76), (130, 72), (160, 70), (180, 66),
           (170, 60), (160, 55), (142, 50), (140, 40), (130, 42), (127, 35), (122, 30),
           (120, 25), (110, 20), (108, 10), (105, 2), (100, 8), (95, 15), (90, 22),
           (80, 15), (75, 8), (70, 20), (60, 25), (55, 30), (50, 35), (45, 30), (42, 38), (40, 45)],
    "AU": [(113, -22), (125, -14), (135, -12), (142, -11), (150, -20), (153, -27),
           (150, -37), (140, -38), (130, -32), (122, -34), (115, -35), (113, -26)],
}

PINS = [(30, 50, "1"), (86, 20, "2"), (4, 51, "3"), (-115, 36, "4"), (127, 37, "5"),
        (42, 9, "6"), (-17, 15, "7"), (44, 33, "8"), (-89, 14, "9"), (12, 42, "10"),
        (139, 36, "11"), (175, -41, "12")]


def draw_map(d, x, y, w, h):
    """Cream world map with numbered pins (leaders' legible style)."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER)

    def proj(lon, lat):
        px = x + (lon + 170) / 360 * w
        py = y + (75 - lat) / 130 * h
        return (px, py)

    for poly in LONLAT.values():
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=TAN, outline=(150, 130, 90))
    for lon, lat, num in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=WHITE, width=1)
        d.text((px, py - 7), num, font=F(SANS_B, 10), fill=WHITE, anchor="ma")
    d.text((x + w // 2, y + h - 12), "Pins 1–12 mark the drawn stories.",
           font=F(SANS, 7), fill=GREY, anchor="ma")


# ---------------------------------------------------------------- content
HEROES = [
    dict(panel=panel_kyiv, chip="KYIV", sub="3 bridges hit", kicker="WAR IN UKRAINE", head="Missiles rain on Kyiv's bridges",
         deck="Three Dnipro crossings hit in an overnight barrage of 80+ missiles and 400 drones.",
         src="Reuters · Kyiv Post", status="Officials say"),
    dict(panel=panel_akvan, chip="CYCLONE AKVAN", sub="Landfall · 8 am", kicker="CYCLONE AKVAN", head="Akvan comes ashore, spares lives",
         deck="More than 300,000 moved to shelters as the storm crosses Odisha at 70–80 km/h.",
         src="IMD · NDTV", status="Officials say"),
    dict(panel=panel_ai, chip="AI SELL-OFF", sub="Asia, Friday's close", kicker="MARKETS", head="Asia's AI rally unwinds",
         deck="Taiex −6.2% in its worst week since 1991; Nikkei −5.1%, Kospi −5.2%.",
         src="Al Jazeera · Reuters", status="Reported"),
    dict(panel=panel_mercury, chip="MERCURY", sub="Orbit burn Saturday", kicker="SPACE · ARRIVES TOMORROW", head="Mercury: almost there",
         deck="After eight years in flight, BepiColombo is captured by Mercury's gravity on Saturday.",
         src="ESA", status="Reported"),
]

MIDS = [
    dict(panel=mid_flags, chip="UK–EU DEAL", place="BRUSSELS · DIPLOMACY", head="UK and EU seal a “reset” deal",
         deck="Food trade, youth visas, carbon link.", src="Reuters", status="Reported"),
    dict(panel=mid_missile, chip="KH-101 IN POLAND", place="POLAND · WAR", head="Russian cruise missile lands in Poland",
         deck="Kh-101 down; NATO jets scrambled.", src="Ukrainska Pravda", status="Officials say"),
    dict(panel=mid_cop31, chip="COP31: NO DEAL", place="ANTALYA · CLIMATE", head="COP31 reaches its last day with no deal",
         deck="Draft text leaves out fossil fuels.", src="AFP", status="Ongoing"),
    dict(panel=mid_iraq, chip="IRAQ: ARMY IN", place="IRAQ · SECURITY", head="Iraqi army enters a militia stronghold",
         deck="Troops deploy to Jurf al-Sakhar.", src="AFP", status="Reported"),
    dict(panel=mid_bukele, chip="BUKELE: 3RD TERM", place="SAN SALVADOR · POLITICS", head="Bukele files to run for a third term",
         deck="The vote is on 28 February 2027.", src="Reuters", status="Filed"),
    dict(panel=mid_strike, chip=None, place="ROME · LABOUR", head="General strike over Italy's budget",
         deck="Workers and students march.", src="Reuters", status="Reported"),
    dict(panel=mid_cpi, chip="JAPAN: +2.3%", place="TOKYO · ECONOMY", head="Japan's inflation picks up to 2.3%",
         deck="A December rate rise stays in view.", src="Japan Times", status="Official data"),
    dict(panel=mid_cricket, chip="PHILLIPS: 118", place="WELLINGTON · CRICKET", head="Phillips hits 118 against India",
         deck="Hundreds in all three formats.", src="Reuters", status="Scorecard"),
    dict(panel=mid_nvidia, chip="NVIDIA: SUBPOENA", place="CALIFORNIA · TECH", head="California subpoenas Nvidia",
         deck="China chips probe; investors misled.", src="Reuters", status="Reported"),
    dict(panel=mid_suneung, chip="SUNEUNG: 111 CAUGHT", place="SEOUL · EDUCATION", head="Suneung: 111 caught cheating",
         deck="Glasses, mini-cameras; ban proposed.", src="Yonhap", status="Officials say"),
]

BRIEFS = [
    ("Kenya oil rig on — first crude due Dec 1", "Business Daily"),
    ("China holds loan rates for an 18th straight month", "Xinhua"),
    ("Senegal boat capsizes; 4 dead, dozens missing", "Al Jazeera"),
    ("Malawi fuel queues; 20L a day ration", "Al Jazeera"),
    ("F1: Russell fastest in wet Las Vegas FP2", "formula1.com"),
    ("Cancer pill shrinks tumours in 60.7%", "Reuters"),
    ("Rohingya: Myanmar calls ICJ ruling “unfair”", "Reuters"),
    ("GTA VI: 24.58m copies, $2.36bn by launch day", "Reuters"),
    ("Seoul ruling party moves to impeach top judge", "Yonhap"),
    ("Brent $92.60 as Hormuz fears rise", "Reuters"),
    ("Houthi missiles at Riyadh intercepted", "AFP"),
    ("Iran says two tankers hit mines in Hormuz", "Reuters"),
    ("Erasca pill: 44% of patients respond in trial", "Reuters"),
    ("Antonelli confirmed youngest F1 champion", "FIA"),
    ("Court overturns ex-PM Han's conviction", "Yonhap"),
    ("Lviv: 2 killed in the strikes", "Reuters"),
    ("Rzeszow airport shut, tower evacuated", "Ukrainska Pravda"),
    ("Youth protests spread to five more countries", "Reuters"),
    ("US approved 900,000 chips for China", "House"),
    ("Akvan: 423 rescue teams, 9,341 shelters ready", "NDTV"),
    ("SoftBank −14.6% in the AI rout", "Reuters"),
    ("TSMC −5.2% as the AI trade cracks", "CNA"),
    ("COP31 keeps its “35 by 35” clean-power goal", "Carbon Brief"),
    ("EU calls the COP31 draft “not acceptable”", "AFP"),
    ("Poland scrambles F-16s and Swedish Gripens", "Ukrainska Pravda"),
    ("Gopalpur landfall 07:30–08:30, done by 11:20", "IMD"),
]

MOMENTS = [
    ("01:20", "KYIV", "Missiles hit 3 bridges"),
    ("07:30", "GOPALPUR", "Landfall begins"),
    ("08:30", "TOKYO", "CPI 2.3% released"),
    ("11:20", "ODISHA", "Landfall done, no deaths"),
    ("EVENING", "BRUSSELS", "UK–EU deal sealed"),
]

STATS = [
    ("3", "BRIDGES HIT"), ("8", "KILLED"), ("300,000+", "EVACUATED"),
    ("−6.2%", "TAIEX"), ("$92.60", "BRENT"), ("100,000", "YOUTH VISAS"),
]

REGIONS = [("EUROPE", 12, NAVY), ("ASIA", 12, RED), ("MIDDLE EAST", 4, (150, 90, 30)),
           ("AFRICA", 3, GREEN), ("AMERICAS", 5, (90, 60, 130)), ("OCEANIA", 1, (40, 120, 130)),
           ("GLOBAL", 3, GREY)]

RECORDS = [
    ("WORST WEEK SINCE 1991", "Taiex −17.5% on the week"),
    ("YOUNGEST CHAMPION", "Antonelli: F1's youngest champion"),
    ("ONLY THE 2ND EVER", "Phillips: 100s in all 3 formats vs India"),
    ("8 YEARS IN FLIGHT", "BepiColombo reaches Mercury Saturday"),
]


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # ---- masthead 0-100
    d.rectangle([0, 0, W, 100], fill=NAVY)
    d.rectangle([0, 100, W, 102], fill=GOLD)
    text(d, 10, 8, "THE FRIDAY EDITION  ·  NIGHT EDITION", F(SANS_B, 11), fill=GOLD_L)
    text(d, 1014, 8, "40 STORIES", F(SANS_B, 13), fill=GOLD_L, anchor="ra")
    text(d, 1014, 26, "7 REGIONS", F(SANS_B, 11), fill=WHITE, anchor="ra")
    text(d, 8, 22, "Friday 20 November 2026", F(SERIF_B, 52), fill=WHITE)
    text(d, 10, 80, "Kyiv's bridges hit  ·  Cyclone Akvan ashore  ·  Asia's markets plunge  ·  UK–EU seal reset",
         F(SERIF_I, 14), fill=(220, 220, 210))
    # ---- region bar 102-122 (proportional segments, leaders' style)
    segbar(d, 10, 104, 1004, 16, REGIONS)
    # ---- timeline 122-166 (compressed)
    text(d, 10, 125, "THE DAY IN FIVE MOMENTS", F(SANS_B, 11), fill=RED)
    text(d, 1014, 125, "LOCAL TIMES", F(SANS, 9), fill=GREY, anchor="ra")
    rule(d, 10, 139, 1014, GREY_L, 1)
    slot = (1014 - 10) / 5
    for i, (tm, place, what) in enumerate(MOMENTS):
        sx = 10 + i * slot
        text(d, sx, 144, tm, F(SANS_B, 13), fill=NAVY)
        px = sx + int(d.textlength(tm, font=F(SANS_B, 13))) + 8
        text(d, px, 145, place, F(SANS_B, 11), fill=INK)
        text(d, sx, 158, what, F(SANS, 9), fill=GREY)
    # ---- stat strip 166-212
    sw = (1014 - 10) / 6
    for i, (val, label) in enumerate(STATS):
        sx = 10 + i * sw
        d.rectangle([sx + 2, 170, sx + sw - 2, 208], fill=WHITE, outline=GREY_L, width=1)
        text(d, sx + sw / 2, 174, val, F(SANS_B, 17), fill=NAVY, anchor="ma")
        text(d, sx + sw / 2, 194, label, F(SANS_B, 9), fill=GREY, anchor="ma")
    # ---- heroes 212-436: panels 112 tall + in-panel headline chips
    hw, gap = 247, 6
    for i, hero in enumerate(HEROES):
        hx = 8 + i * (hw + gap)
        hero["panel"](d, hx, 216, hw, 112)
        cw, ch = panel_chip(d, hx + 6, 222, hero["chip"], F(SANS_B, 13))
        sub = hero["sub"]
        sw2 = int(d.textlength(sub, font=F(SANS_B, 10))) + 12
        d.rectangle([hx + 6, 222 + ch + 4, hx + 6 + sw2, 222 + ch + 4 + 18], fill=WHITE)
        d.text((hx + 12, 222 + ch + 7), sub, font=F(SANS_B, 10), fill=INK)
        text(d, hx, 332, hero["kicker"], F(SANS_B, 10), fill=RED)
        y = 346
        for line in wrap(d, hero["head"], F(SERIF_B, 18), hw)[:2]:
            d.text((hx, y), line, font=F(SERIF_B, 18), fill=INK)
            y += 21
        y = 390
        for line in wrap(d, hero["deck"], F(SANS, 11), hw)[:2]:
            d.text((hx, y), line, font=F(SANS, 11), fill=INK)
            y += 13
        text(d, hx, 420, hero["src"], F(SANS, 9), fill=GREY)
        tag(d, hx + 150, 418, hero["status"], F(SANS_B, 8), NAVY)
    rule(d, 8, 436, 1014, NAVY, 2)
    # ---- mid grid: THE DAY'S TEN, 5 cols x 2 rows, drawn panels + chips
    d.rectangle([8, 440, 8 + 138, 460], fill=NAVY)
    text(d, 14, 444, "THE DAY'S TEN", F(SANS_B, 12), fill=WHITE)
    text(d, 1014, 444, "EVERY STORY DRAWN", F(SANS_B, 9), fill=GREY, anchor="ra")
    mw, mgap = 197, 5
    for i, mid in enumerate(MIDS):
        col, row = i % 5, i // 5
        mx = 8 + col * (mw + mgap)
        py = 464 + row * 152
        ty = py + 80
        mid["panel"](d, mx, py, mw, 76)
        d.rectangle([mx, py, mx + mw, py + 76], outline=GREY_L, width=1)
        if mid.get("chip"):
            panel_chip(d, mx + 4, py + 4, mid["chip"], F(SANS_B, 10))
        text(d, mx, ty, f"{5 + i} · {mid['place']}", F(SANS_B, 9), fill=RED)
        text(d, mx + mw, ty, mid["src"], F(SANS, 8), fill=GREY, anchor="ra")
        y = ty + 12
        for line in wrap(d, mid["head"], F(SANS_B, 15), mw)[:2]:
            d.text((mx, y), line, font=F(SANS_B, 15), fill=INK)
            y += 18
        deck = one_line(d, mid["deck"], F(SANS, 10), mw)
        d.text((mx, y + 1), deck, font=F(SANS, 10), fill=INK)
        text(d, mx, y + 13, mid["status"], F(SANS, 8), fill=GREY)
    # ---- records strip 772-802: the one thing no leader has
    rule(d, 8, 772, 1014, GOLD, 2)
    text(d, 10, 778, "RECORDS OF THE DAY", F(SANS_B, 10), fill=RED)
    rw = (1014 - 180) / 4
    for i, (label, fact) in enumerate(RECORDS):
        rx = 180 + i * rw
        text(d, rx, 778, label, F(SANS_B, 9), fill=NAVY)
        text(d, rx, 791, one_line(d, fact, F(SANS, 9), rw - 8), F(SANS, 9), fill=INK)
    # ---- bottom: map + briefs, header 808-828, content 830-980
    d.rectangle([8, 808, 1014, 828], fill=NAVY)
    text(d, 14, 812, "WHERE IT HAPPENED", F(SANS_B, 11), fill=WHITE)
    text(d, 1014 - 6, 812, "ALSO ON FRIDAY  —  26 MORE STORIES, 40 IN ALL", F(SANS_B, 10), fill=WHITE, anchor="ra")
    draw_map(d, 8, 830, 330, 148)
    bx0, bw = 348, 334
    f_num, f_txt, f_src = F(SANS_B, 10), F(SANS, 10), F(SANS, 8)
    for j, (txt, src) in enumerate(BRIEFS):
        col, row = j // 13, j % 13
        bx = bx0 + col * (bw + 6)
        by = 830 + row * 11
        num = 15 + j
        d.text((bx, by), f"{num}.", font=f_num, fill=RED)
        nw = int(d.textlength(f"{num}.", font=f_num)) + 4
        srcw = int(d.textlength(src, font=f_src)) + 6
        maxw = bw - nw - srcw - 4
        fit = txt
        while d.textlength(fit, font=f_txt) > maxw and " " in fit:
            fit = fit.rsplit(" ", 1)[0] + "…"
        d.text((bx + nw, by), fit, font=f_txt, fill=INK)
        d.text((bx + bw, by + 1), src, font=f_src, fill=GREY, anchor="ra")
    # ---- date check 982-1010 + footer 1014
    d.rectangle([8, 982, 1014, 1010], outline=RED, width=2)
    text(d, 14, 986, "DATE CHECK", F(SANS_B, 10), fill=RED)
    para(d, 108, 986, "Left out as Thursday 19 November news: Anthropic's ANT debut · Wall Street −2% · Dow under 50,000 · ICJ ruling itself (reactions are Friday) · Riyadh tower damage · COP31 second draft.",
         F(SANS, 10), 1014 - 114, leading=12)
    text(d, 10, 1014, "Every story here happened, or was first reported, on Friday 20 November 2026. Claims are attributed, not stated as fact.",
         F(SANS, 9), fill=GREY)
    text(d, 1014, 1014, "Sources named beside each story · Original drawings · Drawn by an AI agent for make.fun",
         F(SANS, 9), fill=GREY, anchor="ra")
    return img, d


def main():
    img, _ = render()
    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()

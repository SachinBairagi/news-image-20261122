#!/usr/bin/env python3
"""The World in One Day, Sunday 22 November 2026.

Draws a one-page newspaper front page summing up the world news of
Sunday 22 November 2026 and writes it to /output/entry.png.

Pure Python standard library. The poster is drawn from code onto an
RGB pixel buffer: flat pictograms, headlines and captions set from a
small 5x7 bitmap font defined below. No network, no clock, no
randomness: two runs produce byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
INK = (24, 28, 38)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
GOLD = (232, 163, 23)
WHITE = (255, 255, 255)
MUTED = (110, 106, 96)
SKY = (205, 227, 238)
LIGHT = (232, 226, 211)
SLATE = (70, 80, 96)
SAFFRON = (255, 153, 51)
GREEN = (19, 136, 8)
CRIMSON = (220, 20, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 characters; '#' is a filled pixel.
FONT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".###.", "#...#", "#...#", ".#.#.", "#.#..", "#.#.#", ".##.#"),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '+': (".....", ".....", ".#...", ".#...", "#####", ".#...", ".#..."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}


class Canvas:
    """An RGB pixel buffer with simple flat drawing primitives."""

    def __init__(self):
        self.px = bytearray(W * H * 3)
        self.fill_rect(0, 0, W, H, PAPER)

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def rect_outline(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        half = w // 2
        while True:
            self.fill_rect(x - half, y - half, w, w, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, y, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, w=2):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            outer = int((r * r - dy * dy) ** 0.5)
            inner_r = r - w
            if inner_r > 0 and abs(dy) < inner_r:
                inner = int((inner_r * inner_r - dy * dy) ** 0.5)
                self.fill_rect(cx - outer, y, outer - inner, 1, c)
                self.fill_rect(cx + inner, y, outer - inner + 1, 1, c)
            else:
                self.fill_rect(cx - outer, y, 2 * outer + 1, 1, c)

    def polygon(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, max(1, int(xs[i + 1] - xs[i])), 1, c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, x, y, w, s, scale, c):
        tw = self.text_w(s, scale)
        self.text(x + (w - tw) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        lines = []
        cur = ''
        for word in s.split(' '):
            trial = (cur + ' ' + word).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, maxw):
        for ln in self.wrap(s, scale, maxw):
            self.text(x, y, ln, scale, c)
            y += 9 * scale
        return y

    # ------------------------------------------------------------ png
    def png_bytes(self):
        raw = bytearray()
        for y in range(H):
            raw.append(0)
            raw += self.px[y * W * 3:(y + 1) * W * 3]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(typ, data):
            return (struct.pack('>I', len(data)) + typ + data +
                    struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))

        ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
        return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', comp) + chunk(b'IEND', b''))


# ---------------------------------------------------------------- pictograms
def draw_globe(cv, cx, cy, r):
    """Earth with a jagged crack: the climate talks failed."""
    cv.circle(cx, cy, r, SKY)
    cv.ring(cx, cy, r, NAVY, 4)
    # latitude lines, clipped to the disc
    for dy in (-r // 2, 0, r // 2):
        dx = int((r * r - dy * dy) ** 0.5) - 4
        cv.line(cx - dx, cy + dy, cx + dx, cy + dy, NAVY, 2)
    # meridian
    cv.line(cx, cy - r + 4, cx, cy + r - 4, NAVY, 2)
    # the crack
    crack = [(cx - 22, cy - r + 8), (cx - 6, cy - r + 42), (cx - 24, cy - r + 74),
             (cx - 2, cy - r + 104), (cx - 20, cy - r + 132), (cx + 2, cy - r + 162),
             (cx - 12, cy + r - 10)]
    for i in range(len(crack) - 1):
        cv.line(crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1], RED, 5)
    cv.line(cx - 6, cy - r + 42, cx + 22, cy - r + 58, RED, 4)
    cv.line(cx - 2, cy - r + 104, cx + 26, cy - r + 118, RED, 4)


def draw_missile(cv, cx, cy):
    """Missile and burst: the strike on Bahrain."""
    burst = []
    for i in range(12):
        ang = i * 30
        rad = 34 if i % 2 == 0 else 16
        import math
        bx = cx + 34 + int(rad * math.cos(math.radians(ang)))
        by = cy - 30 + int(rad * math.sin(math.radians(ang)))
        burst.append((bx, by))
    cv.polygon(burst, GOLD)
    cv.circle(cx + 34, cy - 30, 10, RED)
    # missile body, nose up-right
    cv.polygon([(cx - 34, cy + 34), (cx - 18, cy + 18), (cx + 8, cy - 8),
                (cx + 26, cy - 26), (cx + 14, cy - 34), (cx - 4, cy - 16),
                (cx - 22, cy + 2), (cx - 40, cy + 20)], NAVY)
    cv.polygon([(cx + 26, cy - 26), (cx + 44, cy - 44), (cx + 34, cy - 18)], RED)
    cv.polygon([(cx - 40, cy + 20), (cx - 52, cy + 40), (cx - 30, cy + 34)], GOLD)
    cv.polygon([(cx - 22, cy + 2), (cx - 34, cy + 30), (cx - 12, cy + 22)], GOLD)


def draw_building(cv, cx, cy):
    """Apartment block with a broken top and smoke: the Kyiv strike."""
    cv.circle(cx - 26, cy - 52, 12, MUTED)
    cv.circle(cx + 4, cy - 62, 14, MUTED)
    cv.circle(cx + 28, cy - 50, 10, MUTED)
    # block with jagged broken roofline
    cv.polygon([(cx - 36, cy + 48), (cx - 36, cy - 18), (cx - 18, cy - 34),
                (cx - 4, cy - 16), (cx + 12, cy - 36), (cx + 36, cy - 20),
                (cx + 36, cy + 48)], NAVY)
    # windows
    for wy in (-6, 12, 30):
        for wx in (-26, -8, 10, 26):
            cv.fill_rect(cx + wx - 5, cy + wy - 5, 10, 10, GOLD if (wx + wy) % 3 else SKY)
    # crack down the facade
    cv.line(cx + 8, cy - 30, cx - 2, cy + 6, RED, 3)
    cv.line(cx - 2, cy + 6, cx + 10, cy + 30, RED, 3)


def draw_flags(cv, cx, cy):
    """Nepal's double pennant beside India's tricolour: the Delhi visit."""
    # Nepal flag: two stacked crimson pennants with a white edge
    cv.polygon([(cx - 52, cy - 36), (cx - 52, cy - 4), (cx - 14, cy - 20)], WHITE)
    cv.polygon([(cx - 48, cy - 32), (cx - 48, cy - 8), (cx - 20, cy - 20)], CRIMSON)
    cv.polygon([(cx - 52, cy - 2), (cx - 52, cy + 34), (cx - 18, cy + 16)], WHITE)
    cv.polygon([(cx - 48, cy + 2), (cx - 48, cy + 30), (cx - 24, cy + 16)], CRIMSON)
    # India flag: three stripes and a wheel
    cv.fill_rect(cx + 6, cy - 34, 52, 22, SAFFRON)
    cv.fill_rect(cx + 6, cy - 12, 52, 22, WHITE)
    cv.fill_rect(cx + 6, cy + 10, 52, 24, GREEN)
    cv.ring(cx + 32, cy - 1, 9, NAVY, 2)
    cv.line(cx + 32, cy - 10, cx + 32, cy + 8, NAVY, 1)
    cv.line(cx + 23, cy - 1, cx + 41, cy - 1, NAVY, 1)


def draw_storm(cv, cx, cy):
    """Storm cloud, rain and lightning: the Brazil storm."""
    cv.circle(cx - 26, cy - 8, 20, SLATE)
    cv.circle(cx + 2, cy - 18, 24, SLATE)
    cv.circle(cx + 28, cy - 6, 18, SLATE)
    cv.fill_rect(cx - 46, cy - 8, 92, 18, SLATE)
    # lightning bolt
    cv.polygon([(cx + 6, cy + 8), (cx - 8, cy + 34), (cx + 2, cy + 34),
                (cx - 8, cy + 58), (cx + 16, cy + 26), (cx + 4, cy + 26),
                (cx + 16, cy + 8)], GOLD)
    # rain
    for rx in (-44, -28, 34, 48):
        cv.line(cx + rx, cy + 22, cx + rx - 8, cy + 44, SKY, 3)


def draw_race_flag(cv, cx, cy):
    """Chequered flag on a pole: the Las Vegas Grand Prix."""
    cv.fill_rect(cx - 40, cy - 44, 5, 96, INK)
    for row in range(4):
        for col in range(5):
            colr = INK if (row + col) % 2 == 0 else WHITE
            cv.fill_rect(cx - 34 + col * 15, cy - 44 + row * 15, 15, 15, colr)
    cv.rect_outline(cx - 34, cy - 44, 75, 60, INK, 2)
    # speed lines
    for ly in (16, 30, 44):
        cv.line(cx + 48, cy + ly, cx + 78, cy + ly, RED, 3)


# ---------------------------------------------------------------- poster
def draw_poster():
    cv = Canvas()
    # frame
    cv.rect_outline(12, 12, 1000, 1000, INK, 3)
    cv.rect_outline(20, 20, 984, 984, INK, 1)

    # masthead
    cv.text_center(24, 36, 976, "THE WORLD IN ONE DAY", 6, INK)
    cv.fill_rect(24, 92, 976, 2, INK)
    cv.text_center(24, 100, 976, "SUNDAY, 22 NOVEMBER 2026", 2, INK)
    cv.fill_rect(24, 126, 976, 4, RED)

    # ---- lead story: COP31 collapses
    draw_globe(cv, 172, 272, 92)
    cv.fill_rect(118, 378, 108, 28, RED)
    cv.text_center(118, 384, 108, "NO DEAL", 2, WHITE)
    cv.text(340, 148, "CLIMATE - ANTALYA, TURKIYE", 2, RED)
    cv.text(340, 174, "COP31 TALKS COLLAPSE", 5, INK)
    cv.text(340, 224, "NO DEAL ON FOSSIL FUELS", 2, INK)
    cv.para(340, 254, "THE UN CLIMATE SUMMIT ENDED ON SUNDAY WITH NO "
            "AGREEMENT, TWO DAYS PAST ITS DEADLINE. THE EU, THE UK AND "
            "SMALL ISLAND STATES REJECTED THE FINAL DRAFT BECAUSE IT SAID "
            "NOTHING ABOUT FOSSIL FUELS.", 2, INK, 660)
    cv.text(340, 356, "FIRST CLIMATE SUMMIT TO FAIL SINCE COPENHAGEN 2009", 2, RED)
    cv.fill_rect(24, 440, 976, 2, INK)

    # ---- middle row: Bahrain and Kyiv
    draw_missile(cv, 87, 560)
    cv.text(162, 462, "MIDDLE EAST", 2, RED)
    cv.para(162, 488, "IRAN STRIKES BAHRAIN", 3, INK, 338)
    cv.para(162, 548, "IRANIAN PROJECTILES HIT AN INDUSTRIAL SITE, "
            "WOUNDING TWO. GULF STATES CONDEMNED THE ATTACK.", 2, INK, 338)
    cv.fill_rect(508, 456, 2, 232, LIGHT)
    draw_building(cv, 587, 560)
    cv.text(662, 462, "UKRAINE", 2, RED)
    cv.para(662, 488, "DRONE HITS FLATS NEAR KYIV", 3, INK, 338)
    cv.para(662, 575, "A RUSSIAN DRONE HIT A FIVE-STOREY BLOCK IN DYMER. "
            "FOURTEEN ARE MISSING; TWO KILLED NEAR KYIV.", 2, INK, 338)
    cv.fill_rect(24, 704, 976, 2, INK)

    # ---- bottom row: Delhi, Brazil, Las Vegas
    draw_flags(cv, 180, 766)
    cv.text_center(24, 818, 312, "NEPAL PM IN", 3, INK)
    cv.text_center(24, 845, 312, "DELHI", 3, INK)
    cv.para(36, 872, "PM BALEN SHAH ARRIVED FOR TALKS WITH PM MODI IN DELHI.",
            2, INK, 288)
    cv.fill_rect(344, 720, 2, 200, LIGHT)
    draw_storm(cv, 512, 766)
    cv.text_center(356, 818, 312, "STORM KILLS 3", 3, INK)
    cv.text_center(356, 845, 312, "IN BRAZIL", 3, INK)
    cv.para(368, 872, "A VIOLENT STORM HIT TUPANCIRETA, WRECKING 8,000 HOMES.",
            2, INK, 288)
    cv.fill_rect(676, 720, 2, 200, LIGHT)
    draw_race_flag(cv, 844, 766)
    cv.text_center(688, 818, 312, "VERSTAPPEN", 3, INK)
    cv.text_center(688, 845, 312, "WINS IN VEGAS", 3, INK)
    cv.para(700, 872, "VERSTAPPEN BEAT NORRIS BY 0.6 SECONDS IN LAS VEGAS.",
            2, INK, 288)
    cv.fill_rect(24, 936, 976, 2, INK)

    # ---- footer ticker
    cv.text_center(24, 948, 976,
                   "ALSO TODAY: MEXICO CAPTURES CARTEL BOSS CHAPO ISIDRO", 2, INK)
    cv.text_center(24, 972, 976,
                   "INDIA 720/9 VS NEW ZEALAND - FACTORY FIRE IN INDONESIA, 50 MISSING",
                   2, INK)
    return cv


def main():
    cv = draw_poster()
    os.makedirs("/output", exist_ok=True)
    data = cv.png_bytes()
    with open("/output/entry.png", "wb") as f:
        f.write(data)
    print("wrote /output/entry.png: %d bytes" % len(data))


if __name__ == "__main__":
    main()

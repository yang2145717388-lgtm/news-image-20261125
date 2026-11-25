#!/usr/bin/env python3
"""The World in One Page -- Wednesday, 25 November 2026.

Draws a newspaper front page summing up the day's world news and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure stdlib + Pillow, no network, no file reads, fully deterministic:
the same run always writes the same bytes.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (248, 244, 233)
INK = (26, 26, 26)
MUTED = (90, 83, 72)
RED = (163, 22, 33)
GREEN = (18, 110, 58)
RULE = (26, 26, 26)
PANEL = (240, 234, 219)
PANEL_EDGE = (180, 172, 150)

FONT_PATHS = {
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def font(name, size):
    path = FONT_PATHS[name]
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size=size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, max_width, fill=INK, spacing=5,
               max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, max_width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError("text overflows: %r needs %d lines, max %d"
                         % (text[:40], len(lines), max_lines))
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def centered(draw, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rule(draw, y, x0=None, x1=None, width=2):
    x0 = MARGIN if x0 is None else x0
    x1 = W - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)
    return y + width


def draw_masthead(draw):
    title = font("serif_bold", 60)
    centered(draw, 26, "THE WORLD IN ONE PAGE", title)
    date_f = font("sans_bold", 26)
    centered(draw, 102, "WEDNESDAY, 25 NOVEMBER 2026", date_f, fill=RED)
    sub_f = font("sans", 13)
    centered(draw, 140,
             "THE DAY'S WORLD NEWS  -  ONE PAGE, EVERY STORY THAT MATTERED",
             sub_f, fill=MUTED)
    rule(draw, 164)


def draw_lead(draw):
    x = MARGIN
    y = 182
    kicker = font("sans_bold", 16)
    draw.text((x, y), "LEAD STORY  -  SPACE", font=kicker, fill=RED)
    y += 26
    head = font("serif_bold", 36)
    y = text_block(draw, x, y,
                   "Shenzhou-24 lifts off -\nfirst foreigner in orbit",
                   head, 620, spacing=4, max_lines=2)
    y += 8
    body = font("sans", 19)
    y = text_block(
        draw, x, y,
        "China launched Shenzhou-24 from Jiuquan at 08:18 on Wednesday, "
        "carrying Tang Hongbo, Wu Yi and Pakistani payload specialist "
        "Muhammad Zeeshan Ali - the first Pakistani in orbit and the "
        "first foreign astronaut to visit China's Tiangong station. "
        "Docking was due about three and a half hours after liftoff.",
        body, 620, spacing=6, max_lines=5)
    # Right-hand numbers panel.
    px0, py0, px1, py1 = 692, 182, W - MARGIN, 440
    draw.rectangle([px0, py0, px1, py1], fill=PANEL, outline=PANEL_EDGE,
                   width=2)
    cx = px0 + 18
    lab = font("sans_bold", 14)
    draw.text((cx, py0 + 12), "THE LAUNCH IN NUMBERS", font=lab, fill=MUTED)
    big = font("sans_bold", 52)
    draw.text((cx, py0 + 38), "08:18", font=big, fill=GREEN)
    cap = font("sans", 15)
    draw.text((cx, py0 + 98), "Liftoff, Jiuquan, Wednesday", font=cap,
              fill=INK)
    draw.text((cx, py0 + 118), "Long March-2F rocket, three crew,",
              font=cap, fill=INK)
    draw.text((cx, py0 + 138), "docking ~3.5 hours later.",
              font=cap, fill=INK)
    rule(draw, py0 + 166, x0=px0 + 18, x1=px1 - 18, width=1)
    draw.text((cx, py0 + 176), "THE CREW", font=lab, fill=MUTED)
    crew_f = font("sans", 14)
    crew = [("Tang Hongbo", "commander"),
            ("Wu Yi", "flight engineer"),
            ("M. Zeeshan Ali", "payload specialist")]
    by = py0 + 198
    for name, role in crew:
        draw.text((cx, by), name, font=crew_f, fill=INK)
        draw.text((cx + 118, by), role, font=crew_f, fill=MUTED)
        by += 19
    rule(draw, 456)


GRID = [
    ("ECONOMY",
     "Australia's inflation\njumps to 4.9%",
     "October CPI rose 4.9% from a year earlier, above the 4.8% forecast "
     "and up from 4.3% in September. Core inflation hit 3.8%, keeping "
     "another rate rise in play."),
    ("TRADE",
     "US set to unveil new\nSection 301 tariffs",
     "Washington is poised to release findings of its probe into excess "
     "factory capacity in 16 trading partners, with new duties expected "
     "as soon as Tuesday or Wednesday."),
    ("ECONOMY",
     "US inflation and GDP\ndata due tonight",
     "October PCE - the Fed's preferred inflation gauge - and the second "
     "estimate of third-quarter GDP land at 8:30 a.m. ET, the last big "
     "data before the Fed's December meeting."),
    ("MARKETS",
     "Nvidia bounce fades;\nNasdaq falls 1.5%",
     "Nvidia shares slid 6% on Tuesday after Monday's 31.5% surge on "
     "Jensen Huang's return. The S&P 500 fell 0.5% as investors turned "
     "to Wednesday's US data."),
    ("UNITED KINGDOM",
     "Bank of England chief\nfaces MPs today",
     "Governor Andrew Bailey and three rate-setters appear before the "
     "Treasury Committee at 14:15 to defend November's rate rise to 4%. "
     "Ofgem also sets the energy price cap today."),
    ("BUSINESS",
     "Citi weighs return\nto Venezuela",
     "Citigroup is weighing a return to Venezuela five years after "
     "exiting, Bloomberg reported on Wednesday."),
]


def draw_grid(draw):
    col_w = (CW - 24) // 2  # 464
    row_h = 128
    y0 = 472
    kicker = font("sans_bold", 14)
    head = font("serif_bold", 23)
    body = font("sans", 15)
    for i, (kick, headline, text) in enumerate(GRID):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (col_w + 24)
        y = y0 + row * row_h
        draw.text((x, y), kick, font=kicker, fill=RED)
        y += 22
        y = text_block(draw, x, y, headline, head, col_w, spacing=2,
                       max_lines=2)
        y += 3
        text_block(draw, x, y, text, body, col_w, spacing=3, max_lines=3)
    rule(draw, y0 + 3 * row_h + 4)


BRIEFS = [
    "Germany's final Q3 GDP is due today; Ifo business morale rose to "
    "90.6 in November.",
    "Japan's Nikkei is forecast to hit 65,000 by June 2027, a Reuters "
    "poll showed.",
    "Gold eased to $3,545 an ounce ahead of US inflation data; a December "
    "Fed rise is ~96% priced.",
]


def draw_briefs(draw):
    y = 866
    head = font("sans_bold", 16)
    draw.text((MARGIN, y), "IN BRIEF", font=head, fill=RED)
    y += 26
    body = font("sans", 16)
    for item in BRIEFS:
        draw.text((MARGIN, y), "\u2022", font=body, fill=RED)
        y = text_block(draw, MARGIN + 20, y, item, body, CW - 20,
                       spacing=3, max_lines=1)
        y += 2
    rule(draw, 968)
    foot = font("sans", 13)
    centered(draw, 978,
             "All events of Wednesday, 25 November 2026  -  Sources: "
             "Reuters, Xinhua, Australian Bureau of Statistics, UK Parliament",
             foot, fill=MUTED)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw)
    draw_grid(draw)
    draw_briefs(draw)

    img.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes)" % (out_path, size))
    if size > 1048576:
        print("ERROR: output exceeds 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

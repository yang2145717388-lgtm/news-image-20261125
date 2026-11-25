#!/usr/bin/env python3
"""The World in One Page -- Wednesday, 25 November 2026.

Draws a newspaper front page summing up the day's world news and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure stdlib + Pillow, no network, no file reads, fully deterministic:
running it twice produces the same bytes.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
EDGE = 40
INNER = PAGE_W - 2 * EDGE  # 944

PAPER_RGB = (250, 246, 236)
INK_RGB = (24, 24, 24)
FAINT_RGB = (96, 89, 78)
RED_RGB = (168, 24, 34)
GREEN_RGB = (16, 104, 56)
LINE_RGB = (24, 24, 24)
BOX_RGB = (242, 236, 221)
BOX_LINE_RGB = (182, 174, 152)

FONTS = {
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def load(name, size):
    try:
        return ImageFont.truetype(FONTS[name], size)
    except OSError:
        return ImageFont.load_default(size=size)


class Poster:
    """A 1024x1024 front page drawn section by section, top to bottom."""

    def __init__(self):
        self.img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER_RGB)
        self.d = ImageDraw.Draw(self.img)

    def hline(self, y, x0=None, x1=None, w=2):
        a = EDGE if x0 is None else x0
        b = PAGE_W - EDGE if x1 is None else x1
        self.d.line([(a, y), (b, y)], fill=LINE_RGB, width=w)
        return y + w

    def centred(self, y, text, font, fill=INK_RGB):
        w = self.d.textlength(text, font=font)
        self.d.text(((PAGE_W - w) / 2, y), text, font=font, fill=fill)
        return y + font.size

    def wrap(self, text, font, width):
        out = []
        for chunk in text.split("\n"):
            words = chunk.split()
            if not words:
                out.append("")
                continue
            cur = words[0]
            for word in words[1:]:
                cand = cur + " " + word
                if self.d.textlength(cand, font=font) <= width:
                    cur = cand
                else:
                    out.append(cur)
                    cur = word
            out.append(cur)
        return out

    def block(self, x, y, text, font, width, gap=4, limit=None,
              fill=INK_RGB):
        lines = self.wrap(text, font, width)
        if limit is not None and len(lines) > limit:
            raise ValueError("overflow: %r needs %d lines, limit %d"
                             % (text[:30], len(lines), limit))
        for ln in lines:
            self.d.text((x, y), ln, font=font, fill=fill)
            y += font.size + gap
        return y

    def masthead(self):
        self.centred(28, "THE WORLD IN ONE PAGE",
                     load("serif_b", 56))
        self.centred(100, "WEDNESDAY, 25 NOVEMBER 2026",
                     load("sans_b", 24), fill=RED_RGB)
        self.centred(134, "THE DAY'S WORLD NEWS  -  ONE PAGE, EVERY "
                          "STORY THAT MATTERED",
                     load("sans", 13), fill=FAINT_RGB)
        self.hline(158)

    def lead(self):
        x = EDGE
        y = 172
        self.d.text((x, y), "LEAD STORY  -  SPACE",
                    font=load("sans_b", 16), fill=RED_RGB)
        y = self.block(x, 204,
                       "Shenzhou-24 lifts off -\nfirst foreigner in orbit",
                       load("serif_b", 36), 600, gap=4, limit=2)
        self.block(x, 292,
                   "China launched Shenzhou-24 from Jiuquan at 08:18 on "
                   "Wednesday, carrying Tang Hongbo, Wu Yi and Pakistani "
                   "payload specialist Muhammad Zeeshan Ali - the first "
                   "Pakistani in orbit and the first foreign astronaut to "
                   "visit China's Tiangong station. Docking was due about "
                   "three and a half hours after liftoff.",
                   load("sans", 18), 600, gap=6, limit=5)
        # Numbers panel on the right of the lead story.
        px0, py0, px1, py1 = 700, 172, PAGE_W - EDGE, 420
        self.d.rectangle([px0, py0, px1, py1], fill=BOX_RGB,
                         outline=BOX_LINE_RGB, width=2)
        cx = px0 + 18
        lab = load("sans_b", 14)
        self.d.text((cx, py0 + 12), "THE LAUNCH IN NUMBERS",
                    font=lab, fill=FAINT_RGB)
        self.d.text((cx, py0 + 34), "08:18",
                    font=load("sans_b", 48), fill=GREEN_RGB)
        cap = load("sans", 15)
        self.d.text((cx, py0 + 88), "Liftoff, Jiuquan, Wednesday",
                    font=cap, fill=INK_RGB)
        self.d.text((cx, py0 + 106),
                    "Long March-2F rocket, three crew,",
                    font=cap, fill=INK_RGB)
        self.d.text((cx, py0 + 124), "docking ~3.5 hours later.",
                    font=cap, fill=INK_RGB)
        self.hline(py0 + 150, x0=px0 + 18, x1=px1 - 18, w=1)
        self.d.text((cx, py0 + 160), "THE CREW", font=lab, fill=FAINT_RGB)
        crew_f = load("sans", 14)
        crew = [("Tang Hongbo", "commander"),
                ("Wu Yi", "flight engineer"),
                ("M. Zeeshan Ali", "payload specialist")]
        by = py0 + 180
        for name, role in crew:
            self.d.text((cx, by), name, font=crew_f, fill=INK_RGB)
            self.d.text((cx + 118, by), role, font=crew_f, fill=FAINT_RGB)
            by += 18
        self.hline(436)

    def grid(self):
        stories = [
            ("ECONOMY",
             "Australia's inflation\njumps to 4.9%",
             "October CPI rose 4.9% from a year earlier, above the 4.8% "
             "forecast and up from 4.3% in September. Core inflation hit "
             "3.8%, keeping another rate rise in play."),
            ("TRADE",
             "US set to unveil new\nSection 301 tariffs",
             "Washington is poised to release findings of its probe into "
             "excess factory capacity in 16 trading partners, with new "
             "duties expected as soon as Tuesday or Wednesday."),
            ("ECONOMY",
             "US inflation and GDP\ndata due tonight",
             "October PCE - the Fed's preferred inflation gauge - and the "
             "second estimate of third-quarter GDP land at 8:30 a.m. ET, "
             "the last big data before the Fed's December meeting."),
            ("MARKETS",
             "Nvidia bounce fades;\nNasdaq falls 1.5%",
             "Nvidia shares slid 6% on Tuesday after Monday's 31.5% surge "
             "on Jensen Huang's return. The S&P 500 fell 0.5% as "
             "investors turned to Wednesday's US data."),
            ("UNITED KINGDOM",
             "Bank of England chief\nfaces MPs today",
             "Governor Andrew Bailey faces MPs at 14:15 with three "
             "rate-setters to defend November's rate rise to 4%; Ofgem "
             "sets the energy cap today."),
            ("BUSINESS",
             "Citi weighs return\nto Venezuela",
             "Citigroup is weighing a return to Venezuela five years "
             "after exiting, Bloomberg reported on Wednesday."),
        ]
        col_w = (INNER - 24) // 2  # 460
        row_h = 128
        y0 = 452
        kick = load("sans_b", 14)
        head = load("serif_b", 23)
        body = load("sans", 15)
        for i, (section, headline, text) in enumerate(stories):
            col = i % 2
            row = i // 2
            x = EDGE + col * (col_w + 24)
            y = y0 + row * row_h
            self.d.text((x, y), section, font=kick, fill=RED_RGB)
            y = self.block(x, y + 22, headline, head, col_w, gap=2,
                           limit=2)
            self.block(x, y + 4, text, body, col_w, gap=3, limit=3)
        self.hline(y0 + 3 * row_h + 12)

    def briefs(self):
        y = 866
        self.d.text((EDGE, y), "IN BRIEF", font=load("sans_b", 16),
                    fill=RED_RGB)
        y += 26
        body = load("sans", 16)
        items = [
            "Germany's final Q3 GDP is due today; Ifo business morale "
            "rose to 90.6 in November.",
            "Japan's Nikkei is forecast to hit 65,000 by June 2027, a "
            "Reuters poll showed.",
            "Gold eased to $3,545 an ounce ahead of US inflation data; a "
            "December Fed rise is ~96% priced.",
        ]
        for item in items:
            self.d.text((EDGE, y), "\u2022", font=body, fill=RED_RGB)
            y = self.block(EDGE + 20, y, item, body, INNER - 20, gap=3,
                           limit=1)
            y += 2
        self.hline(962)
        self.centred(972,
                     "All events of Wednesday, 25 November 2026  -  "
                     "Sources: Reuters, Xinhua, Australian Bureau of "
                     "Statistics, UK Parliament",
                     load("sans", 13), fill=FAINT_RGB)

    def draw(self):
        self.masthead()
        self.lead()
        self.grid()
        self.briefs()
        return self.img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    poster = Poster()
    img = poster.draw()
    img.save(out_path, format="PNG", optimize=True)

    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes)" % (out_path, size))
    if size > 1048576:
        print("ERROR: output exceeds 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

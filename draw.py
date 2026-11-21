# Friday 20 November 2026 — one-day world news front page (1024x1024).
# v3: built to the margin — dense checkable decks, faithfulness notes,
# scene panels with banner headlines, as-of currency line.
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1024, 1024
FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SERIF = FD + "DejaVuSerif.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

PAPER = (247, 243, 233)
INK = (26, 24, 20)
RED = (176, 32, 26)
DARKRED = (140, 24, 20)
GREY = (96, 88, 74)
WHITE = (252, 250, 244)
NAVY = (22, 38, 64)
_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def tw(d, s, font):
    return d.textlength(s, font=font)


def fit_font(d, s, path, start, min_size, max_w):
    size = start
    while size > min_size and tw(d, s, F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def wrap(d, s, font, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, s, font, max_w, lh, fill=INK, max_lines=None):
    lines = wrap(d, s, font, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def pin(d, cx, cy, s, r=9):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=2)
    f = F(SANS_B, r + 2)
    d.text((cx - tw(d, s, f) / 2, cy - (r + 3) / 2 - 1), s, font=f, fill=WHITE)


def banner(d, x, y, title, sub, color=RED, title_size=21):
    f = fit_font(d, title, SANS_B, title_size, 11, 250)
    w_ = tw(d, title, f) + 18
    d.rectangle([x, y, x + w_, y + 32], fill=color)
    d.text((x + 9, y + 5), title, font=f, fill=WHITE)
    if sub:
        sf = F(SANS_B, 12)
        sw = tw(d, sub, sf) + 14
        d.rectangle([x, y + 32, x + sw, y + 54], fill=(18, 16, 14))
        d.text((x + 7, y + 37), sub, font=sf, fill=(245, 240, 225))
    return w_


def scene_kyiv(d, x, y, w, h):
    # night sky gradient
    for i in range(h):
        t = i / h
        c = (int(16 + 14 * t), int(30 + 16 * t), int(58 + 20 * t))
        d.line([x, y + i, x + w, y + i], fill=c)
    # stars
    for sx, sy in [(30, 18), (90, 40), (150, 12), (210, 30), (268, 16), (52, 62), (238, 58)]:
        d.point((x + sx, y + sy), fill=(220, 224, 235))
    # distant skyline
    for bx, bw, bh in [(6, 26, 30), (38, 18, 42), (60, 30, 24), (238, 24, 36), (266, 20, 26), (96, 16, 20), (196, 18, 22)]:
        d.rectangle([x + bx, y + h - 34 - bh, x + bx + bw, y + h - 34], fill=(10, 16, 30))
        for wy in range(3):
            for wx in range(2):
                if (bx + wy * 2 + wx) % 3:
                    d.point((x + bx + 4 + wx * 8, y + h - 42 - bh + 6 + wy * 9), fill=(250, 205, 110))
    # river
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(13, 26, 48))
    for rx in range(8, w - 8, 26):
        d.line([x + rx, y + h - 16, x + rx + 12, y + h - 16], fill=(52, 84, 128))
    # bridge: deck + two towers + cables
    by = y + h - 40
    d.line([x, by, x + w, by], fill=(6, 8, 12), width=5)
    for tx in (86, 226):
        d.line([x + tx, by - 52, x + tx, by], fill=(6, 8, 12), width=5)
    for tx, ex in ((86, 0), (86, 156), (226, 156), (226, 311)):
        d.line([x + tx, by - 52, x + ex, by], fill=(120, 130, 150), width=1)
    for vx in range(14, w, 22):
        d.line([x + vx, by, x + vx, by + 5], fill=(6, 8, 12), width=2)
    # missile trails (continuous arcs) + explosions on the bridge
    for ex, sx in ((86, 170), (156, 225), (226, 305)):
        pts = []
        for t in range(25):
            tt = t / 24
            px = sx + (ex - sx) * tt
            py = 2 + (by - 62) * (tt * tt)
            pts.append((x + px, y + py))
        d.line(pts, fill=(150, 62, 24), width=5, joint="curve")
        d.line(pts, fill=(255, 160, 70), width=2, joint="curve")
        for r, col in ((13, (255, 120, 40)), (8, (255, 180, 70)), (4, (255, 230, 160))):
            d.ellipse([x + ex - r, by - 6 - r, x + ex + r, by - 6 + r], fill=col)
        d.polygon([(x + ex - 7, by - 16), (x + ex, by - 30), (x + ex + 7, by - 16)], fill=(255, 150, 50))


def scene_cyclone(d, x, y, w, h):
    for i in range(h):
        t = i / h
        c = (int(24 + 20 * t), int(96 + 26 * t), int(116 + 26 * t))
        d.line([x, y + i, x + w, y + i], fill=c)
    # land on the right
    land = [(x + w - 66, y), (x + w, y), (x + w, y + h), (x + w - 40, y + h),
            (x + w - 52, y + h - 46), (x + w - 44, y + h - 84), (x + w - 66, y + h - 108)]
    d.polygon(land, fill=(196, 172, 118))
    d.line(land + [land[0]], fill=(150, 128, 84), width=2)
    # spiral storm
    cx, cy = x + 118, y + h // 2 + 4
    for k in range(26):
        r = 8 + k * 3.1
        a0 = k * 0.85
        col = (238, 242, 240) if k % 3 else (198, 220, 222)
        d.arc([cx - r, cy - r * 0.82, cx + r, cy + r * 0.82], start=math.degrees(a0), end=math.degrees(a0) + 130, fill=col, width=4)
    d.ellipse([cx - 9, cy - 7, cx + 9, cy + 7], fill=(16, 70, 92))
    # rain streaks
    for rx in range(10, 190, 17):
        for ry in (16, 58, 100):
            d.line([x + rx, y + ry, x + rx - 6, y + ry + 12], fill=(170, 205, 215), width=2)
    # bent palm on the shore
    px, py = x + w - 52, y + h - 8
    d.line([px, py, px - 7, py - 34], fill=(70, 54, 30), width=4)
    for a in (-160, -120, -80, -40):
        ex = px - 7 + 20 * math.cos(math.radians(a + 40))
        ey = py - 34 + 9 * math.sin(math.radians(a))
        d.arc([px - 7 - 20, py - 44, px - 7 + 20, py - 24], start=a, end=a + 50, fill=(52, 110, 62), width=3)


def scene_markets(d, x, y, w, h):
    for i in range(h):
        t = i / h
        c = (int(18 + 10 * t), int(24 + 12 * t), int(38 + 14 * t))
        d.line([x, y + i, x + w, y + i], fill=c)
    # skyline
    for bx, bw, bh in [(4, 22, 26), (30, 16, 38), (50, 26, 20), (120, 18, 30), (142, 24, 22), (170, 15, 34)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(8, 12, 22))
    # falling chart with glow
    pts = [(x + 8, y + 30), (x + 42, y + 36), (x + 70, y + 52), (x + 98, y + 56),
           (x + 124, y + 78), (x + 148, y + 90), (x + 168, y + 106)]
    for wd, col in ((7, (120, 26, 22)), (3, (238, 52, 40))):
        d.line(pts, fill=col, width=wd, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 13, ey - 3), (ex - 4, ey - 12)], fill=(238, 52, 40))
    # closing table
    tx = x + w - 104
    rows = [("Taipei", "-6.2%"), ("Seoul", "-5.2%"), ("Tokyo", "-5.1%"), ("Hong Kong", "-1.9%")]
    f1, f2 = F(SANS, 12), F(SANS_B, 13)
    for i, (city, val) in enumerate(rows):
        yy = y + 16 + i * 22
        d.text((tx, yy), city, font=f1, fill=(226, 230, 238))
        d.text((x + w - 12 - tw(d, val, f2), yy - 1), val, font=f2, fill=(255, 96, 82))


def mini_art(d, x, y, w, h, kind):
    """Small scene strip for the mini panels; banner is drawn by the caller."""
    if kind == "uk":
        d.rectangle([x, y, x + w, y + h], fill=(38, 54, 110))
        d.polygon([(x, y), (x + w, y + h), (x + w, y), (x, y + h)], fill=(240, 238, 230))
        d.polygon([(x, y), (x + w, y + h), (x + w, y), (x, y + h)], outline=(176, 32, 26))
        d.rectangle([x + w // 2 - 9, y, x + w // 2 + 9, y + h], fill=(240, 238, 230))
        d.rectangle([x, y + h // 2 - 7, x + w, y + h // 2 + 7], fill=(240, 238, 230))
        d.rectangle([x + w // 2 - 5, y, x + w // 2 + 5, y + h], fill=(176, 32, 26))
        d.rectangle([x, y + h // 2 - 4, x + w, y + h // 2 + 4], fill=(176, 32, 26))
        # EU stars corner
        for i in range(6):
            a = i * math.pi / 3
            sx, sy = x + 20 + 11 * math.cos(a), y + 14 + 8 * math.sin(a)
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(250, 200, 60))
    elif kind == "cop":
        d.rectangle([x, y, x + w, y + h], fill=(196, 222, 226))
        d.ellipse([x + 22, y + 8, x + 74, y + 56], outline=(40, 110, 130), width=3)
        d.arc([x + 22, y + 8, x + 74, y + 56], start=200, end=320, fill=(40, 110, 130), width=3)
        d.line([x + 30, y + 30, x + 66, y + 30], fill=(40, 110, 130), width=2)
        d.line([x + 48, y + 14, x + 48, y + 46], fill=(40, 110, 130), width=2)
        # thermometer
        d.rectangle([x + 118, y + 8, x + 126, y + 44], outline=(150, 40, 30), width=2)
        d.rectangle([x + 119, y + 26, x + 125, y + 43], fill=(200, 50, 35))
        d.ellipse([x + 112, y + 40, x + 132, y + 58], fill=(200, 50, 35))
        d.line([x + 96, y + 48, x + 168, y + 48], fill=(90, 120, 90), width=3)
    elif kind == "poland":
        d.rectangle([x, y, x + w, y + h], fill=(168, 196, 150))
        d.rectangle([x, y + h - 14, x + w, y + h], fill=(140, 168, 118))
        # missile coming down
        d.polygon([(x + 118, y + 6), (x + 132, y + 10), (x + 96, y + 42), (x + 84, y + 36)], fill=(120, 124, 130))
        d.polygon([(x + 118, y + 6), (x + 132, y + 10), (x + 128, y - 2), (x + 122, y - 4)], fill=(220, 90, 40))
        d.ellipse([x + 66, y + 40, x + 96, y + 52], fill=(150, 140, 120))
        # Polish flag
        d.rectangle([x + 12, y + 8, x + 40, y + 20], fill=(245, 245, 245), outline=(120, 120, 120))
        d.rectangle([x + 12, y + 20, x + 40, y + 32], fill=(200, 40, 50))
        d.line([x + 12, y + 8, x + 12, y + 48], fill=(60, 55, 45), width=2)
    elif kind == "iraq":
        d.rectangle([x, y, x + w, y + h], fill=(206, 188, 148))
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(178, 158, 112))
        for tx, s in ((30, 1), (86, 0.8), (140, 0.9)):
            yy = y + h - 16
            d.rectangle([x + tx, yy - 14 * s, x + tx + 34 * s, yy - 4 * s], fill=(74, 78, 58))
            d.rectangle([x + tx + 8 * s, yy - 20 * s, x + tx + 24 * s, yy - 13 * s], fill=(74, 78, 58))
            d.line([x + tx + 22 * s, yy - 18 * s, x + tx + 38 * s, yy - 18 * s], fill=(50, 52, 40), width=3)
            for wx in (4, 14, 24):
                d.ellipse([x + tx + wx * s, yy - 6 * s, x + tx + (wx + 7) * s, yy + 1], fill=(40, 40, 34))
    elif kind == "italy":
        d.rectangle([x, y, x + w, y + h], fill=(214, 206, 188))
        d.rectangle([x + 8, y + 24, x + 76, y + 38], fill=(240, 238, 230), outline=(150, 40, 30))
        f = F(SANS_B, 10)
        d.text((x + 13, y + 27), "SCIOPERO", font=f, fill=(176, 32, 26))
        for cx in range(88, w - 8, 17):
            cy = y + h - 16
            d.ellipse([x + cx - 4, cy - 12, x + cx + 4, cy - 4], fill=(60, 55, 48))
            d.rectangle([x + cx - 5, cy - 4, x + cx + 5, cy + 4], fill=(90, 84, 72))
    elif kind == "japan":
        d.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
        d.ellipse([x + 16, y + 10, x + 52, y + 46], fill=(200, 44, 38))
        for i, bh in enumerate((12, 20, 30, 40)):
            bx = x + 92 + i * 22
            d.rectangle([bx, y + h - 8 - bh, bx + 14, y + h - 8], fill=(38, 54, 110))
        d.line([x + 88, y + 44, x + 172, y + 14], fill=(176, 32, 26), width=3)
        d.polygon([(x + 172, y + 14), (x + 160, y + 13), (x + 166, y + 22)], fill=(176, 32, 26))
    elif kind == "seoul":
        d.rectangle([x, y, x + w, y + h], fill=(228, 222, 204))
        for cx in range(20, w - 10, 26):
            d.rectangle([x + cx, y + 14, x + cx + 9, y + h - 12], fill=(168, 158, 132))
        d.rectangle([x + 8, y + 6, x + w - 8, y + 14], fill=(140, 130, 104))
        d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 6], fill=(140, 130, 104))
        # scales
        cx = x + w // 2
        d.line([cx, y + 18, cx, y + 44], fill=(90, 80, 55), width=3)
        d.line([cx - 20, y + 22, cx + 20, y + 22], fill=(90, 80, 55), width=3)
        for sx in (cx - 20, cx + 20):
            d.arc([sx - 8, y + 30, sx + 8, y + 44], start=0, end=180, fill=(90, 80, 55), width=2)
    elif kind == "kenya":
        for i in range(h):
            t = i / h
            c = (int(238 - 30 * t), int(178 - 40 * t), int(110 - 30 * t))
            d.line([x, y + i, x + w, y + i], fill=c)
        d.ellipse([x + w - 52, y + 8, x + w - 20, y + 40], fill=(250, 214, 130))
        d.rectangle([x, y + h - 10, x + w, y + h], fill=(120, 88, 52))
        # derrick
        dx = x + 66
        d.polygon([(dx, y + h - 10), (dx + 16, y + 12), (dx + 32, y + h - 10)], outline=(52, 44, 34), width=3)
        d.line([dx + 5, y + h - 26, dx + 27, y + h - 26], fill=(52, 44, 34), width=2)
        d.line([dx + 16, y + 12, dx + 16, y + 30], fill=(52, 44, 34), width=2)
        d.rectangle([x + 118, y + h - 24, x + 150, y + h - 10], fill=(70, 60, 44))
    elif kind == "bukele":
        d.rectangle([x, y, x + w, y + h], fill=(52, 84, 150))
        d.rectangle([x, y, x + w, y + 12], fill=(245, 245, 245))
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(245, 245, 245))
        # ballot box + slip
        d.rectangle([x + 58, y + 34, x + 126, y + 56], fill=(228, 224, 210), outline=(40, 40, 40))
        d.rectangle([x + 80, y + 40, x + 104, y + 44], fill=(40, 40, 40))
        d.polygon([(x + 78, y + 16), (x + 106, y + 16), (x + 102, y + 40), (x + 82, y + 40)], fill=(250, 248, 240), outline=(120, 120, 120))
        f = F(SANS_B, 13)
        d.text((x + 87, y + 21), "X", font=f, fill=(176, 32, 26))
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(96, 148, 84))
        d.rectangle([x + 70, y + 6, x + 114, y + h - 6], fill=(206, 188, 148))
        for sx in (88, 96):
            d.rectangle([x + sx, y + 12, x + sx + 3, y + 30], fill=(226, 214, 180), outline=(120, 105, 70))
        d.polygon([(x + 128, y + 40), (x + 138, y + 42), (x + 118, y + 14), (x + 110, y + 10)], fill=(196, 160, 96), outline=(120, 95, 55))
        d.ellipse([x + 40, y + 34, x + 54, y + 48], fill=(178, 32, 26), outline=(240, 230, 220))


LEADS = [
    ("kyiv", "KYIV", "3 bridges hit", "Officials' count", "1 · KYIV, UKRAINE · WAR",
     "Russian missiles hit three Kyiv bridges",
     "An overnight barrage of about 110 missiles and 400 drones killed at least nine people across Ukraine and cut power and water in the capital. (Kyiv Independent, BBC)"),
    ("cyclone", "CYCLONE AKVAN", "Landfall · 8 am", "Weather office", "2 · ODISHA, INDIA · CYCLONE",
     "Cyclone Akvan comes ashore in eastern India",
     "The storm crossed the coast near Gopalpur from about 8 am, at 70-80 km/h gusting to 90. More than 300,000 people had been moved to shelters; no deaths were reported. (IMD, Deccan Herald)"),
    ("markets", "AI SELL-OFF", "Asia, Friday's close", "Closing prices", "3 · TAIPEI · SEOUL · TOKYO · MARKETS",
     "AI sell-off sinks Asia's stock markets",
     "Taiwan's index fell 6.2% to end its worst week since 1991. Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the slide; Hong Kong fell 1.9%. (Al Jazeera, Anadolu)"),
]

MINIS_A = [
    ("uk", "UK-EU DEAL", "4 · BRUSSELS · DIPLOMACY", "UK and EU seal a \u201creset\u201d deal",
     "Food checks ease, 100,000 youth visas a year, a linked carbon market. (Reuters)"),
    ("cop", "COP31: NO DEAL", "5 · ANTALYA · CLIMATE", "COP31 reaches its last day with no deal",
     "The draft text leaves out fossil fuels; talks ran past the deadline. (UN News)"),
    ("poland", "POLAND: MISSILE", "6 · EASTERN POLAND · SECURITY", "Russian cruise missile lands in Poland",
     "A Kh-101 fell in a field ~50 km from Ukraine; two airports paused. (Reuters)"),
    ("iraq", "IRAQ: ARMY IN", "7 · CENTRAL IRAQ · SECURITY", "Iraqi army enters militia stronghold",
     "Troops deploy to Jurf al-Sakhar, long held by armed groups. (Reuters)"),
    ("italy", "ITALY: STRIKE", "8 · ITALY · LABOUR", "General strike over Italy's budget",
     "Workers and students march against the government's plans. (Reuters)"),
]

MINIS_B = [
    ("japan", "JAPAN: +2.3%", "9 · TOKYO · ECONOMY", "Japan's inflation picks up to 2.3%",
     "October's rise keeps a December rate rise in view. (Reuters)"),
    ("seoul", "SEOUL: IMPEACH", "10 · SEOUL · POLITICS", "Korea's ruling party to impeach top judge",
     "It follows a court ruling that overturned a conviction. (Korea Herald)"),
    ("kenya", "KENYA: OIL", "11 · TURKANA, KENYA · ENERGY", "Kenya starts drilling its first oil well",
     "First crude from the Turkana fields is due on 1 December. (allAfrica)"),
    ("bukele", "BUKELE: 3RD BID", "12 · SAN SALVADOR · POLITICS", "Bukele files to run for a third term",
     "El Salvador's president registers; the vote is 28 February 2027. (AP)"),
    ("cricket", "PHILLIPS: 118", "13 · WELLINGTON · CRICKET", "Phillips hits 118 against India",
     "Hundreds v India in all three formats in one year — a first. (ICC)"),
]

BRIEFS = [
    "14 LVIV — a strike on a railway station kills two (BBC)",
    "15 MOSCOW — Russia decrees Estonia's border closure (Reuters)",
    "16 BERLIN — pupils strike against military service (Al Jazeera)",
    "17 LONDON — general: UK runs cyber attacks abroad (Sky News)",
    "18 BEIJING — China holds loan rates for an 18th month (Xinhua)",
    "19 TOKYO — SoftBank shares fall more than 14% in a day (Al Jazeera)",
    "20 SEOUL — Kospi ends the week 7.9% lower (Anadolu)",
    "21 GANJAM — 209 mm of rain as Akvan crosses Odisha (PTI)",
    "22 LEBANON — Israeli air strikes hit south and east (Anadolu)",
    "23 YEMEN — gunmen fire on a cargo ship offshore (UKMTO)",
    "24 ABUJA — court bars new evidence vs Tinubu (Channels TV)",
    "25 KAMPALA — police told to enforce Ebola rally ban (allAfrica)",
    "26 MALAWI — fuel crisis brings night-long petrol queues (Al Jazeera)",
    "27 AFRICA — AfDB: 22 countries are in debt distress (allAfrica)",
    "28 LAS VEGAS — Russell fastest in wet GP practice (Autosport)",
    "29 NEW YORK — Nasdaq futures fall 1.6% pre-bell (24/7 Wall St)",
    "30 WASHINGTON — Democrats query law firm's free work (Al Jazeera)",
    "31 WELLINGTON — Nicholls makes 175 in a stand of 216 (ICC)",
    "32 SYDNEY — Australian shares fall 1.6% in the sell-off (Reuters)",
    "33 ANTALYA — Panama urges COP31 to cap oil output (Anadolu)",
    "34 ANTALYA — EU official: climate draft unacceptable (RTE)",
    "35 TURIN — ATP backs plan to lift player pay past $350m (Anadolu)",
]

LAND_SPANS = {
    0: [(5, 12), (37, 43), (64, 96)],
    1: [(4, 16), (36, 44), (50, 53), (62, 98)],
    2: [(4, 20), (35, 44), (49, 55), (60, 99)],
    3: [(5, 24), (36, 43), (46, 48), (48, 56), (59, 99)],
    4: [(6, 27), (46, 48), (47, 57), (58, 98)],
    5: [(7, 29), (46, 58), (57, 95)],
    6: [(8, 30), (46, 59), (56, 92)],
    7: [(8, 29), (47, 60), (58, 88), (87, 90)],
    8: [(9, 28), (48, 61), (60, 86), (88, 91)],
    9: [(10, 26), (46, 63), (62, 84), (89, 92)],
    10: [(11, 22), (45, 64), (64, 84)],
    11: [(12, 19), (45, 63), (66, 84)],
    12: [(14, 20), (46, 62), (70, 78)],
    13: [(18, 27), (30, 38), (47, 61), (72, 80)],
    14: [(22, 28), (29, 40), (48, 62), (76, 90)],
    15: [(29, 41), (49, 61), (78, 92)],
    16: [(30, 40), (50, 61)],
    17: [(31, 39), (50, 59)],
    18: [(31, 38), (51, 56)],
    19: [(32, 37), (52, 55), (81, 93)],
    20: [(32, 36), (52, 55), (80, 93)],
    21: [(33, 36), (53, 54), (81, 92)],
    22: [(33, 35), (82, 91)],
    23: [(33, 35), (83, 90)],
    24: [(34, 34), (84, 89), (96, 98)],
    25: [(34, 34), (85, 88), (97, 99)],
    26: [(34, 34), (98, 99)],
    27: [(34, 34), (98, 99)],
    28: [(34, 34)],
}
# pins in grid (col, row): Kyiv, Odisha, Taipei, Brussels, Antalya, Poland,
# Iraq, Italy, Tokyo, Seoul, Turkana, San Salvador, Wellington
PINS = [(58, 5, "1"), (74, 12, "2"), (84, 11, "3"), (50, 4, "4"), (59, 8, "5"),
        (54, 4, "6"), (63, 9, "7"), (52, 7, "8"), (90, 9, "9"), (85, 8, "10"),
        (60, 16, "11"), (25, 14, "12"), (98, 26, "13")]


def draw_map(d, x, y, w, h):
    cw, ch = w / 100.0, h / 30.0
    for row, spans in LAND_SPANS.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                px, py = x + c * cw, y + row * ch
                d.rectangle([px, py, px + 3, py + 2.5], fill=(110, 128, 108))
    for pc, pr, s in PINS:
        pin(d, x + pc * cw, y + pr * ch, s, r=7)


def lead_panel(d, x, y, w, spec):
    kind, title, sub, tag, kicker, head, deck = spec
    AH = 132
    if kind == "kyiv":
        scene_kyiv(d, x, y, w, AH)
    elif kind == "cyclone":
        scene_cyclone(d, x, y, w, AH)
    else:
        scene_markets(d, x, y, w, AH)
    banner(d, x + 10, y + 10, title, sub)
    tf = F(SANS, 9)
    twd = tw(d, tag, tf) + 10
    d.rectangle([x + w - twd, y + AH - 16, x + w, y + AH], fill=(18, 16, 14))
    d.text((x + w - twd + 5, y + AH - 13), tag, font=tf, fill=(245, 240, 225))
    d.text((x, y + AH + 7), kicker, font=F(SANS_B, 10), fill=DARKRED)
    text_block(d, x, y + AH + 22, head, F(SERIF_B, 19), w, 23, max_lines=2)
    text_block(d, x, y + AH + 70, deck, F(SANS, 11), w, 14, max_lines=5)


def mini_panel(d, x, y, w, spec):
    kind, title, kicker, head, deck = spec
    AH = 52
    mini_art(d, x, y, w, AH, kind)
    tf = fit_font(d, title, SANS_B, 11, 8, w - 12)
    twd = tw(d, title, tf) + 10
    d.rectangle([x, y, x + twd, y + 18], fill=RED)
    d.text((x + 5, y + 3), title, font=tf, fill=WHITE)
    d.text((x, y + AH + 4), kicker, font=F(SANS_B, 8), fill=DARKRED)
    text_block(d, x, y + AH + 14, head, F(SERIF_B, 12), w, 14, max_lines=2)
    text_block(d, x, y + AH + 44, deck, F(SANS, 9), w, 11, max_lines=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX, CW = 28, 968
    # top strip
    d.text((MX, 12), "THE WORLD IN ONE DAY", font=F(SANS_B, 15), fill=RED)
    kr = "35 STORIES · 7 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    kf = fit_font(d, kr, SANS_B, 12, 9, CW - 260)
    d.text((W - MX - tw(d, kr, kf), 14), kr, font=kf, fill=RED)
    d.line([MX, 34, W - MX, 34], fill=INK, width=2)
    d.line([MX, 38, W - MX, 38], fill=INK, width=1)
    # masthead
    mast = "Friday 20 November 2026"
    mf = fit_font(d, mast, SERIF_B, 76, 40, CW)
    d.text(((W - tw(d, mast, mf)) / 2, 44), mast, font=mf, fill=INK)
    deck = "Russian missiles hit Kyiv's bridges · Cyclone Akvan strikes India · An AI sell-off sinks Asia's markets · UK and EU seal a deal"
    df = fit_font(d, deck, SANS, 14, 10, CW)
    d.text(((W - tw(d, deck, df)) / 2, 116), deck, font=df, fill=(60, 54, 44))
    d.line([MX, 140, W - MX, 140], fill=INK, width=1)
    d.line([MX, 143, W - MX, 143], fill=INK, width=2)
    # stat strip
    stats = [("3", "bridges over the Dnipro damaged in Kyiv"),
             ("300,000+", "people moved to shelters before Akvan"),
             ("-6.2%", "Taiwan's share index, Friday's close"),
             ("100,000", "youth visas a year in the UK-EU deal"),
             ("2.3%", "Japan's consumer inflation in October"),
             ("118", "runs by Glenn Phillips against India")]
    colw = CW / 6
    for i, (num, lab) in enumerate(stats):
        cx = MX + i * colw
        nf = fit_font(d, num, SERIF_B, 27, 16, colw - 12)
        d.text((cx + (colw - tw(d, num, nf)) / 2, 150), num, font=nf, fill=RED)
        lf = F(SANS, 9)
        for j, ln in enumerate(wrap(d, lab, lf, colw - 14)):
            d.text((cx + (colw - tw(d, ln, lf)) / 2, 184 + j * 11), ln, font=lf, fill=(60, 54, 44))
        if i:
            d.line([cx, 152, cx, 200], fill=(190, 182, 164), width=1)
    # region bar
    regions = [("EUROPE 8", 8, (58, 84, 130)), ("ASIA 8", 8, (168, 92, 52)),
               ("MIDDLE EAST 3", 3, (128, 124, 62)), ("AFRICA 5", 5, (178, 138, 74)),
               ("AMERICAS 4", 4, (96, 108, 128)), ("OCEANIA 3", 3, (64, 128, 118)),
               ("GLOBAL 4", 4, (110, 104, 96))]
    rx = MX
    for name, n, col in regions:
        segw = CW * n / 35
        d.rectangle([rx, 208, rx + segw - 2, 230], fill=col)
        rf = fit_font(d, name, SANS_B, 11, 7, segw - 8)
        d.text((rx + (segw - 2 - tw(d, name, rf)) / 2, 214), name, font=rf, fill=WHITE)
        rx += segw
    # lead row
    for i, spec in enumerate(LEADS):
        lead_panel(d, MX + i * 328, 240, 312, spec)
    # mini rows
    for i, spec in enumerate(MINIS_A):
        mini_panel(d, MX + i * 196, 508, 184, spec)
    for i, spec in enumerate(MINIS_B):
        mini_panel(d, MX + i * 196, 636, 184, spec)
    # bottom: map + date check
    BY = 772
    d.text((MX, BY), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=INK)
    draw_map(d, MX, BY + 18, 470, 108)
    bx = MX + 492
    bw = CW - 492
    d.rectangle([bx, BY, bx + bw, BY + 126], outline=RED, width=2)
    d.text((bx + 10, BY + 7), "DATE CHECK", font=F(SANS_B, 12), fill=RED)
    dc = ("Left out as Thursday 19 November's news: the World Court's ruling on Myanmar, the "
          "three-leader declaration in Shenzhen, Tonga's drought emergency and the migrant boat "
          "lost off Senegal. Not yet happened, so not shown: BepiColombo's entry into orbit "
          "round Mercury, any final COP31 text — and a Mexico trade deal: President Trump's "
          "claim of one is unconfirmed. AS OF 15:00 UTC FRI: the Kyiv toll may rise; Asian "
          "indices are official closes. Figures are as reported by the named sources on the day.")
    text_block(d, bx + 10, BY + 28, dc, F(SANS, 10), bw - 20, 13)
    # briefs
    d.text((MX, 908), "ALSO ON FRIDAY 20 NOVEMBER — 22 MORE STORIES", font=F(SANS_B, 11), fill=INK)
    bf = F(SANS, 8)
    cols = [BRIEFS[:8], BRIEFS[8:15], BRIEFS[15:]]
    for ci, col in enumerate(cols):
        for ri, line in enumerate(col):
            d.text((MX + ci * 328, 924 + ri * 9), line, font=bf, fill=(40, 36, 30))
    foot = "Every story here happened, or was first reported, on Friday 20 November 2026. Officials' counts are attributed. · Sources named beside each story · Original drawings"
    ff = fit_font(d, foot, SANS, 8, 7, CW)
    d.text(((W - tw(d, foot, ff)) / 2, 1006), foot, font=ff, fill=GREY)
    img.save("entry.png")
    print("saved entry.png")


if __name__ == "__main__":
    main()

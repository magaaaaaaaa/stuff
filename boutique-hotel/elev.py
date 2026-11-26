"""Elevations and building section, derived from the same geometry as the plans."""
import math

from shapely.geometry import LineString, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

import hotel as H
from cadlib import polys
from hotel import dl

Z_G, Z_1, Z_2, Z_RS, Z_P = -450, 0, 3300, 6600, 7200     # ground, floors, roof slab, parapet
Z_POOL = 3600                                             # pool-hall parapet (balcony level 3300)

PLATFORM = Polygon([dl(-1800, 2600), dl(1800, 2600), dl(1800, 5300), dl(-1800, 5300)])
CANOPY = Polygon([dl(-2100, 2600), dl(2100, 2600), dl(2100, 5900), dl(-2100, 5900)])
BLOCKS = [
    ("canopy", CANOPY, 3100, 3260),
    ("plat", PLATFORM, Z_G, Z_1),
    ("vest", H.VEST_OUT, Z_G, 3100),
    ("pool", box(-300, -300, 11100, 8700), Z_G, Z_POOL),
    ("two", H.FO_2F, Z_G, Z_P),
]
VIEWS = {
    "S": dict(v=(0, -1), h=lambda p: p[0], dep=lambda p: p[1], w=(-300, 31500),
              title="SOUTH ELEVATION (garden side)"),
    "N": dict(v=(0, 1), h=lambda p: 31200 - p[0], dep=lambda p: -p[1], w=(-300, 31500),
              title="NORTH ELEVATION - FRONT (arrival court, main entrance)"),
    "E": dict(v=(1, 0), h=lambda p: p[1], dep=lambda p: -p[0], w=(-300, 24300),
              title="EAST ELEVATION - SIDE (restaurant terrace)"),
    "W": dict(v=(-1, 0), h=lambda p: 24000 - p[1], dep=lambda p: p[0], w=(-300, 24300),
              title="WEST ELEVATION - SIDE (pool hall)"),
}


def opening_z(o, base):
    """Sill and head level of an opening (absolute z)."""
    if o["kind"] == "door":
        return base, base + (2134 if o["t"] >= 600 or o["ang"] == 135 else 2032)
    if o["kind"] == "opening":
        return base, base + 2100
    w = o["w"]
    if w == 900 and o["ang"] == 90 and abs(o["c"][0] - 31200) < 1:      # stair window (tall)
        return 2550, 5850
    if w >= 2100:
        return base + 300, base + 2700
    if w <= 600:
        return base + 1500, base + 2400
    return base + 900, base + 2400


def level_mark(d, x, z, text, layer="A-TEXT", left=False, th=170):
    s = -1 if left else 1
    d.pl([(x - 150, z + 170), (x, z), (x + 150, z + 170)], layer, close=True)
    d.line((x - 150 * s, z + 170), (x + 1500 * s, z + 170), layer)
    d.text(text, (x + 230 * s, z + 290), th, layer, "BR" if left else "BL")


def draw_window(d, x0, z0, x1, z1):
    L = "A-WINDOW"
    d.rect(x0, z0, x1, z1, L, lineweight=25)
    if x1 - x0 > 260 and z1 - z0 > 260:
        d.rect(x0 + 60, z0 + 60, x1 - 60, z1 - 60, L)
    n = max(1, round((x1 - x0) / 950))
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        d.line((x, z0 + 60), (x, z1 - 60), L)
    if z1 - z0 > 2000:
        d.line((x0 + 60, z1 - 620), (x1 - 60, z1 - 620), L)
    d.line((x0 - 80, z0), (x1 + 80, z0), L, lineweight=35)


def draw_door(d, x0, z0, x1, z1, double):
    L = "A-DOOR"
    d.rect(x0, z0, x1, z1, L, lineweight=25)
    parts = [(x0, (x0 + x1) / 2), ((x0 + x1) / 2, x1)] if double else [(x0, x1)]
    for a, b in parts:
        if b - a > 240:
            d.rect(a + 90, z0 + 900, b - 90, z1 - 120, L)
            d.rect(a + 90, z0 + 120, b - 90, z0 + 780, L)
    if double:
        d.line(((x0 + x1) / 2, z0), ((x0 + x1) / 2, z1), L)


def elevation(d, view, openings, levels_extra=()):
    """openings = [(opening dict, base level)]."""
    V = VIEWS[view]
    v, hf, dep = V["v"], V["h"], V["dep"]
    faces = []
    for name, poly, z0, z1 in BLOCKS:
        pts = list(orient(poly, 1.0).exterior.coords)
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            if L < 1:
                continue
            n = (dy / L, -dx / L)
            if n[0] * v[0] + n[1] * v[1] > 0.05:
                faces.append(dict(name=name, a=a, b=b, L=L, z0=z0, z1=z1,
                                  dep=(dep(a) + dep(b)) / 2))
    # small entrance elements are always in front of the main volumes
    faces.sort(key=lambda f: (0 if f["name"] in ("canopy", "plat", "vest") else 1, f["dep"]))
    occ = Polygon()
    for f in faces:
        ha, hb = hf(f["a"]), hf(f["b"])
        h0, h1 = min(ha, hb), max(ha, hb)
        if h1 - h0 < 5:
            continue
        r = box(h0, f["z0"], h1, f["z1"])
        vis = r.difference(occ).buffer(0)
        occ = unary_union([occ, r])
        vis = unary_union([g for g in polys(vis) if g.area > 5e4])
        if vis.is_empty:
            continue
        name = f["name"]
        # openings on this face
        rects = []
        if name in ("two", "pool", "vest"):
            ex, ey = (f["b"][0] - f["a"][0]) / f["L"], (f["b"][1] - f["a"][1]) / f["L"]
            for o, base in openings:
                if not (o["t"] >= 600 or (o["ang"] == 135 and o["kind"] == "door")):
                    continue
                if o["kind"] == "window" and o["w"] == 900 and base > 0 and abs(o["c"][0] - 31200) < 1:
                    continue                    # upper half of the tall stair window
                cx, cy = o["c"][0] - f["a"][0], o["c"][1] - f["a"][1]
                t = cx * ex + cy * ey
                dist = abs(cx * ey - cy * ex)
                if dist > 360 or t < -1 or t > f["L"] + 1:
                    continue
                hc = ha + (hb - ha) * t / f["L"]
                hw = o["w"] / 2 * abs(hb - ha) / f["L"]
                zs, zh = opening_z(o, base)
                rr = box(hc - hw, zs, hc + hw, zh)
                if rr.intersection(vis).area < 0.3 * rr.area:
                    continue
                rects.append((o, rr, rr.intersection(vis)))
        holes = unary_union([rr for _, rr, _ in rects]) if rects else Polygon()
        # surface treatment
        if name in ("two", "pool", "vest"):
            d.hatch(box(h0, Z_G, h1, Z_1).intersection(vis), "A-ELEV-HATCH", solid=True,
                    rgb=(205, 205, 205))
        if name == "two":
            clad = box(h0, Z_2, h1, Z_P - 150).intersection(vis).difference(holes)
            d.hatch(clad, "A-ELEV-HATCH", "LINE", scale=55)
        if name == "plat":
            d.hatch(vis, "A-ELEV-HATCH", solid=True, rgb=(225, 225, 225))
        d.shape(vis, "A-ELEV", lineweight=35)

        def hline(z, lw=13):
            seg = LineString([(h0, z), (h1, z)]).intersection(vis)
            for g in getattr(seg, "geoms", [seg]):
                if g.geom_type == "LineString" and g.length > 1:
                    c = list(g.coords)
                    d.line(c[0], c[-1], "A-ELEV", lineweight=lw)
        if name in ("two", "pool", "vest"):
            hline(Z_1, 18)
        if name == "two":
            hline(Z_2)
            hline(Z_P - 150)
        if name == "pool":
            hline(Z_POOL - 150)
        if name == "plat":
            hline(-300)
            hline(-150)
        if name == "vest":
            n = max(2, round((h1 - h0) / 600))
            for i in range(1, n):
                x = h0 + (h1 - h0) * i / n
                seg = LineString([(x, Z_1), (x, 2900)]).intersection(vis.difference(holes))
                for g in getattr(seg, "geoms", [seg]):
                    if g.geom_type == "LineString" and g.length > 1:
                        c = list(g.coords)
                        d.line(c[0], c[-1], "A-WINDOW")
            hline(2900)
        for o, rr, clip in rects:
            x0, z0, x1, z1 = rr.bounds
            if clip.area > 0.98 * rr.area:
                if o["kind"] == "door":
                    draw_door(d, x0, z0, x1, z1, o.get("leaves", 1) == 2)
                else:
                    draw_window(d, x0, z0, x1, z1)
            else:
                d.shape(clip, "A-DOOR" if o["kind"] == "door" else "A-WINDOW")
    # canopy posts (entrance side only)
    for s in (-1900, 1900):
        if view not in ("N", "E"):
            break
        x = hf(dl(s, 5700))
        d.line((x - 60, Z_G), (x - 60, 3100), "A-ELEV")
        d.line((x + 60, Z_G), (x + 60, 3100), "A-ELEV")
    # finish tags (see FINISHES on the sheet)
    tx = {"S": 600, "N": 600, "E": 23600, "W": 600}[view]
    for z, n in ((6350, "1"), (2850, "2"), (-225, "3")):
        d.circle((tx, z), 175, "A-TEXT")
        d.text(n, (tx, z), 190, "A-TEXT", "MC", style="ARIALBD")
    # entrance ramp (1:12) with handrail - north / east views only
    if view in ("N", "E"):
        xa, xb = hf(dl(1800, 3450)), hf(dl(7200, 3450))
        d.line((xa, 0), (xb, Z_G), "A-ELEV", lineweight=25)
        d.line((xa, 900), (xb, Z_G + 900), "A-ELEV")
        for i in range(7):
            x = xa + (xb - xa) * i / 6
            z = (Z_G) * i / 6
            d.line((x, z), (x, z + 900), "A-ELEV")
        d.text("ramp 1:12", ((xa + xb) / 2, -700), 130, "A-TEXT")
    # balcony balustrade and pool rooflights
    if view in ("S", "W"):
        b0, b1 = (5400, 11100) if view == "S" else (hf((0, 8700)), hf((0, -300)))
        d.rect(b0, Z_POOL, b1, 4400, "A-BALCONY")
        d.line((b0, 4320), (b1, 4320), "A-BALCONY")
        n = round((b1 - b0) / 950)
        for i in range(1, n):
            x = b0 + (b1 - b0) * i / n
            d.line((x, Z_POOL), (x, 4400), "A-BALCONY", lineweight=5)
        d.text("glass balustrade", ((b0 + b1) / 2, 4620), 130, "A-TEXT")
        spans = ((800, 2100), (2900, 4200)) if view == "S" else ((hf((0, 5400)), hf((0, 1800))),)
        for a, b in spans:
            d.rect(a, Z_POOL, b, Z_POOL + 260, "A-BALCONY", lineweight=13)
    # shanyrak rooflight dome
    hc = hf((12400, 12900))
    d.arc((hc, Z_P - 300), 850, 21, 159, "A-ELEV", lineweight=18)
    d.text("rooflight", (hc, Z_P + 750), 120, "A-TEXT")
    # ground line
    w0, w1 = V["w"]
    d.line((w0 - 3500, Z_G), (w1 + 3500, Z_G), "A-ELEV", lineweight=70)
    d.hatch(box(w0 - 3500, Z_G - 350, w1 + 3500, Z_G), "A-ELEV-HATCH", "EARTH", scale=22)
    # a figure for scale
    fx = w1 + 2300
    d.circle((fx, Z_G + 1620), 130, "A-FURNITURE")
    d.pl([(fx - 180, Z_G), (fx, Z_G + 800), (fx + 180, Z_G)], "A-FURNITURE")
    d.line((fx, Z_G + 800), (fx, Z_G + 1490), "A-FURNITURE")
    d.pl([(fx - 260, Z_G + 950), (fx, Z_G + 1380), (fx + 260, Z_G + 950)], "A-FURNITURE")
    # levels, dimensions, title
    lx = w0 - 1700
    for z, t in ((Z_G, "-0.450"), (Z_1, "±0.000"), (Z_2, "+3.300"), (Z_RS, "+6.600"),
                 (Z_P, "+7.200")) + tuple(levels_extra):
        level_mark(d, lx, z, t, left=True)
    d.chain_v([Z_G, Z_1, Z_2, Z_RS, Z_P], w1 + 1300, w1 + 300)
    d.dim_h(w0, w1, -1500, Z_G - 450)
    d.text(V["title"], (w0, -2700), 330, "A-TEXT", "BL", style="ARIALBD")
    d.line((w0, -2820), (w0 + len(V["title"]) * 235, -2820), "A-TEXT")
    d.text("SCALE 1:100  -  levels in m, dimensions in mm", (w0, -3180), 170, "A-TEXT", "BL")


FINISH_NOTES = [
    "FINISHES",
    "1  Upper floor: ventilated timber-look rainscreen (horizontal boards)",
    "2  Ground floor: mineral render, warm white, on insulated masonry",
    "3  Plinth to ±0.000: frost-resistant granite tiles",
    "4  Windows: triple-glazed, larger on S and E, small on N",
    "5  Flat roof behind a 600 mm parapet, drained internally",
]


# ---------------------------------------------------------------------------
#  SECTION A-A (offset): x = 6800 through the pool, x = 9300 through stair 1
# ---------------------------------------------------------------------------
X_S, X_N, Y_JOG = 6800, 9300, 8600


def section_marks(d):
    """Section line A-A on a plan (looking east)."""
    L = "A-SECTION"
    d.pl([(X_S, -1000), (X_S, 700)], L, lineweight=70)                    # only the ends and the
    d.pl([(X_S, 8150), (X_S, Y_JOG), (X_N, Y_JOG), (X_N, 9050)], L, lineweight=70)   # jog are drawn
    d.pl([(X_N, 23300), (X_N, 25000)], L, lineweight=70)
    for (x, y) in ((X_S, -800), (X_N, 24850)):
        d.line((x, y), (x + 700, y), L, lineweight=50)
        d.pl([(x + 700, y + 150), (x + 1050, y), (x + 700, y - 150)], L, close=True)
        d.text("A", (x - 380, y), 330, L, "MC", style="ARIALBD")


def _intervals(walls, line):
    out = []
    g = walls.intersection(line)
    for s in getattr(g, "geoms", [g]):
        if s.geom_type == "LineString" and s.length > 5:
            ys = [p[1] for p in s.coords]
            out.append((min(ys), max(ys)))
    return sorted(out)


def section(d, P1, P2):
    hs = lambda y: 24300 - y            # looking east: north on the left
    CUT, HATCH, THIN = "A-WALL", "A-WALL-HATCH", "A-ELEV"
    line_s = LineString([(X_S, -400), (X_S, Y_JOG)])
    line_n = LineString([(X_N, Y_JOG), (X_N, 24400)])

    def conc(y0, z0, y1, z1, lw=35):
        r = box(hs(y1), z0, hs(y0), z1)
        d.hatch(r, HATCH, solid=True, rgb=(200, 200, 200))
        d.rect(hs(y1), z0, hs(y0), z1, CUT, lineweight=lw)

    def wall(y0, y1, z0, z1):
        r = box(hs(y1), z0, hs(y0), z1)
        d.hatch(r, HATCH, "ANSI31", scale=30)
        d.rect(hs(y1), z0, hs(y0), z1, CUT)

    # --- foundations ------------------------------------------------------
    for y, half, stem in ((0, 600, 300), (24000, 600, 300), (9000, 400, 200), (12750, 400, 200),
                          (14600, 400, 200), (19200, 400, 200)):
        conc(y - half, -2300, y + half, -1900)
        conc(y - stem, -1900, y + stem, -150 if stem == 200 else 0)
    # --- pool basin (cut at x = 6800: y 1600..5600) -----------------------
    shell = Polygon([(hs(5850), 0), (hs(5850), -1800), (hs(1350), -1800), (hs(1350), 0),
                     (hs(1600), 0), (hs(1600), -1500), (hs(5600), -1500), (hs(5600), 0)])
    d.hatch(shell, HATCH, solid=True, rgb=(200, 200, 200))
    d.shape(shell, CUT, lineweight=35)
    d.hatch(box(hs(5600), -1500, hs(1600), -100), "A-FLOOR-HATCH", "DASH", scale=30)
    d.line((hs(5600), -100), (hs(1600), -100), "A-POOL")
    d.text("POOL  water -0.100, floor -1.500", (hs(3600), -800), 150, "A-TEXT-ROOM")
    # --- ground slab ------------------------------------------------------
    for y0, y1 in ((300, 1350), (5850, 8800), (9200, 12550), (12950, 14400), (14800, 19000),
                   (19400, 23700)):
        conc(y0, -150, y1, 0, lw=25)
        d.hatch(box(hs(y1), -260, hs(y0), -150), HATCH, "ANSI37", scale=18)
    # --- walls: ground floor and second floor -----------------------------
    def storey(P, lines, base, top):
        for ln in lines:
            for y0, y1 in _intervals(P.walls, ln):
                wall(y0, y1, base, top)
            for o in P.openings:
                cut = o["poly"].intersection(ln)
                if cut.is_empty or cut.length < 5:
                    continue
                ys = [p[1] for p in cut.coords]
                y0, y1 = min(ys), max(ys)
                zs, zh = opening_z(o, base)
                zh = min(zh, top)
                if zs > base:
                    wall(y0, y1, base, zs)
                if zh < top:
                    wall(y0, y1, zh, top)
                if o["kind"] == "window":
                    ym = (y0 + y1) / 2
                    d.rect(hs(ym) - 40, zs, hs(ym) + 40, zh, "A-WINDOW")
                    d.line((hs(y1) - 60, zs), (hs(y0) + 60, zs), "A-WINDOW", lineweight=25)
                elif o["kind"] == "door":
                    d.rect(hs(y1), zs, hs(y0), zh, "A-DOOR", lineweight=13)
    storey(P1, (line_s, line_n), Z_1, 3000)
    storey(P2, (line_n,), Z_2, 6300)
    # --- floor slab, roof slab, parapets ----------------------------------
    conc(-300, 3000, 14725, Z_2)
    conc(19075, 3000, 24300, Z_2)
    conc(8700, 6300, 24300, Z_RS)
    wall(-300, 300, Z_2, Z_POOL)                       # balcony upstand
    d.rect(hs(40), Z_POOL, hs(-40), 4400, "A-BALCONY")  # glass balustrade
    wall(8700, 9300, Z_RS, Z_P)
    wall(23700, 24300, Z_RS, Z_P)
    for y0, y1 in ((8640, 9360), (23640, 24360)):       # copings
        d.rect(hs(y1), Z_P, hs(y0), Z_P + 60, CUT, lineweight=18)
    # roof build-up (insulation to falls)
    d.pl([(hs(23700), Z_RS + 320), (hs(16500), Z_RS + 180), (hs(9300), Z_RS + 320)], THIN)
    d.hatch(Polygon([(hs(23700), Z_RS), (hs(23700), Z_RS + 320), (hs(16500), Z_RS + 180),
                     (hs(9300), Z_RS + 320), (hs(9300), Z_RS)]), HATCH, "ANSI37", scale=22)
    d.line((hs(8700), Z_2 + 60), (hs(300), Z_2 + 60), THIN)   # balcony paving
    # --- stair 1 ----------------------------------------------------------
    conc(17725, 1450, 19075, 1650, lw=25)               # half landing
    up = [(hs(17725), 1650)]
    y, z = 17725, 1650
    for i in range(10):
        z += 150
        up.append((hs(y), z))
        y -= 300
        up.append((hs(y), z))
    up.append((hs(14725), Z_2))
    waist = [(hs(14725), 3000), (hs(14900), 3000), (hs(17725), 1450)]
    flight = Polygon(up + waist)
    d.hatch(flight, HATCH, solid=True, rgb=(200, 200, 200))
    d.shape(flight, CUT, lineweight=35)
    lo = []
    y, z = 14725, 0
    for i in range(11):
        lo.append((hs(y), z))
        z += 150
        lo.append((hs(y), z))
        y += 300
    lo = lo[:-1] + [(hs(17725), 1650)]
    d.pl(lo, THIN)
    d.line((hs(14725), 150), (hs(17725), 1650), THIN, linetype="HDASH")
    d.line((hs(14725), 900), (hs(17725), 2550), "A-STAIR")           # handrails
    d.line((hs(17725), 2550), (hs(14725), 4200), "A-STAIR")
    d.line((hs(14725), 4200), (hs(14725), 3300), "A-STAIR")
    d.text("STAIR 1", (hs(18400), 2650), 150, "A-TEXT-ROOM", style="ARIALBD")
    d.text("22 R x 150 / 300", (hs(18400), 2430), 110, "A-TEXT-ROOM")
    # --- beyond: wing A west wall above the balcony, hot tub --------------
    d.pl([(hs(8700), Z_P), (hs(-300), Z_P), (hs(-300), Z_2 + 60)], THIN)
    d.line((hs(8700), Z_P - 150), (hs(-300), Z_P - 150), THIN)
    draw_door(d, hs(6850) - 457, Z_2 + 60, hs(6850) + 457, Z_2 + 2134, False)
    d.text("south wing beyond", (hs(3500), 5600), 130, "A-TEXT")
    d.rect(hs(8350), 0, hs(6350), 450, THIN)
    d.text("hot tub beyond", (hs(7350), 650), 110, "A-TEXT")
    # --- ground -----------------------------------------------------------
    for a, b in ((-3200, -300), (24300, 27200)):
        d.line((hs(b), Z_G), (hs(a), Z_G), THIN, lineweight=70)
        d.hatch(box(hs(b), Z_G - 320, hs(a), Z_G), "A-ELEV-HATCH", "EARTH", scale=22)
    # --- labels -----------------------------------------------------------
    for txt, y, z in (("INDOOR POOL HALL", 4300, 1900), ("PUBLIC BALCONY", 4300, 4900),
                      ("PLANT", 10900, 1500), ("CORRIDOR", 13700, 1500),
                      ("STAFF ROOM", 21200, 1500), ("STORAGE", 10900, 4800),
                      ("CORRIDOR", 13700, 4800), ("ROOM 207", 21200, 4800)):
        d.text(txt, (hs(y), z), 160, "A-TEXT-ROOM", style="ARIALBD")
    d.text("flat roof: membrane, 180-320 insulation to falls, 300 RC slab", (hs(16500), 7450),
           130, "A-TEXT")
    d.text("300 floor slab", (hs(11500), 3460), 110, "A-TEXT")
    d.text("strip footings -2.300 (below frost depth)", (hs(16900), -2650), 130, "A-TEXT")
    # --- levels, dimensions, grid ----------------------------------------
    for z, t in ((-2300, "-2.300"), (Z_G, "-0.450"), (Z_1, "±0.000"), (Z_2, "+3.300"),
                 (Z_RS, "+6.600"), (Z_P, "+7.200")):
        level_mark(d, -1700, z, t, left=True)
    for z, t in ((Z_G, "-0.450"), (Z_1, "±0.000"), (Z_2, "+3.300"), (Z_POOL, "+3.600"),
                 (4400, "+4.400")):
        level_mark(d, 26300, z, t)
    level_mark(d, hs(18400), 1650, "+1.650", th=120)
    d.chain_v([Z_1, 3000, Z_2, 6300, Z_RS, Z_P], -600, 0)
    d.dim_v(Z_1, 3000, hs(22900))
    d.dim_v(Z_2, 6300, hs(22900))
    d.dim_v(Z_1, 3000, hs(2200))
    grids = [(24000, "H"), (19200, "G"), (14600, "F"), (9000, "D"), (0, "A")]
    d.chain_h([hs(y) for y, _ in grids], -3300, -2500)
    for y, lab in grids:
        d.line((hs(y), -2450), (hs(y), 7700), "A-GRID")
        d.circle((hs(y), -4050), 420, "A-GRID", linetype="Continuous")
        d.text(lab, (hs(y), -4050), 300, "A-GRID", "MC", style="ARIALBD")
    d.text("SECTION A-A", (0, -5300), 330, "A-TEXT", "BL", style="ARIALBD")
    d.line((0, -5420), (2700, -5420), "A-TEXT")
    d.text("SCALE 1:100  -  offset section: through the pool (x = 6800) and stair 1 (x = 9300), "
           "looking east", (0, -5780), 170, "A-TEXT", "BL")

#!/usr/bin/env python3
"""CEE 204 individual project - two-storey boutique hotel "AUL", Astana.

Generates one DXF (open in AutoCAD and SAVEAS .dwg) that holds, in model space,
the site plan, first-floor plan, second-floor plan and foundation plan, plus four
A2 paper-space layouts with title blocks and scaled viewports.

    python3 build.py        -> output/AUL_Boutique_Hotel.dxf
    python3 render.py       -> output/*.pdf, output/*.png
"""
import math
import os

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import elev as E
import hotel as H
from cadlib import Dwg, new_doc, polys
from hotel import dl
from plan import Plan

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")

STUDENT = "STUDENT NAME"          # <- edit before submission
STUDENT_ID = "ID ________"
DATE = "27.11.2026"
PROJECT = 'TWO-STOREY BOUTIQUE HOTEL "AUL", ASTANA'

# model-space origins of the individual drawings (mm)
O_SITE, O_GF, O_FF, O_FND, O_DET = (0, 0), (100000, 0), (200000, 0), (300000, 0), (400000, 0)
O_E4, O_E5 = (500000, 0), (600000, 0)   # elevations N + S; elevations E + W and section
BLDG_ON_SITE = (3300, 3300)       # grid 1/A on the site (outer faces 3.0 m from W and S boundary)


# ---------------------------------------------------------------------------
def entrance_steps(d, layer="A-STAIR", text_layer="A-TEXT", th=130, notes=True):
    """Entrance platform, steps and 1:12 ramp in front of the vestibule."""
    d.pl([dl(-1800, 2600), dl(1800, 2600), dl(1800, 4400), dl(-1800, 4400)], layer, close=True)
    for n in (4700, 5000, 5300):
        d.line(dl(-1800, n), dl(1800, n), layer)
    d.line(dl(-1800, 4400), dl(-1800, 5300), layer)
    d.line(dl(1800, 4400), dl(1800, 5300), layer)
    d.pl([dl(1800, 2700), dl(7200, 2700), dl(7200, 4200), dl(1800, 4200)], layer, close=True)
    d.line(dl(6900, 3450), dl(2300, 3450), layer)
    a = dl(2300, 3450)
    for da in (-25, 25):
        ang = math.radians(135 + da)
        d.line(a, (a[0] + 300 * math.cos(ang), a[1] + 300 * math.sin(ang)), layer)
    d.text("RAMP 1:12 (up)", dl(4600, 3800), th, text_layer, rot=-45)
    if notes:
        d.text("3 risers", dl(0, 4850), th * 0.85, text_layer, rot=-45)
        d.pl([dl(-2100, 2600), dl(-2100, 5900), dl(2100, 5900), dl(2100, 4500)], "A-ABOVE")  # canopy
        d.text("canopy over", dl(-2350, 4300), th * 0.85, text_layer, rot=45)


def north_arrow(d, c, r, layer="A-TEXT", th=None):
    x, y = c
    d.circle(c, r, layer)
    d.pl([(x, y + r), (x - 0.35 * r, y - 0.75 * r), (x, y - 0.45 * r), (x + 0.35 * r, y - 0.75 * r)],
         layer, close=True)
    d.line((x, y + r), (x, y - 0.45 * r), layer)
    d.text("N", (x, y + r * 1.35), th or r * 0.55, layer, "MC", style="ARIALBD")


def title_under(d, pos, title, scale, h=450):
    d.text(title, pos, h, "A-TEXT", "BL", style="ARIALBD")
    d.line((pos[0], pos[1] - h * 0.35), (pos[0] + len(title) * h * 0.72, pos[1] - h * 0.35), "A-TEXT")
    d.text(f"SCALE {scale}  -  all dimensions in mm", (pos[0], pos[1] - h * 1.3), h * 0.5,
           "A-TEXT", "BL")


# ---------------------------------------------------------------------------
#  FLOOR PLANS
# ---------------------------------------------------------------------------
def draw_first_floor(msp):
    d = Dwg(msp, *O_GF)
    P = H.first_floor(d)
    H.exterior_dims(d, P)
    entrance_steps(d)
    north_arrow(d, (29800, 22300), 900)
    d.label([("ARRIVAL COURT", 220, "ARIALBD"), ("sheltered from SW winter winds", 140, "ARIAL"),
             ("see site plan A-01", 140, "ARIAL")], (26300, 17700), "A-TEXT")
    H.level_mark(d, (14700, 6300), "±0.000  FFL")
    H.level_mark(d, (25300, 15250), "-0.450  ground")
    d.text("kitchen service door", (26600, 13750), 130, "A-TEXT")
    d.text("staff entrance", (7100, 24750), 130, "A-TEXT")
    d.text("MAIN ENTRANCE", dl(0, 6350), 200, "A-TEXT", rot=-45, style="ARIALBD")
    d.text("step-free access via ramp", dl(0, 6050), 120, "A-TEXT", rot=-45)
    E.section_marks(d)
    title_under(d, (-3500, -5600), "FIRST FLOOR PLAN", "1:100")
    return P


def draw_second_floor(msp):
    d = Dwg(msp, *O_FF)
    P = H.second_floor(d)
    H.exterior_dims(d, P, second=True)
    north_arrow(d, (29800, 22300), 900)
    H.level_mark(d, (23800, 6750), "+3.300  FFL")
    H.level_mark(d, (8600, 3550), "+3.250")
    E.section_marks(d)
    title_under(d, (-3500, -5600), "SECOND FLOOR PLAN", "1:100")
    return P


# ---------------------------------------------------------------------------
#  ELEVATIONS AND SECTION
# ---------------------------------------------------------------------------
def draw_elevations(msp, P1, P2):
    ops = [(o, 0) for o in P1.openings] + [(o, 3300) for o in P2.openings]
    for view, (ox, oy) in (("N", (O_E4[0], O_E4[1] + 22000)), ("S", (O_E4[0], O_E4[1] + 6000)),
                           ("W", (O_E5[0], O_E5[1] + 29200)), ("E", (O_E5[0], O_E5[1] + 17400))):
        E.elevation(Dwg(msp, ox, oy), view, ops)
    E.section(Dwg(msp, O_E5[0], O_E5[1] + 6000), P1, P2)


# ---------------------------------------------------------------------------
#  FOUNDATION PLAN
# ---------------------------------------------------------------------------
INT_WALL_AXES = [
    ((5800, 14600), (5800, 24000)), ((8000, 14600), (8000, 20225)),
    ((11400, 0), (11400, 19800)), ((16000, 0), (16000, 7800)),
    ((20600, 0), (20600, 11400)), ((28000, 5900), (28000, 11400)),
    ((11400, 5900), (31200, 5900)), ((11400, 7800), (28000, 7800)),
    ((0, 9000), (11400, 9000)), ((0, 12750), (11400, 12750)),
    ((0, 14600), (11400, 14600)), ((0, 18900), (5800, 18900)),
    ((8000, 19200), (11400, 19200)), ((5800, 20225), (8000, 20225)),
    ((11400, 11400), (16150, 11400)), ((16150, 7800), (16150, 11400)),
    ((3150, 9000), (3150, 14600)),
]


def draw_foundation(msp):
    d = Dwg(msp, *O_FND)
    ext = Polygon(H.AX_GF).exterior
    vest = Polygon([dl(-1350, 0), dl(1350, 0), dl(1350, 2450), dl(-1350, 2450)]).exterior

    def strips(half_ext, half_int, half_vest):
        parts = [ext.buffer(half_ext, cap_style=2, join_style=2, mitre_limit=10),
                 vest.buffer(half_vest, cap_style=2, join_style=2, mitre_limit=10)]
        parts += [LineString(l).buffer(half_int, cap_style=2) for l in INT_WALL_AXES]
        return unary_union(parts).buffer(0).simplify(0.5)

    footing = strips(600, 400, 400)
    stem = strips(300, 200, 150)
    shell = H.pool_polygon(grow=250)
    tub = Point(9500, 7350).buffer(1250, 32)
    footing_all = unary_union([footing, shell.buffer(150, join_style=2), tub])

    d.hatch(footing_all.difference(unary_union([H.pool_polygon(), Point(9500, 7350).buffer(1000, 32)])),
            "S-FOOTING-HATCH", solid=True, rgb=(218, 218, 218))
    d.hatch(stem, "S-FWALL-HATCH", "ANSI31", scale=22)
    d.shape(footing_all, "S-FOOTING")
    d.shape(stem, "S-FWALL")
    d.plb(H.POOL, "S-FWALL", close=True)
    d.shape(shell, "S-FWALL", lineweight=25)
    d.circle((9500, 7350), 1000, "S-FWALL", lineweight=25)
    d.label([("RC POOL BASIN", 200, "ARIALBD"), ("walls 250, base slab 300", 140, "ARIAL"),
             ("base -1.500 ... -1.900", 140, "ARIAL")], (4400, 3600), "S-TEXT")
    d.text("hot-tub pit -1.200", (9500, 7350), 110, "S-TEXT")

    # slab note in the larger bays
    for pos in ((24500, 3000), (2900, 21500), (15500, 13300)):
        d.label([("RC ground slab 150", 140, "ARIAL"), ("on 100 XPS + 200 gravel", 120, "ARIAL")],
                pos, "S-TEXT")

    # footing tags with leaders
    def tag(txt, at, to):
        d.line(at, to, "S-TEXT")
        d.circle(to, 40, "S-TEXT")
        w = len(txt) * 125
        d.line(at, (at[0] + w, at[1]), "S-TEXT")
        d.text(txt, (at[0] + w / 2, at[1] + 130), 170, "S-TEXT", "MC", style="ARIALBD")

    tag("FS-1", (13600, -1150), (14500, -300))
    tag("FS-1", (-1900, 16600), (-350, 17300))
    tag("FS-1", (32000, 9500), (31500, 8900))
    tag("FS-2", (17000, 2300), (16250, 1800))
    tag("FS-2", (22500, 6700), (23300, 6050))
    tag("FS-2", (12300, 16400), (11650, 15900))
    tag("FS-2", (6700, 17500), (5900, 17000))
    tag("FS-3", dl(-3000, 3300), dl(-1500, 1500))
    tag("FS-1", (17200, 16600), (16200, 15450))

    # typical width dimensions
    d.dim_h(-600, 600, 4300)
    d.dim_h(15600, 16400, 4300)
    d.dim_v(-600, 600, 25300)
    d.dim_v(5500, 6300, 25300)

    # section mark 1 - 1 across the south wall
    d.pl([(18300, -1000), (18300, -700)], "S-TEXT", lineweight=50)
    d.pl([(18300, 700), (18300, 1000)], "S-TEXT", lineweight=50)
    d.text("1", (18050, -900), 220, "S-TEXT", style="ARIALBD")
    d.text("1", (18050, 900), 220, "S-TEXT", style="ARIALBD")

    # grid + dimension chains
    P = Plan(d, None)
    d.chain_h(H.GX, -2200, -700)
    d.chain_h([-600, 31800], -3000, -700)
    d.chain_h(H.GX, 26200, 24700)
    d.chain_v(H.GY, -2200, -700)
    d.chain_v([-600, 24600], -3000, -700)
    d.chain_v(H.GY, 33400, 31900)
    P.grid(H.GX, H.GY, (-3700, 34100), (-3700, 26900))
    north_arrow(d, (29800, 22300), 900, "S-TEXT")
    d.label([("FOUNDATION NOTES", 170, "ARIALBD"),
             ("top of footing -1.900, underside -2.300", 130, "ARIAL"),
             ("(below seasonal frost depth, Astana)", 130, "ARIAL"),
             ("see detail 1 on this sheet", 130, "ARIAL")], (26000, 17600), "S-TEXT")
    title_under(d, (-3500, -5600), "FOUNDATION PLAN", "1:100")
    return dict(footing=footing_all.area / 1e6)


def draw_foundation_detail(msp):
    d = Dwg(msp, *O_DET, dimstyle="A25", dim_layer="A-DIMS")
    L = "S-DETAIL"
    # hatched solids
    d.hatch(box(-600, -2300, 600, -1900), "S-FOOTING-HATCH", "AR-CONC", scale=0.5)
    d.hatch(box(-300, -1900, 300, 0), "S-FOOTING-HATCH", "AR-CONC", scale=0.5)
    d.hatch(box(-300, 0, 300, 850), "S-FWALL-HATCH", "ANSI31", scale=6)
    d.hatch(box(300, -150, 1450, 0), "S-FOOTING-HATCH", "AR-CONC", scale=0.5)
    d.hatch(box(300, -250, 1450, -150), "S-FWALL-HATCH", "ANSI37", scale=5)
    d.hatch(box(-400, -1900, -300, -100), "S-FWALL-HATCH", "ANSI37", scale=5)
    d.hatch(box(300, -450, 1450, -250), "S-FOOTING-HATCH", "DOTS", scale=6)
    d.hatch(box(-700, -2400, 700, -2300), "S-FOOTING-HATCH", "DOTS", scale=4)
    d.hatch(Polygon([(-1450, -450), (-400, -450), (-400, -700), (-1450, -700)]),
            "S-FOOTING-HATCH", "EARTH", scale=6)
    for r in ((-600, -2300, 600, -1900), (-300, -1900, 300, 0), (300, -150, 1450, 0),
              (300, -250, 1450, -150), (-400, -1900, -300, -100), (-700, -2400, 700, -2300),
              (300, -450, 1450, -250)):
        d.rect(*r, L)
    d.line((-300, 0), (-300, 850), L)
    d.line((300, 0), (300, 850), L)
    d.pl([(-420, 850), (-120, 850), (-60, 950), (60, 750), (120, 850), (420, 850)], L, lineweight=13)
    d.line((-1450, -450), (-400, -450), L, lineweight=50)          # ground level
    d.pl([(-400, -400), (-1200, -450)], L, lineweight=13)          # paved apron fall
    d.line((-300, 0), (300, 0), L, lineweight=13)
    # level marks
    for y, txt, x in ((0, "±0.000 FFL", 950), (-450, "-0.450 GL", -1250),
                      (-1900, "-1.900", 850), (-2300, "-2.300", 850)):
        d.pl([(x - 60, y + 60), (x, y), (x + 60, y + 60)], L, close=True, lineweight=13)
        d.line((x - 60, y + 60), (x + 420, y + 60), L, lineweight=13)
        d.text(txt, (x + 90, y + 105), 55, "S-TEXT", "BL")
    d.line((600, -1900), (900, -1900), L, lineweight=13)
    d.line((600, -2300), (900, -2300), L, lineweight=13)
    d.dim_h(-600, 600, -2800, -2420)
    d.dim_h(-300, 300, 1050, 870)
    d.dim_v(-2300, -1900, -900, -620)
    # notes
    notes = [((330, 500), "600 exterior wall"), ((330, 400), "(masonry + insulation)"),
             ((330, -560), "150 RC slab / 100 XPS /"), ((330, -650), "200 compacted gravel"),
             ((-1430, -1000), "100 XPS perimeter"), ((-1430, -1090), "insulation +"),
             ((-1430, -1180), "waterproofing"),
             ((330, -1200), "RC stem wall 600"), ((-560, -2100), "FS-1  1200 x 400"),
             ((-520, -2530), "100 blinding concrete")]
    for pos, txt in notes:
        d.text(txt, pos, 55, "S-TEXT", "BL")
    d.text("DETAIL 1 - TYPICAL STRIP FOOTING (FS-1)", (-1450, 1330), 75, "S-TEXT", "BL",
           style="ARIALBD")
    d.text("SCALE 1:25", (-1450, 1220), 55, "S-TEXT", "BL")


# ---------------------------------------------------------------------------
#  SITE PLAN
# ---------------------------------------------------------------------------
EXISTING_TREES = [
    (25000, 48500), (30000, 49800), (36000, 50500), (27500, 45500), (33000, 46200),
    (29500, 43000), (34500, 42500), (37500, 40500), (24500, 41000),
    (2500, 38500), (9500, 39500), (13500, 40000), (17000, 39500), (20500, 39800),
    (2200, 34000), (9500, 32500), (13000, 32300), (17000, 32500), (37000, 37000),
    (6000, 36500), (12000, 36300), (16000, 36000), (24500, 36200), (28500, 36300),
    (33000, 36800), (5200, 51500),
]


def arc_pts(c, r, a0, a1, step=3):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def draw_site(msp, gf_area):
    d = Dwg(msp, *O_SITE, dimstyle="A200", ltscale=2.0, dim_layer="L-DIMS")
    bx, by = BLDG_ON_SITE
    tr = lambda g: affinity.translate(g, bx, by)
    bldg = tr(H.FOOT_GF)
    two = tr(H.FO_2F)
    pool_roof = tr(H.POOL_ROOF)
    balcony = tr(H.BALCONY)

    # ---- new road, parking, paving --------------------------------------
    cl = [(6300, 60000), (6300, 40000)] + arc_pts((10300, 40000), 4000, 180, 270) \
        + [(27800, 36000)] + arc_pts((27800, 32000), 4000, 90, 0) + [(31800, 29500)]
    drive = LineString(cl).buffer(1750, cap_style=2, join_style=1)
    aisle = box(28800, 15800, 34800, 30000)
    bays = box(34800, 16000, 39800, 29600)
    road = unary_union([drive, aisle]).buffer(0)
    plaza = box(15000, 15000, 28800, 27600).difference(bldg.buffer(1))
    plaza = max(polys(plaza), key=lambda g: g.area)
    terrace = box(34800, 3600, 39200, 9400)
    exit_path = box(34800, 9400, 36300, 10500)
    deck = box(900, 6200, 3000, 9600)
    service = box(29300, 15000, 30500, 15800)
    staff_path = box(9800, 27600, 15600, 28800)
    footpath = box(20200, 27600, 21700, 34250)

    d.hatch(road, "L-PAVING-HATCH", solid=True, rgb=(222, 222, 222))
    d.hatch(bays, "L-PAVING-HATCH", solid=True, rgb=(235, 235, 235))
    for g in (plaza, terrace, deck, exit_path, service, staff_path, footpath):
        d.hatch(g, "L-PAVING-HATCH", solid=True, rgb=(244, 238, 226))
    d.hatch(plaza, "L-PAVING-HATCH", "NET", scale=260)
    d.hatch(terrace, "L-PAVING-HATCH", "ANSI37", scale=110)
    d.hatch(deck, "L-PAVING-HATCH", "LINE", scale=90)
    d.shape(road, "L-ROAD")
    d.shape(bays, "L-ROAD")
    y = 16000
    for i, w in enumerate((3600, 2500, 2500, 2500, 2500)):
        d.line((34800, y), (39800, y), "L-ROAD")
        if i:
            d.text("P%d" % (i + 1), (37300, y + w / 2), 330, "L-TEXT")
        else:
            d.text("P1", (37900, y + w / 2 + 300), 330, "L-TEXT")
            d.text("accessible", (37900, y + w / 2 - 300), 260, "L-TEXT")
        y += w
    d.line((34800, y), (39800, y), "L-ROAD")
    d.line((36000, 16000), (36000, 19600), "L-ROAD", linetype="HDASH")
    for g in (plaza, terrace, deck, exit_path, service, staff_path, footpath):
        d.shape(g, "L-PAVING")
    # shanyrak paving pattern in the arrival plaza
    sc = (26550 , 22300)
    for r in (2000, 1750, 550):
        d.circle(sc, r, "L-PAVING")
    for ang in (45, 135):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for off in (-260, 0, 260):
            h = math.sqrt(1750 ** 2 - off ** 2)
            p = (sc[0] - sa * off, sc[1] + ca * off)
            d.line((p[0] - ca * h, p[1] - sa * h), (p[0] + ca * h, p[1] + sa * h), "L-PAVING")
    # drive direction arrows + centre line
    d.pl(cl, "L-ROAD", linetype="HCENTER", lineweight=9)

    # ---- building -------------------------------------------------------
    d.hatch(two, "L-BUILDING-HATCH", "ANSI31", scale=150)
    d.hatch(balcony, "L-BUILDING-HATCH", "NET", scale=180)
    d.shape(bldg, "L-BUILDING")
    d.shape(two, "L-BUILDING", lineweight=35)
    d.shape(balcony, "L-BUILDING", lineweight=18)
    dd = Dwg(msp, O_SITE[0] + bx, O_SITE[1] + by, dimstyle="A200", ltscale=2.0)
    entrance_steps(dd, layer="L-PAVING", text_layer="L-TEXT", th=260, notes=False)
    a = dl(0, 6800)
    tip = dl(0, 2900)
    dd.line(a, tip, "L-TEXT", lineweight=35)
    for da in (-25, 25):
        ang = math.radians(45 + da)
        dd.line(tip, (tip[0] + 700 * math.cos(ang), tip[1] + 700 * math.sin(ang)), "L-TEXT",
                lineweight=35)
    d.label([("NEW BOUTIQUE HOTEL", 620, "ARIALBD"), ("2 storeys  -  FFL ±0.000", 400, "ARIAL"),
             (f"footprint {gf_area:.0f} m²", 400, "ARIAL")], (24500, 7200), "L-TEXT")
    d.label([("WEST WING", 380, "ARIALBD"), ("2 storeys", 320, "ARIAL")], (8800, 21500), "L-TEXT")
    d.label([("POOL HALL", 330, "ARIALBD"), ("1 storey", 300, "ARIAL")], (5600, 6500), "L-TEXT")
    d.label([("PUBLIC", 300, "ARIALBD"), ("BALCONY", 300, "ARIALBD"), ("(2nd floor)", 280, "ARIAL")],
            (11550, 7600), "L-TEXT")
    d.text("MAIN ENTRANCE", (26500, 16900), 330, "L-TEXT", style="ARIALBD")
    d.text("(step-free via ramp)", (26500, 16400), 260, "L-TEXT")
    d.label([("ARRIVAL PLAZA", 380, "ARIALBD"), ('"shanyrak" paving', 300, "ARIAL")],
            (21500, 25800), "L-TEXT")
    d.label([("RESTAURANT", 280, "ARIAL"), ("TERRACE", 280, "ARIAL"), ("(morning sun)", 260, "ARIAL")],
            (37000, 6500), "L-TEXT")
    d.text("sun deck", (1950, 7900), 260, "L-TEXT", rot=90)
    d.text("staff path", (12700, 28200), 260, "L-TEXT")
    d.text("service", (31900, 15400), 260, "L-TEXT")
    d.text("fire exit", (37800, 9950), 260, "L-TEXT")
    d.text("footpath to garden", (21000, 31000), 260, "L-TEXT", rot=90)
    d.text("PARKING  5 bays", (37300, 30350), 330, "L-TEXT", style="ARIALBD")
    d.text("NEW DRIVEWAY 3.5 m", (19000, 36300), 330, "L-TEXT", style="ARIALBD")
    d.text("NEW DRIVEWAY", (6300, 44500), 330, "L-TEXT", rot=90, style="ARIALBD")
    d.text("turning / drop-off aisle 6.0 m", (31800, 23000), 300, "L-TEXT", rot=90)

    # ---- site boundary, hotel zone ---------------------------------------
    d.rect(0, 0, 40000, 60000, "L-BOUNDARY")
    d.line((0, 30000), (40000, 30000), "L-ZONE")
    d.text("limit of the 40 x 30 m area provisioned for the hotel", (500, 30300), 300, "L-TEXT", "BL")
    # main entrance gates (existing) in the north boundary
    d.line((4550, 59700), (4550, 60300), "L-EXISTING", lineweight=50)
    d.line((8050, 59700), (8050, 60300), "L-EXISTING", lineweight=50)
    d.arc((4550, 60000), 1750, 270, 360, "L-EXISTING")
    d.arc((8050, 60000), 1750, 180, 270, "L-EXISTING")
    d.line((4550, 60000), (4550, 58250), "L-EXISTING")
    d.line((8050, 60000), (8050, 58250), "L-EXISTING")
    d.text("MAIN ENTRANCE GATES (existing)", (6300, 61200), 380, "L-TEXT", style="ARIALBD")

    # ---- existing structures --------------------------------------------
    house = Polygon([(8600, 46000), (16000, 46000), (16000, 57000), (8600, 57000)])
    d.hatch(house, "L-BUILDING-HATCH", "ANSI31", scale=260, angle=90)
    d.shape(house, "L-EXISTING", lineweight=50)
    d.line((8600, 52000), (16000, 52000), "L-EXISTING")
    d.line((13500, 52000), (13500, 57000), "L-EXISTING")
    d.line((14600, 46000), (14600, 52000), "L-EXISTING")
    d.rect(14400, 45000, 16000, 46000, "L-EXISTING")
    d.label([("EXISTING", 360, "ARIALBD"), ("TWO-STOREY HOUSE", 360, "ARIALBD"),
             ("(retained)", 300, "ARIAL")], (11700, 49000), "L-TEXT")
    garden = Polygon([(18200, 51500), (19000, 56800), (22500, 57600), (26000, 56600),
                      (26600, 52500), (24500, 50400), (20500, 50200)])
    d.hatch(garden, "L-PAVING-HATCH", "DOTS", scale=170)
    d.shape(garden, "L-EXISTING")
    d.label([("GARDENING AREA", 340, "ARIALBD"), ("(existing, retained)", 280, "ARIAL")],
            (22400, 54000), "L-TEXT")
    path = Polygon([(16000, 45200), (16000, 46300), (31500, 54500), (32000, 53600)])
    d.hatch(path, "L-PAVING-HATCH", "ANSI31", scale=120)
    d.shape(path, "L-EXISTING")
    d.rect(32000, 53000, 39500, 58000, "L-EXISTING", lineweight=35)
    d.label([("OPEN TERRACE", 340, "ARIALBD"), ("(existing)", 280, "ARIAL")], (35750, 55500), "L-TEXT")
    d.rect(1000, 46500, 4000, 49500, "L-EXISTING", lineweight=35)
    d.label([("open", 260, "ARIAL"), ("summer", 260, "ARIAL"), ("terrace", 260, "ARIAL")],
            (2500, 48000), "L-TEXT")
    d.rect(500, 57200, 2300, 59200, "L-EXISTING", lineweight=35)
    d.line((500, 57200), (2300, 59200), "L-EXISTING")
    d.text("steel storage", (1400, 56700), 240, "L-TEXT")
    d.text("container", (1400, 56300), 240, "L-TEXT")

    # ---- planting --------------------------------------------------------
    keep_clear = unary_union([road.buffer(1500), footpath.buffer(1200), house.buffer(500)])
    kept = 0
    for c in EXISTING_TREES:
        if not keep_clear.contains(Point(c)):
            d.tree(c, 1400)
            kept += 1
    new_trees = [(17500, 29000, 900), (24200, 28900, 1000), (27300, 28900, 1000),
                 (37400, 11700, 1300), (37400, 14200, 1100), (1500, 12500, 1000),
                 (1500, 16500, 1000), (1500, 20500, 1000), (1500, 24500, 1000),
                 (1500, 28300, 1000), (5500, 28900, 1000), (36800, 32200, 1200),
                 (12500, 43200, 1200), (20000, 43000, 1200)]
    for x, y, r in new_trees:
        d.circle((x, y), r, "L-PLANT")
        d.circle((x, y), r * 0.55, "L-PLANT")
        d.line((x - r * 0.3, y), (x + r * 0.3, y), "L-PLANT")
        d.line((x, y - r * 0.3), (x, y + r * 0.3), "L-PLANT")
    for x in range(5000, 34001, 2600):                      # hedge along the south boundary
        d.circle((x, 1450), 650, "L-PLANT")
    for yy in range(1800, 5001, 1500):
        d.circle((1450, yy), 600, "L-PLANT")
    d.circle((26550, 22300), 550, "L-PLANT")
    d.text("hedge / low planting (south and west setback 3.0 m)", (19000, 480), 260, "L-TEXT")

    # ---- dimensions ------------------------------------------------------
    d.chain_h([0, 3000, 34800, 40000], -1600, 0)
    d.chain_h([0, 40000], -3200, 0)
    d.chain_v([0, 3000, 27600, 30000, 60000], 41800, 40000)
    d.chain_v([0, 60000], 43600, 40000)
    # ---- north arrow, legend ---------------------------------------------
    north_arrow(d, (49500, 56000), 2000, "L-TEXT", th=900)
    lx, ly = 46000, 50000
    d.text("LEGEND", (lx, ly), 480, "L-TEXT", "BL", style="ARIALBD")
    items = [("site boundary 40 x 60 m", "bnd"), ("hotel zone limit", "zone"),
             ("new hotel, 2-storey part", "two"), ("new hotel, 1-storey part", "one"),
             ("existing structure (retained)", "ex"), ("new driveway / parking (asphalt)", "road"),
             ("new paving / terraces", "pave"), ("existing tree (retained)", "tree"),
             ("new tree / planting", "ntree")]
    y = ly - 1700
    for txt, kind in items:
        if kind == "bnd":
            d.line((lx, y), (lx + 3000, y), "L-BOUNDARY")
        elif kind == "zone":
            d.line((lx, y), (lx + 3000, y), "L-ZONE")
        elif kind == "two":
            d.hatch(box(lx, y - 500, lx + 3000, y + 500), "L-BUILDING-HATCH", "ANSI31", scale=150)
            d.rect(lx, y - 500, lx + 3000, y + 500, "L-BUILDING")
        elif kind == "one":
            d.rect(lx, y - 500, lx + 3000, y + 500, "L-BUILDING")
        elif kind == "ex":
            d.hatch(box(lx, y - 500, lx + 3000, y + 500), "L-BUILDING-HATCH", "ANSI31", scale=260,
                    angle=90)
            d.rect(lx, y - 500, lx + 3000, y + 500, "L-EXISTING", lineweight=50)
        elif kind == "road":
            d.hatch(box(lx, y - 500, lx + 3000, y + 500), "L-PAVING-HATCH", solid=True,
                    rgb=(222, 222, 222))
            d.rect(lx, y - 500, lx + 3000, y + 500, "L-ROAD")
        elif kind == "pave":
            d.hatch(box(lx, y - 500, lx + 3000, y + 500), "L-PAVING-HATCH", solid=True,
                    rgb=(244, 238, 226))
            d.rect(lx, y - 500, lx + 3000, y + 500, "L-PAVING")
        elif kind == "tree":
            d.tree((lx + 1500, y), 700)
        elif kind == "ntree":
            d.circle((lx + 1500, y), 700, "L-PLANT")
            d.circle((lx + 1500, y), 385, "L-PLANT")
        d.text(txt, (lx + 3800, y), 330, "L-TEXT", "ML")
        y -= 2000
    y -= 600
    d.text("SITE DATA", (lx, y), 480, "L-TEXT", "BL", style="ARIALBD")
    two_area = H.FO_2F.area / 1e6
    data = [("Plot area", "40 x 60 m = 2400 m²"), ("Hotel zone", "40 x 30 m = 1200 m²"),
            ("Building footprint", f"{gf_area:.1f} m²  (limit 400-600)"),
            ("Second-floor area", f"{two_area:.1f} m² + balcony 51 m²"),
            ("Zone coverage", f"{gf_area / 1200 * 100:.0f} %"),
            ("Setbacks", "W 3.0 / S 3.0 / E 5.2 m"),
            ("Parking", "5 bays (1 accessible)"),
            ("Existing trees kept", f"{kept} of {len(EXISTING_TREES)}")]
    y -= 1500
    for k, v in data:
        d.text(k, (lx, y), 330, "L-TEXT", "ML")
        d.text(v, (lx + 6200, y), 330, "L-TEXT", "ML")
        y -= 1250
    title_under(d, (0, -6200), "SITE PLAN", "1:200", h=900)


# ---------------------------------------------------------------------------
#  SHEETS (paper space, A2 landscape, mm)
# ---------------------------------------------------------------------------
PW, PH = 594, 420
PX0, PX1 = 446, 584                 # right-hand panel


def schedule_rows(P):
    rows = []
    for r in P.rooms:
        if not r["count"]:
            continue
        name = r["name"].replace("\n", " ").title() if r["name"].isupper() else r["name"].replace("\n", " ")
        name = name.replace("Wc", "WC")
        if r["group"] == "guest":
            name = f"{r['no']} {r['name']}"
            if r["no"] == "102":
                name += " (accessible)"
        rows.append((name, f"{r['area']:.1f}", r["spec"] if r["spec"] != "additional" else "extra"))
    guests = sorted([r for r in rows if r[0][:3].isdigit()], key=lambda r: r[0])
    return guests + [r for r in rows if not r[0][:3].isdigit()]


def make_sheet(doc, name, title, number, scale_txt, viewports, panel):
    lay = doc.layouts.new(name)
    lay.page_setup(size=(PW, PH), margins=(0, 0, 0, 0), units="mm")
    d = Dwg(lay)
    d.rect(10, 10, 584, 410, "T-FRAME")
    d.line((PX0, 10), (PX0, 410), "T-FRAME", lineweight=35)
    for (cx, cy, w, h, mx, my, scale) in viewports:
        vp = lay.add_viewport(center=(cx, cy), size=(w, h), view_center_point=(mx, my),
                              view_height=h * scale)
        vp.dxf.layer = "T-VIEWPORT"
        vp.dxf.flags = vp.dxf.get("flags", 0) | 16384      # display locked
    # ---- title block ----------------------------------------------------
    rows = [10, 26, 38, 50, 68, 82, 94, 106]
    for y in rows[1:]:
        d.line((PX0, y), (PX1, y), "T-TITLE", lineweight=35 if y == rows[-1] else 18)
    d.line((515, 10), (515, 26), "T-TITLE")
    d.line((492, 26), (492, 50), "T-TITLE")

    def cell(label, value, x, y, h=3.2, bold=True):
        d.text(label, (x + 1.5, y - 2.6), 1.6, "T-TEXT", "ML")
        d.text(value, (x + 1.5, y - 7.6 - (h - 3.2) * 0.4), h, "T-TEXT", "ML",
               style="ARIALBD" if bold else "ARIAL")

    d.text("NAZARBAYEV UNIVERSITY", (PX0 + 69, 101.6), 3.4, "T-TEXT", "MC", style="ARIALBD")
    d.text("School of Engineering", (PX0 + 69, 96.6), 2.2, "T-TEXT", "MC")
    cell("COURSE", "CEE 204 Civil Engineering CAD & Surveying", PX0, 94, 2.9)
    d.text("PROJECT", (PX0 + 1.5, 79.4), 1.6, "T-TEXT", "ML")
    d.text("INDIVIDUAL PROJECT", (PX0 + 1.5, 75.3), 2.6, "T-TEXT", "ML", style="ARIALBD")
    d.text(PROJECT, (PX0 + 1.5, 71), 2.6, "T-TEXT", "ML", style="ARIALBD")
    d.text("DRAWING TITLE", (PX0 + 1.5, 65.4), 1.6, "T-TEXT", "ML")
    d.text(title, (PX0 + 1.5, 57.5), 5.0, "T-TEXT", "ML", style="ARIALBD")
    cell("STUDENT", STUDENT, PX0, 50, 3.0)
    cell("STUDENT ID", STUDENT_ID, 492, 50, 3.0)
    cell("INSTRUCTOR", "Bakhyt Aubakirova", PX0, 38, 3.0)
    cell("DATE", DATE, 492, 38, 3.0)
    cell("SCALE (A2)", scale_txt, PX0, 26, 4.0)
    cell("SHEET No.", number, 515, 26, 5.0)
    panel(d)
    return lay


def text_block(d, x, y, title, lines, h=2.1, lead=3.6):
    d.text(title, (x, y), 2.8, "T-TEXT", "BL", style="ARIALBD")
    d.line((x, y - 1.2), (PX1 - 3, y - 1.2), "T-TITLE")
    y -= 5.2
    for ln in lines:
        d.text(ln, (x, y), h, "T-TEXT", "BL")
        y -= lead
    return y - 2.5


def table(d, x, y, title, header, rows, widths, h=2.0, lead=3.75):
    d.text(title, (x, y), 2.8, "T-TEXT", "BL", style="ARIALBD")
    y -= 2.0
    x1 = x + sum(widths)
    d.line((x, y), (x1, y), "T-TITLE", lineweight=35)
    for i, row in enumerate([header] + rows):
        yy = y - lead * (i + 1)
        cx = x
        for j, (val, w) in enumerate(zip(row, widths)):
            if j == 0:
                d.text(val, (cx + 1, yy + lead / 2), h, "T-TEXT", "ML",
                       style="ARIALBD" if i == 0 else "ARIAL")
            else:
                d.text(val, (cx + w / 2, yy + lead / 2), h, "T-TEXT", "MC",
                       style="ARIALBD" if i == 0 else "ARIAL")
            cx += w
        d.line((x, yy), (x1, yy), "T-TITLE", lineweight=25 if i == 0 else 5)
    y_end = y - lead * (len(rows) + 1)
    cx = x
    for w in list(widths) + [0]:
        d.line((cx, y), (cx, y_end), "T-TITLE", lineweight=5)
        cx += w
    return y_end - 6


GENERAL_NOTES = [
    "1. All dimensions in millimetres; levels in metres.",
    "2. Exterior walls 600 mm; interior walls 250 mm;",
    "    bathroom / wet-room and vestibule walls 300 mm.",
    "3. Interior doors 813 x 2032; exterior doors 915 x 2134",
    "    (double leaf at main entrance and terrace).",
    "4. Accessible room 102 and public WC 1: 915 mm doors,",
    "    1500 mm turning circle (dashed).",
    "5. Grid lines = centre lines of load-bearing walls.",
]


def build():
    os.makedirs(OUT, exist_ok=True)
    doc = new_doc()
    msp = doc.modelspace()
    P1 = draw_first_floor(msp)
    P2 = draw_second_floor(msp)
    draw_elevations(msp, P1, P2)
    fnd = draw_foundation(msp)
    draw_foundation_detail(msp)
    gf_area = H.FOOT_GF.area / 1e6
    draw_site(msp, gf_area)

    VW, VH = 430, 398                   # main viewport on every sheet
    VC = (14 + VW / 2, 11 + VH / 2)
    px = PX0 + 3

    def site_panel(d):
        y = text_block(d, px, 402, "DESIGN CONCEPT", [
            '"AUL" - an L-shaped hotel wrapped around a',
            "sheltered arrival court, like a nomadic aul.",
            "The L hugs the SW corner of the plot: its two",
            "wings block the prevailing SW winter winds and",
            "open the court to the morning (east) sun.",
        ])
        y = text_block(d, px, y, "SITE NOTES", [
            "1. Hotel placed 3.0 m from the west and south",
            "    boundaries (edge of the site), inside the",
            "    40 x 30 m zone provisioned for it.",
            "2. Access: existing main gates (north) - new",
            "    3.5 m driveway - drop-off aisle and parking.",
            "3. Existing house, terraces, garden and steel",
            "    container are retained unchanged.",
            "4. Step-free route: parking bay P1 - plaza -",
            "    1:12 ramp - main entrance.",
            "5. Restaurant and its terrace face east/south",
            "    for morning daylight.",
            "6. Trees inside the new driveway are",
            "    transplanted to the planting strips.",
            "7. All dimensions in mm.",
        ])

    def gf_panel(d):
        rows = schedule_rows(P1)
        y = table(d, px, 402, "ROOM SCHEDULE - FIRST FLOOR", ("Room", "Area m²", "Spec m²"),
                  rows, (84, 24, 24), h=1.9, lead=3.55)
        y = text_block(d, px, y, "AREAS", [
            f"Building footprint: {gf_area:.1f} m² (spec 400-600)",
            "Guest-room areas include the private bathroom.",
        ])
        text_block(d, px, y, "GENERAL NOTES", GENERAL_NOTES, h=1.9, lead=3.3)

    def ff_panel(d):
        rows = schedule_rows(P2) + [("Public balcony (open)", "51.3", "extra")]
        y = table(d, px, 402, "ROOM SCHEDULE - SECOND FLOOR", ("Room", "Area m²", "Spec m²"),
                  rows, (84, 24, 24), h=1.9, lead=3.7)
        y = text_block(d, px, y, "SECOND-FLOOR NOTES", [
            "1. 8 standard + 2 deluxe rooms, every room with",
            "    its own plan and a private bathroom.",
            "2. Public balcony (sun terrace) on the pool-hall",
            "    roof, reached from both corridors.",
            "3. Two protected stairs (1 and 2) give two",
            "    escape routes from every room.",
            "4. Circular 'shanyrak' rooflight over the lounge",
            "    node where the two wings meet.",
            "5. North facades carry few windows; bathrooms,",
            "    stairs and storage buffer the cold sides.",
        ])
        text_block(d, px, y, "GENERAL NOTES", GENERAL_NOTES, h=1.9, lead=3.3)

    def fnd_panel(d):
        y = table(d, px, 402, "FOOTING SCHEDULE", ("Mark", "b x h", "Under"),
                  [("FS-1 strip", "1200 x 400", "ext. walls 600"),
                   ("FS-2 strip", "800 x 400", "int. bearing walls"),
                   ("FS-3 strip", "800 x 400", "vestibule walls"),
                   ("Pool basin", "RC 250 / 300", "pool + hot tub")],
                  (40, 40, 52), h=1.9, lead=3.8)
        y = text_block(d, px, y, "FOUNDATION NOTES", [
            "1. Simplified conceptual layout: continuous RC",
            "    strip footings under all load-bearing walls.",
            "2. Underside of footings -2.300 m, i.e. below",
            "    the seasonal frost depth assumed for Astana",
            "    (about 1.8-2.0 m) - to be confirmed by a",
            "    geotechnical survey.",
            "3. Stem walls: 600 (exterior) / 400 (interior).",
            "4. Light partitions sit on the 150 mm ground slab.",
            "5. Concrete C25/30; 100 mm blinding under footings.",
            "6. All dimensions in mm, levels in m.",
        ], h=1.9, lead=3.3)

    make_sheet(doc, "A-01 SITE PLAN", "SITE PLAN", "A-01", "1 : 200",
               [(VC[0], VC[1], VW, VH, O_SITE[0] + 27500, O_SITE[1] + 27600, 200)], site_panel)
    make_sheet(doc, "A-02 FIRST FLOOR", "FIRST FLOOR PLAN", "A-02", "1 : 100",
               [(VC[0], VC[1], VW, VH, O_GF[0] + 15200, O_GF[1] + 10400, 100)], gf_panel)
    make_sheet(doc, "A-03 SECOND FLOOR", "SECOND FLOOR PLAN", "A-03", "1 : 100",
               [(VC[0], VC[1], VW, VH, O_FF[0] + 15200, O_FF[1] + 10400, 100)], ff_panel)
    def elev_panel(d):
        y = text_block(d, px, 402, "ELEVATION NOTES", [
            "1. North elevation = front: it faces the arrival",
            "    court; the 45-degree entrance facade and",
            "    vestibule appear foreshortened.",
            "2. South and east facades carry the large",
            "    windows (restaurant, pool hall, guest rooms);",
            "    the north facades have few, small openings.",
            "3. Two-storey wings: parapet +7.200.",
            "    Pool hall: one storey, public balcony on its",
            "    roof at +3.300 with a 1.1 m glass balustrade.",
            "4. Plinth up to FFL \u00b10.000 (450 above ground).",
            "5. Entrance: 3 risers + 1:12 ramp, canopy over.",
        ])
        text_block(d, px, y, "FINISHES", [ln for ln in E.FINISH_NOTES[1:]], h=1.8, lead=3.3)

    def sec_panel(d):
        y = text_block(d, px, 402, "SECTION NOTES", [
            "1. Section A-A is an offset section looking east:",
            "    through the pool at x = 6800 and through",
            "    stair 1 at x = 9300 (jog on grid line D side).",
            "2. Storey height 3.30 m, clear height 3.00 m.",
            "3. Stair 1: 2 flights x 11 risers, 150 x 300 mm,",
            "    half landing at +1.650.",
            "4. Floors and roof: 300 mm RC slabs on",
            "    load-bearing masonry walls.",
            "5. Roof: insulation laid to falls, parapet +7.200.",
            "6. Pool basin: RC, water depth 1.20-1.60 m",
            "    (1.40 m at the cut).",
            "7. Footings at -2.300, below the frost depth.",
        ])
        text_block(d, px, y, "ELEVATIONS", [
            "East = restaurant / terrace side.",
            "West = pool hall and west-wing guest rooms.",
        ])

    make_sheet(doc, "A-04 ELEVATIONS N-S", "ELEVATIONS: NORTH (FRONT), SOUTH", "A-04", "1 : 100",
               [(VC[0], VC[1], VW, VH, O_E4[0] + 15700, O_E4[1] + 16500, 100)], elev_panel)
    make_sheet(doc, "A-05 ELEVATIONS E-W SECTION", "ELEVATIONS E, W; SECTION A-A", "A-05", "1 : 100",
               [(VC[0], VC[1], VW, VH, O_E5[0] + 12000, O_E5[1] + 18700, 100)], sec_panel)
    make_sheet(doc, "S-01 FOUNDATION", "FOUNDATION PLAN", "S-01", "1 : 100 / 1 : 25",
               [(VC[0], VC[1], VW, VH, O_FND[0] + 15200, O_FND[1] + 10400, 100),
                (PX0 + 69, 215, 132, 168, O_DET[0], O_DET[1] - 640, 25)], fnd_panel)
    if "Layout1" in doc.layouts.names():
        doc.layouts.delete("Layout1")
    path = os.path.join(OUT, "AUL_Boutique_Hotel.dxf")
    doc.saveas(path)

    # room schedule as text (for the report)
    with open(os.path.join(OUT, "room_schedule.md"), "w") as f:
        f.write("# AUL Boutique Hotel - room schedule (generated from the drawing)\n\n")
        f.write(f"Building footprint: **{gf_area:.1f} m2** (spec 400-600 m2)\n\n")
        for ttl, P in (("First floor", P1), ("Second floor", P2)):
            f.write(f"## {ttl}\n\n| Room | Area, m2 | Spec, m2 |\n|---|---|---|\n")
            for n, a, s in schedule_rows(P):
                f.write(f"| {n} | {a} | {s} |\n")
            f.write("\n")
        f.write("Guest-room areas include the private bathroom. Public balcony: 51.3 m2.\n")
    import json
    with open(os.path.join(OUT, "rooms.json"), "w") as f:
        json.dump({"footprint": round(gf_area, 1), "second": round(H.FO_2F.area / 1e6, 1),
                   "gf": schedule_rows(P1), "ff": schedule_rows(P2)}, f, indent=1)
    print("saved", path)
    return doc


if __name__ == "__main__":
    build()

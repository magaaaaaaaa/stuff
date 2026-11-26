"""Geometry of the AUL boutique hotel: shared constants + the two floor plans.

Coordinates are millimetres in the building's structural-axis system:
origin = intersection of grid lines 1 and A (centre lines of the west and
south exterior walls); x = east, y = north.
"""
import math

from shapely.geometry import Polygon
from shapely.ops import unary_union

from plan import Plan, rect

SQ2 = math.sqrt(2.0)

# exterior wall centre lines (ground floor / second floor)
AX_GF = [(0, 0), (31200, 0), (31200, 11400), (19800, 11400), (11400, 19800),
         (11400, 24000), (0, 24000)]
AX_2F = [(11400, 0), (31200, 0), (31200, 11400), (19800, 11400), (11400, 19800),
         (11400, 24000), (0, 24000), (0, 9000), (11400, 9000)]
GX = [0, 5800, 8000, 11400, 16000, 20600, 28000, 31200]
GY = [0, 5900, 7800, 9000, 11400, 14600, 19200, 24000]

# diagonal (entrance) facade: local frame at the vestibule centre
A0 = (17700.0, 13500.0)
U = (-1 / SQ2, 1 / SQ2)      # along the facade, towards north-west
N = (1 / SQ2, 1 / SQ2)       # outward normal (north-east)


def dl(s, n=0.0):
    return (A0[0] + U[0] * s + N[0] * n, A0[1] + U[1] * s + N[1] * n)


def offset(ax, dist):
    return Polygon(ax).buffer(dist, join_style=2, mitre_limit=10)


FO_GF, FI_GF = offset(AX_GF, 300), offset(AX_GF, -300)
FO_2F, FI_2F = offset(AX_2F, 300), offset(AX_2F, -300)
VEST_OUT = Polygon([dl(-1500, 0), dl(1500, 0), dl(1500, 2600), dl(-1500, 2600)])
VEST_IN = Polygon([dl(-1200, 300), dl(1200, 300), dl(1200, 2300), dl(-1200, 2300)])
FOOT_GF = unary_union([FO_GF, VEST_OUT])          # building footprint
BALCONY = rect(5400, -300, 11100, 8700)           # public balcony on the pool-hall roof
POOL_ROOF = rect(-300, -300, 11100, 8700)

# pool outline (x, y, bulge) - rectangle with a semicircular "roman" end
POOL = [(1400, 1600, 0), (7600, 1600, 1), (7600, 5600, 0), (1400, 5600, 0)]
POOL_COPING = [(1100, 1300, 0), (7600, 1300, 1), (7600, 5900, 0), (1100, 5900, 0)]


def pool_polygon(x0=1400, y0=1600, x1=7600, y1=5600, grow=0):
    r = (y1 - y0) / 2 + grow
    cy = (y0 + y1) / 2
    pts = [(x0 - grow, y0 - grow), (x1, y0 - grow)]
    pts += [(x1 + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in range(-85, 90, 5)]
    pts += [(x1, y1 + grow), (x0 - grow, y1 + grow)]
    return Polygon(pts)


def bath(x0, y0, x1, y1):
    return rect(x0, y0, x1, y1)


# =====================================================================
#  FIRST (GROUND) FLOOR
# =====================================================================
def first_floor(d):
    P = Plan(d, FOOT_GF)
    fi = FI_GF

    # ---------------- wellness: pool hall + sauna + changing -------------
    pool_hall = rect(300, 300, 11250, 8850)
    d.hatch(pool_polygon(), "A-FLOOR-HATCH", "DASH", scale=30)
    d.plb(POOL, "A-POOL", close=True)
    d.plb(POOL_COPING, "A-POOL", close=True, lineweight=13)
    for r in (800, 1400):                                   # roman steps
        d.arc((7600, 3600), r, -90, 90, "A-POOL", lineweight=13)
    d.line((7600, 1600), (7600, 5600), "A-POOL", lineweight=13)
    d.text("POOL 4.0 x 8.2 m", (4300, 3900), 200, "A-TEXT-ROOM", style="ARIALBD")
    d.text("water depth 1.20 - 1.60 m", (4300, 3500), 150, "A-TEXT-ROOM")
    d.text("steps", (8500, 3600), 130, "A-TEXT-ROOM", rot=90)
    d.circle((9500, 7350), 1000, "A-POOL")                 # hot tub
    d.circle((9500, 7350), 800, "A-POOL", lineweight=13)
    d.text("HOT TUB", (9500, 7350), 130, "A-TEXT-ROOM")
    for y in (6500, 7400):
        d.lounger((300, y), 0)
    P.room("pool", pool_hall, "INDOOR POOL HALL", at=(5300, 7500), no="",
           spec="additional", hd=(8400, 300, 11250), vd=(10850, 300, 8850))

    P.room("ante", rect(300, 9150, 3000, 11000), "SHOWER\nLOBBY", at=(760, 10550), h=105)
    d.shower(2100, 9150, 3000, 10050)
    P.room("sauna", rect(300, 11300, 3000, 14475), "SAUNA", at=(2000, 12600), h=170,
           spec="additional", hd=(11650, 300, 3000), vd=(1300, 11300, 14475))
    d.rect(300, 13875, 3000, 14475, "A-FURNITURE")          # benches
    d.rect(300, 12100, 900, 13875, "A-FURNITURE")
    for x in (975, 1650, 2325):
        d.line((x, 13875), (x, 14475), "A-FURNITURE")
    for y in (12690, 13280):
        d.line((300, y), (900, y), "A-FURNITURE")
    d.rect(2400, 13150, 2950, 13700, "A-FURNITURE")         # sauna heater
    d.line((2400, 13150), (2950, 13700), "A-FURNITURE")
    d.line((2400, 13700), (2950, 13150), "A-FURNITURE")

    P.room("chgF", rect(3300, 9150, 5850, 12600), "CHANGING (F)", at=(4750, 10800), h=120,
           spec="additional")
    d.shower(3300, 9150, 4150, 10000)
    d.rect(3300, 10300, 3680, 12600, "A-FURNITURE")          # lockers
    for y in (10760, 11220, 11680, 12140):
        d.line((3300, y), (3680, y), "A-FURNITURE")
    d.rect(3720, 10500, 4050, 12100, "A-FURNITURE")          # bench
    d.line((5000, 11350), (5850, 11350), "A-SANITARY")       # wc cubicle
    d.line((5000, 11350), (5000, 11750), "A-SANITARY")
    d.wc((5425, 12600), 270)
    d.basin((5850, 10350), 180)

    P.room("chgM", rect(6150, 9150, 8700, 12600), "CHANGING (M)", at=(7250, 10800), h=120,
           spec="additional")
    d.shower(7850, 9150, 8700, 10000)
    d.rect(8320, 10300, 8700, 12600, "A-FURNITURE")
    for y in (10760, 11220, 11680, 12140):
        d.line((8320, y), (8700, y), "A-FURNITURE")
    d.rect(7950, 10500, 8280, 12100, "A-FURNITURE")
    d.line((6150, 11350), (7000, 11350), "A-SANITARY")
    d.line((7000, 11350), (7000, 11750), "A-SANITARY")
    d.wc((6575, 12600), 270)
    d.basin((6150, 10350), 0)

    P.room("plant", rect(9000, 9150, 11250, 12600), "PLANT ROOM", at=(10125, 11350), h=130,
           sub="pool filtration / boiler")
    d.circle((9600, 9800), 380, "A-FURNITURE")
    d.circle((10600, 9800), 380, "A-FURNITURE")
    d.rect(9150, 10300, 9750, 10800, "A-FURNITURE")

    # ---------------- west wing circulation + stair 1 -------------------
    corr_w = unary_union([rect(3300, 12900, 11275, 14475), rect(5925, 14475, 7875, 20100)])
    stair1 = rect(8125, 14475, 11275, 19075)
    P.room("corrW", corr_w, "CORRIDOR", at=(6900, 13700), h=150,
           hd=(13150, 3300, 11275), vd=(6250, 14475, 20100))
    P.room("stair1", stair1, "STAIR 1", label=False)
    P.dogleg(8125, 11275, 14725, 10, 300, 19075, level="lower", well=350, name="STAIR 1")

    staff = Polygon([(8125, 19325), (11100, 19325), (11100, 23700), (5925, 23700),
                     (5925, 20350), (8125, 20350)])
    P.room("staff", staff, "STAFF ROOM", at=(9000, 21850), spec="15-30",
           hd=(22600, 5925, 11100), vd=(10700, 19325, 23700))
    d.table4((9400, 20650), 900)
    d.rect(5925, 21300, 6325, 23000, "A-FURNITURE")          # staff lockers
    for y in (21725, 22150, 22575):
        d.line((5925, y), (6325, y), "A-FURNITURE")
    d.rect(8600, 23100, 10900, 23700, "A-FURNITURE")         # kitchenette counter
    d.circle((9100, 23400), 180, "A-FURNITURE")

    # ---------------- guest rooms 103 / 104 (west wing) -----------------
    R = rect(300, 14725, 5675, 18775)
    B = bath(3575, 16725, 5625, 18725)
    P.guest("103", "Standard room", R, B, at=(2300, 15950), bath_at=(4450, 17400),
            hd=(14975, 300, 5675), vd=(650, 14725, 18775), spec="18-25")
    d.shower(4725, 17825, 5625, 18725)
    d.wc((4050, 18725), 270)
    d.basin((3575, 17250), 0)
    d.bed((1750, 18775), 270)
    d.desk(300, 15250, 900, 16350, (1150, 15800))
    d.wardrobe(3600, 14725, 4800, 15300)

    R = rect(300, 19025, 5675, 23700)
    B = bath(3175, 21900, 5625, 23700)
    P.guest("104", "Standard room", R, B, at=(1650, 20300), bath_at=(4050, 22500),
            hd=(19350, 300, 5675), vd=(2650, 19025, 23700), spec="18-25")
    d.tub(3175, 22950, 4875, 23700)
    d.wc((5625, 22400), 180)
    d.basin((5225, 23700), 270)
    d.bed((1450, 23700), 270)
    d.desk(3300, 21000, 4500, 21600, (3900, 20750))
    d.wardrobe(4250, 19025, 5450, 19600)

    # ---------------- guest rooms 101 / 102 (south, centre) -------------
    R = rect(11550, 300, 15875, 5775)
    B = bath(11550, 3375, 13350, 5725)
    P.guest("101", "Standard room", R, B, at=(13050, 2350), bath_at=(12500, 4700),
            hd=(560, 11550, 15875), vd=(15100, 300, 5775), spec="18-25")
    d.shower(11550, 3375, 12450, 4275)
    d.wc((12150, 5725), 270)
    d.basin((12950, 3375), 90)
    d.bed((15875, 1750), 180)
    d.desk(11550, 850, 12150, 1750, (12400, 1300))
    d.wardrobe(15275, 3500, 15875, 4850)

    R = rect(16125, 300, 20475, 5775)
    B = bath(18175, 3475, 20425, 5725)
    P.guest("102", "Standard room", R, B, at=(18950, 1900), bath_at=(18850, 4000),
            hd=(560, 16125, 20475), vd=(17650, 300, 5775), spec="18-25",
            sub="ACCESSIBLE")
    d.shower(19325, 3475, 20425, 4575)                       # level-access shower
    d.wc((20425, 5200), 180)
    d.basin((18700, 5725), 270)
    d.circle((19050, 4550), 750, "A-ABOVE")                  # 1500 turning circle
    d.bed((16125, 1750), 0)
    d.desk(19875, 2150, 20475, 3100, (19620, 2650))

    # ---------------- lobby: corridor, WCs, reception, luggage ----------
    P.room("c1", rect(11550, 6025, 16300, 7650), "CORRIDOR", at=(12800, 7150), h=120,
           area_label=False)
    P.room("wc2", rect(11550, 7950, 13300, 11250), "PUBLIC\nWC 2", at=(12550, 9500), h=115,
           spec="3-8", vd=(11850, 7950, 11250))
    d.wc((11950, 11250), 270)
    d.line((12400, 10250), (12400, 11250), "A-SANITARY")
    d.wc((12850, 11250), 270)
    d.basin((13300, 8700), 180)
    P.room("wc1", rect(13600, 7950, 16000, 11250), "PUBLIC WC 1", at=(14700, 9900), h=115,
           sub="accessible", spec="3-8", hd=(8900, 13600, 16000))
    d.wc((14200, 11250), 270)
    d.basin((16000, 10300), 180)
    d.circle((14800, 9850), 750, "A-ABOVE")

    hall = unary_union([rect(16300, 6025, 20475, 11550),
                        rect(11525, 11550, 20475, 15475)]).intersection(fi)
    P.room("hall", hall, "RECEPTION", at=(14500, 12550), spec="20-50",
           sub="lobby & lounge", hd=(6500, 16300, 20475), vd=(20100, 6025, 11100))
    d.dim_h(11525, 19226, 11900)
    d.pl([(12500, 13950), (15000, 13950), (15000, 14550), (12500, 14550)], "A-FURNITURE",
         close=True)                                         # reception desk
    d.text("RECEPTION DESK", (13750, 14250), 110, "A-TEXT-ROOM")
    d.circle((13200, 14950), 200, "A-FURNITURE")
    d.circle((14300, 14950), 200, "A-FURNITURE")
    d.sofa((17300, 11050), 270, w=1900)
    d.sofa((20475, 9000), 180, w=1900)
    d.round_table((18400, 9400), 400, n=0)
    d.sofa((16300, 9300), 0, w=1700)
    lug = rect(11525, 15725, 16000, 19800).intersection(fi)
    P.room("lug", lug, "LUGGAGE\n& OFFICE", at=(12700, 16700), h=120)

    vest = VEST_IN
    P.room("vest", vest, "ENTRANCE\nVESTIBULE", at=dl(0, 1300), h=105, sub="2400 x 2000")

    # ---------------- restaurant, kitchen, stair 2 ----------------------
    rest = Polygon([(20725, 300), (30900, 300), (30900, 5775), (27875, 5775),
                    (27875, 7675), (20725, 7675)])
    P.room("rest", rest, "RESTAURANT", at=(24300, 4500), spec="50-90", h=240,
           sub="48 seats, east + south daylight",
           hd=(5300, 20725, 30900), vd=(21050, 300, 7675))
    for x in (22300, 24300, 26300, 28300, 30150):
        d.table4((x, 1500))
    for x in (22300, 24300, 26300, 28300):
        d.table4((x, 3200))
    for x in (22700, 24900, 26900):
        d.round_table((x, 6450), 420)
    d.round_table((29900, 3900), 420)
    kit = rect(20725, 7925, 27875, 11100)
    P.room("kit", kit, "KITCHEN", at=(24300, 9300), spec="20-40",
           hd=(8250, 20725, 27875), vd=(27500, 7925, 11100))
    d.rect(20725, 10500, 26000, 11100, "A-FURNITURE")        # worktops under windows
    d.rect(20725, 8600, 21325, 10500, "A-FURNITURE")
    d.rect(23000, 9700, 25600, 10200, "A-FURNITURE")         # island / pass
    for x in (21500, 23300, 25200):
        d.circle((x, 10800), 170, "A-FURNITURE")
    d.rect(27275, 7925, 27875, 9300, "A-FURNITURE")          # cold store
    d.line((27275, 7925), (27875, 9300), "A-FURNITURE")
    stair2 = rect(28125, 6025, 30900, 11100)
    P.room("stair2", stair2, "STAIR 2", label=False)
    P.dogleg(28125, 30900, 7300, 10, 270, 11100, level="lower", well=175, name="STAIR 2")

    # ---------------- doors --------------------------------------------
    D = P.door
    D(dl(0, 2450), 135, 300, dl(0, 4000), w=1830, leaves=2)          # main entrance
    D(dl(0, 0), 135, 600, dl(0, 1000), w=1830, leaves=2)
    P.opening((11400, 13690), 90, 250, 1400)                         # hall <-> west wing
    D((12700, 15600), 0, 250, (12700, 16500))
    D((20600, 6850), 90, 250, (21500, 6850), w=1626, leaves=2)       # restaurant
    D((17050, 5900), 0, 250, (17050, 5000), w=915, hinge="a")        # 102 (accessible)
    D((18025, 4650), 90, 300, (17000, 4650), w=915, hinge="a")
    D((14800, 5900), 0, 250, (14800, 5000), hinge="b")               # 101
    D((13500, 4650), 90, 300, (14500, 4650), hinge="a")
    D((12425, 7800), 0, 300, (12425, 8500), hinge="a")               # public WCs
    D((14800, 7800), 0, 300, (14800, 8500), w=915, hinge="b")
    D((1650, 9000), 0, 300, (1650, 10000), hinge="a")                # shower lobby
    D((1650, 11150), 0, 300, (1650, 10500), hinge="b")               # sauna
    D((4575, 12750), 0, 300, (4575, 12000), hinge="a")               # changing F
    D((4575, 9000), 0, 300, (4575, 9800), hinge="b")
    D((7425, 12750), 0, 300, (7425, 12000), hinge="b")               # changing M
    D((7425, 9000), 0, 300, (7425, 9800), hinge="a")
    D((10100, 12750), 0, 300, (10100, 12000), hinge="a")             # plant
    D((5800, 15550), 90, 250, (4800, 15550), hinge="a")              # 103
    D((4350, 16575), 0, 300, (4350, 15800), hinge="a")
    D((5800, 19500), 90, 250, (4800, 19500), hinge="a")              # 104
    D((4500, 21750), 0, 300, (4500, 21000), hinge="b")
    D((6900, 20225), 0, 250, (6900, 21000), hinge="a")               # staff room
    D((7100, 24000), 0, 600, (7100, 23000), w=915, hinge="a", side="N")
    D((22200, 7800), 0, 250, (22200, 8500), hinge="a")               # kitchen in / out
    D((26300, 7800), 0, 250, (26300, 7000), hinge="b")
    D((26600, 11400), 0, 600, (26600, 12500), w=915, hinge="a", side="N")
    D((29500, 5900), 0, 250, (29500, 6500), hinge="a")               # restaurant -> stair 2
    D((31200, 6650), 90, 600, (32000, 6650), w=915, hinge="a", side="E")
    D((31200, 3900), 90, 600, (32000, 3900), w=1830, leaves=2, side="E")
    D((0, 4700), 90, 600, (-1000, 4700), w=915, hinge="a", side="W")

    # ---------------- windows ------------------------------------------
    W = P.window
    for x in (2500, 5700, 8900):
        W((x, 0), 0, 2400, side="S")
    W((13700, 0), 0, 1800, side="S")
    W((18300, 0), 0, 1800, side="S")
    for x in (22200, 24900, 27600):
        W((x, 0), 0, 2100, side="S")
    W((30000, 0), 0, 1500, side="S")
    W((31200, 1700), 90, 1800, side="E")
    W((31200, 10300), 90, 900, side="E")
    W((22300, 11400), 0, 1200, side="N")
    W((24400, 11400), 0, 1200, side="N")
    W(dl(-2300), 135, 1000)
    W(dl(2300), 135, 1000)
    W(dl(5700), 135, 900)
    W((11400, 21900), 90, 1200)
    W((9600, 24000), 0, 1200, side="N")
    W((0, 2300), 90, 2400, side="W")
    W((0, 7000), 90, 2400, side="W")
    W((0, 16900), 90, 1800, side="W")
    W((0, 20400), 90, 1800, side="W")

    P.build()
    return P


# =====================================================================
#  SECOND FLOOR
# =====================================================================
def second_floor(d):
    P = Plan(d, FO_2F)
    fi = FI_2F

    # roof of the pool hall (below) and the public balcony on it
    d.rect(-300, -300, 11100, 8700, "A-BALCONY", lineweight=18)
    d.rect(5400, -300, 11100, 8700, "A-BALCONY")
    d.pl([(11100, -150), (5550, -150), (5550, 8700)], "A-BALCONY", lineweight=13)  # railing
    d.hatch(rect(5550, -150, 11100, 8700), "A-FLOOR-HATCH", "NET", scale=120)
    d.label([("PUBLIC BALCONY", 220, "ARIALBD"), ("sun terrace on the pool-hall roof", 140, "ARIAL"),
             (f"{5.7 * 9.0:.1f} m²", 170, "ARIAL")], (8300, 5200))
    d.dim_h(5400, 11100, 800)
    d.dim_v(-300, 8700, 10800)
    for c in ((7000, 2300), (9500, 2300), (9500, 7200)):
        d.round_table(c, 420)
    d.lounger((6000, 3600), 90)
    d.lounger((6900, 3600), 90)
    for x0 in (800, 2900):                                   # rooflights over the pool
        d.rect(x0, 1800, x0 + 1300, 5400, "A-BALCONY", lineweight=13)
        d.line((x0, 1800), (x0 + 1300, 5400), "A-BALCONY", lineweight=5)
        d.line((x0, 5400), (x0 + 1300, 1800), "A-BALCONY", lineweight=5)
    d.label([("POOL-HALL ROOF", 150, "ARIAL"), ("(not accessible)", 120, "ARIAL"),
             ("2 rooflights", 120, "ARIAL")], (2500, 7100))
    d.shape(VEST_OUT.difference(FO_2F), "A-BELOW")           # entrance canopy below
    d.text("vestibule roof / canopy below", dl(0, 3300), 120, "A-TEXT", rot=-45)

    # ---------------- south rooms 201-203 + deluxe 209 ------------------
    R = rect(11700, 300, 15875, 5775)
    B = bath(11700, 3475, 13450, 5725)
    P.guest("201", "Standard room", R, B, at=(13100, 2350), bath_at=(12850, 4500),
            hd=(560, 11700, 15875), vd=(15100, 300, 5775), spec="18-25")
    d.shower(11700, 3475, 12600, 4375)
    d.wc((13450, 5250), 180)
    d.basin((12150, 5725), 270)
    d.bed((15875, 1750), 180)
    d.desk(11700, 850, 12300, 1750, (12550, 1300))
    d.wardrobe(15275, 3500, 15875, 4850)

    R = rect(16125, 300, 20475, 5775)
    B = bath(18275, 3575, 20425, 5725)
    P.guest("202", "Standard room", R, B, at=(19150, 1650), bath_at=(19100, 4350),
            hd=(560, 16125, 20475), vd=(17800, 300, 5775), spec="18-25", sub="twin")
    d.tub(18275, 4975, 19975, 5725)
    d.wc((20425, 4350), 180)
    d.basin((19900, 3575), 90)
    d.bed((16125, 2350), 0, w=900, tables=(False, False))
    d.bed((16125, 1050), 0, w=900, tables=(True, False))
    d.desk(18700, 2600, 20100, 3150, (19400, 2380))
    d.wardrobe(16125, 3600, 16725, 4900)

    R = rect(20725, 300, 24875, 5775)
    B = bath(23075, 3075, 24825, 5725)
    P.guest("203", "Standard room", R, B, at=(22000, 3400), bath_at=(23950, 4250),
            hd=(480, 20725, 24875), vd=(21150, 300, 5775), spec="18-25")
    d.shower(23075, 4825, 23975, 5725)
    d.wc((24825, 5250), 180)
    d.basin((24825, 3600), 180)
    d.bed((24875, 1650), 180, tables=(False, False))
    d.desk(20725, 900, 21325, 2100, (21570, 1500))
    d.wardrobe(20725, 3300, 21325, 4700)

    R = rect(25125, 300, 30900, 5775)
    B = bath(28400, 3575, 30900, 5725)
    P.guest("209", "Deluxe room", R, B, at=(26650, 3350), bath_at=(29250, 4300),
            hd=(650, 25125, 30900), vd=(25500, 300, 5775), spec="28-40",
            sub="south-east corner")
    d.tub(28400, 4975, 30100, 5725)
    d.wc((30900, 4300), 180)
    d.basin((28900, 3575), 90)
    d.basin((29600, 3575), 90)
    d.bed((28300, 300), 90, w=1800)
    d.sofa((25125, 1500), 0, w=1800)
    d.round_table((26500, 1500), 300, n=0)
    d.desk(30300, 1900, 30900, 3200, (30050, 2550))
    d.wardrobe(25125, 3900, 25725, 5500)

    # ---------------- 208 (courtyard room) + deluxe 210 -----------------
    R = rect(20725, 7925, 27875, 11100)
    B = bath(20775, 7975, 22225, 11100)
    P.guest("208", "Standard room", R, B, at=(24650, 9450), bath_at=(21500, 9300),
            hd=(10650, 22525, 27875), vd=(27550, 7925, 11100), spec="18-25")
    d.shower(20775, 10200, 21675, 11100)
    d.wc((20775, 9500), 0)
    d.basin((21500, 7975), 90)
    d.bed((27875, 9700), 180)
    d.desk(22700, 10550, 23900, 11100, (23300, 10320))
    d.wardrobe(23900, 7925, 25300, 8500)

    main = Polygon([(13525, 7925), (17600, 7925), (17600, 14000), (13525, 18000)]).intersection(fi)
    b10 = bath(17900, 7975, 20425, 10200)
    wd = rect(17900, 10500, 20475, 14000).intersection(fi)
    tot = (main.area + b10.area + wd.area) / 1e6
    P.rooms.append(dict(key="r210", no="210", name="Deluxe room", poly=main, spec="28-40",
                        group="guest", area=tot, bed=(main.area + wd.area) / 1e6,
                        bath=b10.area / 1e6, count=True))
    P.rooms.append(dict(key="b210", no="", name="Bath 210", poly=b10, spec="", group="bath",
                        area=b10.area / 1e6, count=False))
    P.rooms.append(dict(key="w210", no="", name="Wardrobe 210", poly=wd, spec="", group="bath",
                        area=wd.area / 1e6, count=False))
    d.label([("210", 260, "ARIALBD"), ("DELUXE ROOM", 140, "ARIAL"),
             ("courtyard view", 140, "ARIAL"), (f"{tot:.1f} m²", 160, "ARIAL")],
            (15300, 13350))
    d.label([("BATH", 120, "ARIAL"), (f"{b10.area / 1e6:.1f} m²", 120, "ARIAL")],
            (19000, 9500))
    d.label([("DRESSING", 110, "ARIAL"), (f"{wd.area / 1e6:.1f} m²", 110, "ARIAL")],
            (18750, 11250))
    d.dim_h(13525, 17600, 8250)
    d.dim_v(7925, 17251, 13900)
    d.tub(17900, 7975, 19600, 8725)
    d.wc((20425, 9300), 180)
    d.basin((18500, 10200), 270)
    d.bed((13525, 10500), 0, w=1800)
    d.sofa(dl(2900, -330 - 850 - 600), 45, w=1800)
    d.desk(16400, 8100, 17550, 8700, (16950, 8950))
    d.line((17900, 12300), (18500, 11700), "A-FURNITURE")      # dressing shelves
    d.rect(19875, 10500, 20475, 11000, "A-FURNITURE")

    # ---------------- west wing rooms 204-207 --------------------------
    R = rect(300, 9300, 5675, 13775)
    B = bath(3575, 11725, 5625, 13725)
    P.guest("204", "Standard room", R, B, at=(2350, 10700), bath_at=(4450, 12500),
            hd=(9550, 300, 5675), vd=(650, 9300, 13775), spec="18-25")
    d.shower(4725, 12825, 5625, 13725)
    d.wc((4050, 13725), 270)
    d.basin((3575, 12300), 0)
    d.bed((1650, 13775), 270)
    d.desk(300, 10050, 900, 11250, (1150, 10650))
    d.wardrobe(3600, 9300, 4800, 9875)

    R = rect(300, 14025, 5675, 18575)
    B = bath(3875, 14075, 5625, 16425)
    P.guest("205", "Standard room", R, B, at=(2300, 16950), bath_at=(4600, 15250),
            hd=(17650, 300, 5675), vd=(3300, 14025, 18575), spec="18-25")
    d.shower(4725, 14075, 5625, 14975)
    d.wc((3875, 14600), 0)
    d.basin((5625, 15800), 180)
    d.bed((1900, 14025), 90)
    d.desk(300, 16600, 900, 17800, (1150, 17200))
    d.wardrobe(3700, 18025, 4850, 18575)

    R = rect(300, 18825, 5675, 23700)
    B = bath(3175, 21900, 5625, 23700)
    P.guest("206", "Standard room", R, B, at=(1650, 20250), bath_at=(4050, 22500),
            hd=(19150, 300, 5675), vd=(3000, 18825, 23700), spec="18-25", sub="twin")
    d.tub(3175, 22950, 4875, 23700)
    d.wc((5625, 22400), 180)
    d.basin((5225, 23700), 270)
    d.bed((900, 23700), 270, w=900, tables=(False, True))
    d.bed((2300, 23700), 270, w=900, tables=(False, False))
    d.desk(3300, 21000, 4500, 21600, (3900, 20750))
    d.wardrobe(4250, 18825, 5450, 19400)

    poly7 = Polygon([(8125, 19325), (11100, 19325), (11100, 23700), (5925, 23700),
                     (5925, 20350), (8125, 20350)])
    B = bath(5975, 21850, 8125, 23700)
    P.guest("207", "Standard room", poly7, B, at=(9650, 20850), bath_at=(7050, 22500),
            hd=(19650, 8125, 11100), vd=(10800, 19325, 23700), spec="18-25")
    d.shower(5975, 22800, 6875, 23700)
    d.wc((7600, 23700), 270)
    d.basin((6600, 21850), 90)
    d.bed((9750, 23700), 270)
    d.wardrobe(8200, 19325, 9250, 19875)

    # ---------------- circulation, storage, stairs ----------------------
    corr = unary_union([
        rect(11700, 6025, 27875, 7675), rect(11700, 7675, 13275, 9300),
        rect(11525, 9300, 13275, 14475), rect(11525, 14475, 13275, 20000),
        rect(7875, 12900, 11525, 14475), rect(5925, 9300, 7875, 20100),
    ]).intersection(fi)
    P.room("corr", corr, "CORRIDOR", at=(16300, 7050), h=160,
           hd=(6350, 11700, 27875), vd=(7550, 9300, 20100))
    d.label([("LOUNGE", 140, "ARIALBD"), ("NODE", 140, "ARIALBD")], (12400, 11000))
    d.label([("READING", 110, "ARIAL"), ("NOOK", 110, "ARIAL")], (12350, 15600))
    d.circle((12400, 12900), 700, "A-ABOVE")                 # shanyrak rooflight above
    d.line((11900, 12400), (12900, 13400), "A-ABOVE")
    d.line((11900, 13400), (12900, 12400), "A-ABOVE")
    d.text("shanyrak rooflight", (12400, 13800), 100, "A-TEXT")
    d.text("above", (12400, 13630), 100, "A-TEXT")
    d.sofa((11525, 16500), 0, w=1400, d=700)
    d.dim_h(11525, 13275, 9800)
    P.room("stair1", rect(8125, 14475, 11275, 19075), "STAIR 1", label=False)
    P.dogleg(8125, 11275, 14725, 10, 300, 19075, level="upper", well=350, name="STAIR 1")
    P.room("store", rect(8125, 9300, 11275, 12650), "STORAGE", at=(9650, 11350), h=170,
           sub="linen store", spec="6-12", hd=(10200, 8125, 11275),
           vd=(11000, 9300, 12650))
    d.rect(8125, 9300, 8625, 12300, "A-FURNITURE")           # shelving
    for y in (10050, 10800, 11550):
        d.line((8125, y), (8625, y), "A-FURNITURE")
    d.rect(9300, 9300, 11275, 9800, "A-FURNITURE")
    P.room("stair2", rect(28125, 6025, 30900, 11100), "STAIR 2", label=False)
    P.dogleg(28125, 30900, 7300, 10, 270, 11100, level="upper", well=175, name="STAIR 2")

    # ---------------- doors --------------------------------------------
    D = P.door
    D((14800, 5900), 0, 250, (14800, 5000), hinge="b")               # 201
    D((13600, 4650), 90, 300, (14500, 4650), hinge="a")
    D((17100, 5900), 0, 250, (17100, 5000), hinge="a")               # 202
    D((18125, 4500), 90, 300, (17200, 4500), hinge="a")
    D((21700, 5900), 0, 250, (21700, 5000), hinge="a")               # 203
    D((22925, 4350), 90, 300, (22000, 4350), hinge="a")
    D((26700, 5900), 0, 250, (26700, 5000), hinge="a")               # 209
    D((28250, 4650), 90, 300, (27500, 4650), hinge="b")
    D((23300, 7800), 0, 250, (23300, 8600), hinge="a")               # 208
    D((22375, 9500), 90, 300, (23200, 9500), hinge="b")
    D((14600, 7800), 0, 250, (14600, 8600), hinge="a")               # 210
    D((17750, 9300), 90, 300, (17000, 9300), hinge="a")
    P.opening((17750, 11300), 90, 300, 800)
    D((9700, 12775), 0, 250, (9700, 12000), hinge="a")               # storage
    D((5800, 10400), 90, 250, (4800, 10400), hinge="a")              # 204
    D((4350, 11575), 0, 300, (4350, 10800), hinge="a")
    D((5800, 17600), 90, 250, (4800, 17600), hinge="a")              # 205
    D((4700, 16575), 0, 300, (4700, 15800), hinge="a")
    D((5800, 19500), 90, 250, (4800, 19500), hinge="a")              # 206
    D((4500, 21750), 0, 300, (4500, 21000), hinge="b")
    D((6900, 20225), 0, 250, (6900, 21000), hinge="a")               # 207
    D((8275, 22700), 90, 300, (9200, 22700), hinge="a")
    D((28000, 6850), 90, 250, (28800, 6850), hinge="a")              # stair 2
    D((11400, 6850), 90, 600, (10500, 6850), w=915, hinge="a")       # balcony doors
    D((6900, 9000), 0, 600, (6900, 8000), w=915, hinge="a")

    # ---------------- windows ------------------------------------------
    W = P.window
    W((13700, 0), 0, 1800, side="S")
    W((18300, 0), 0, 1800, side="S")
    W((22800, 0), 0, 1800, side="S")
    W((26600, 0), 0, 1800, side="S")
    W((29300, 0), 0, 1800, side="S")
    W((31200, 1800), 90, 1800, side="E")
    W((31200, 4650), 90, 600, side="E")
    W((31200, 10300), 90, 900, side="E")
    W((24000, 11400), 0, 1500, side="N")
    W((26300, 11400), 0, 1500, side="N")
    W(dl(1400), 135, 1800)
    W(dl(3900), 135, 1800)
    W(dl(7200), 135, 1200)
    W((11400, 22000), 90, 1500)
    W((9700, 24000), 0, 1200, side="N")
    W((7000, 24000), 0, 600, side="N")
    W((0, 10500), 90, 1800, side="W")
    W((0, 16300), 90, 1800, side="W")
    W((0, 20300), 90, 1800, side="W")
    W((2000, 9000), 0, 1200)

    P.build()
    return P


# =====================================================================
#  exterior dimension chains + grid (shared by both floors)
# =====================================================================
def exterior_dims(d, P, second=False):
    x_w = 11100 if second else -300
    xs_s = [x_w, 31500] + P.ext["S"]
    d.chain_h(xs_s, -1400, -300)
    d.chain_h(GX, -2200, -300)
    d.chain_h([-300, 31500], -3000, -300)
    xs_n = [-300, 11700] + [v for v in P.ext["N"] if v < 11700]
    d.chain_h(xs_n, 25400, 24300)
    xs_n2 = [19924, 31500] + [v for v in P.ext["N"] if v > 11700]
    d.chain_h(xs_n2, 13000, 11700)
    d.chain_h(GX, 26200, 24300)
    y_s = 8700 if second else -300
    d.chain_v([y_s, 24300] + [v for v in P.ext["W"]], -1400, -300)
    d.chain_v(GY, -2200, -300)
    d.chain_v([-300, 24300], -3000, -300)
    d.chain_v([-300, 11700] + P.ext["E"], 32600, 31500)
    d.chain_v(GY, 33400, 31500)
    # diagonal facade
    k = 300 * (SQ2 - 1)
    if second:
        d.dim_al((11700, 19800 + k), (19800 + k, 11700), 1100)
    else:                                   # facade either side of the vestibule
        d.dim_al(dl(8785, 300), dl(1500, 300), 1200)

    P.grid(GX, GY, (-3700, 34100), (-3700, 26900))


def level_mark(d, pos, text):
    x, y = pos
    d.pl([(x - 180, y + 180), (x, y), (x + 180, y + 180)], "A-TEXT", close=True)
    d.line((x - 180, y + 180), (x + 900, y + 180), "A-TEXT")
    d.text(text, (x + 250, y + 300), 150, "A-TEXT", "BL")

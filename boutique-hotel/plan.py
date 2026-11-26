"""Floor-plan builder: rooms first, walls = footprint minus rooms, then openings."""
import math

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from cadlib import polys


class Plan:
    def __init__(self, d, footprint):
        self.d = d
        self.fp = footprint
        self.rooms = []          # dicts: key, no, name, poly, spec, group
        self.cuts = []
        self.openings = []       # every door / window / opening (for elevations, section)
        self.symbols = []        # deferred door / window drawing
        self.ext = {"S": [], "N": [], "E": [], "W": []}   # opening edges per facade
        self.walls = None

    # ------------------------------------------------------------- rooms
    def room(self, key, poly, name, at=None, no="", spec="", hd=None, vd=None,
             label=True, h=200, sub=None, group="", area_label=True, count=True):
        r = dict(key=key, no=no, name=name, poly=poly, spec=spec, group=group,
                 area=poly.area / 1e6, count=count)
        self.rooms.append(r)
        d = self.d
        if label and at is not None:
            lines = []
            if no:
                lines.append((no, h * 1.25, "ARIALBD"))
            for part in name.split("\n"):
                lines.append((part, h if not no else h * 0.75, "ARIALBD" if not no else "ARIAL"))
            if sub:
                lines.append((sub, h * 0.75, "ARIAL"))
            if area_label:
                lines.append((f"{r['area']:.1f} m²", h * 0.8, "ARIAL"))
            d.label(lines, at)
        if hd:
            d.dim_h(hd[1], hd[2], hd[0])
        if vd:
            d.dim_v(vd[1], vd[2], vd[0])
        return r

    def guest(self, no, kind, R, B, at, bath_at, hd=None, vd=None, spec="", sub=None):
        """Guest room = bedroom (R minus bath and its 300 mm walls) + private bath."""
        bed = R.difference(B.buffer(300, join_style=2))
        total = (bed.area + B.area) / 1e6
        self.rooms.append(dict(key=f"r{no}", no=no, name=kind, poly=bed, spec=spec,
                               group="guest", area=total, bed=bed.area / 1e6,
                               bath=B.area / 1e6, count=True))
        self.rooms.append(dict(key=f"b{no}", no="", name=f"Bath {no}", poly=B, spec="",
                               group="bath", area=B.area / 1e6, count=False))
        d = self.d
        lines = [(no, 260, "ARIALBD"), (kind.upper(), 140, "ARIAL")]
        if sub:
            lines.append((sub, 140, "ARIAL"))
        lines.append((f"{total:.1f} m²", 160, "ARIAL"))
        d.label(lines, at)
        d.label([("BATH", 120, "ARIAL"), (f"{B.area / 1e6:.1f} m²", 120, "ARIAL")], bath_at)
        if hd:
            d.dim_h(hd[1], hd[2], hd[0])
        if vd:
            d.dim_v(vd[1], vd[2], vd[0])
        return bed

    # ---------------------------------------------------------- openings
    @staticmethod
    def _vec(ang):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        return (c, s), (-s, c)

    def _cut(self, c, ang, w, t):
        dv, nv = self._vec(ang)
        hw, ht = w / 2, t / 2 + 3
        pts = [(c[0] + dv[0] * a + nv[0] * b, c[1] + dv[1] * a + nv[1] * b)
               for a, b in ((-hw, -ht), (hw, -ht), (hw, ht), (-hw, ht))]
        poly = Polygon(pts)
        self.cuts.append(poly)
        return poly

    def _edges(self, side, c, ang, w):
        if side:
            v = c[0] if side in "SN" else c[1]
            self.ext[side] += [v - w / 2, v + w / 2]

    def door(self, c, ang, t, into, w=813, hinge="a", leaves=1, side=None):
        """Door in a wall running at `ang` through centre point c (wall centre line)."""
        self.openings.append(dict(kind="door", c=c, ang=ang, w=w, t=t, leaves=leaves,
                                  poly=self._cut(c, ang, w, t)))
        self._edges(side, c, ang, w)
        dv, nv = self._vec(ang)
        swing = 1 if ((into[0] - c[0]) * nv[0] + (into[1] - c[1]) * nv[1]) >= 0 else -1
        d = self.d

        def leaf(hx, sgn, lw):
            H = (c[0] + dv[0] * hx + nv[0] * swing * t / 2,
                 c[1] + dv[1] * hx + nv[1] * swing * t / 2)
            L = (H[0] + nv[0] * swing * lw, H[1] + nv[1] * swing * lw)
            d.line(H, L, "A-DOOR", lineweight=35)
            a_leaf = math.degrees(math.atan2(nv[1] * swing, nv[0] * swing))
            a_cl = math.degrees(math.atan2(dv[1] * sgn, dv[0] * sgn))
            if round((a_cl - a_leaf) % 360) == 90:
                d.arc(H, lw, a_leaf, a_cl, "A-DOOR")
            else:
                d.arc(H, lw, a_cl, a_leaf, "A-DOOR")

        def draw():
            if leaves == 1:
                if hinge == "a":
                    leaf(-w / 2, 1, w)
                else:
                    leaf(w / 2, -1, w)
            else:
                leaf(-w / 2, 1, w / 2)
                leaf(w / 2, -1, w / 2)
        self.symbols.append(draw)

    def opening(self, c, ang, t, w, side=None):
        self.openings.append(dict(kind="opening", c=c, ang=ang, w=w, t=t,
                                  poly=self._cut(c, ang, w, t)))
        self._edges(side, c, ang, w)
        dv, nv = self._vec(ang)
        d = self.d

        def draw():
            for sgn in (-1, 1):
                a = (c[0] - dv[0] * w / 2 + nv[0] * sgn * t / 2, c[1] - dv[1] * w / 2 + nv[1] * sgn * t / 2)
                b = (c[0] + dv[0] * w / 2 + nv[0] * sgn * t / 2, c[1] + dv[1] * w / 2 + nv[1] * sgn * t / 2)
                d.line(a, b, "A-ABOVE")
        self.symbols.append(draw)

    def window(self, c, ang, w, t=600, side=None):
        self.openings.append(dict(kind="window", c=c, ang=ang, w=w, t=t,
                                  poly=self._cut(c, ang, w, t)))
        self._edges(side, c, ang, w)
        dv, nv = self._vec(ang)
        d = self.d

        def draw():
            for off in (-t / 2, -40, 40, t / 2):
                a = (c[0] - dv[0] * w / 2 + nv[0] * off, c[1] - dv[1] * w / 2 + nv[1] * off)
                b = (c[0] + dv[0] * w / 2 + nv[0] * off, c[1] + dv[1] * w / 2 + nv[1] * off)
                d.line(a, b, "A-WINDOW")
        self.symbols.append(draw)

    # -------------------------------------------------------------- walls
    def build(self, hatch_scale=30.0):
        walls = self.fp.difference(unary_union([r["poly"] for r in self.rooms]))
        if self.cuts:
            walls = walls.difference(unary_union(self.cuts))
        walls = walls.buffer(0).simplify(0.5)
        # drop slivers created by numeric noise
        walls = unary_union([g for g in polys(walls) if g.area > 2000])
        self.walls = walls
        self.d.hatch(walls, "A-WALL-HATCH", "ANSI31", scale=hatch_scale)
        self.d.shape(walls, "A-WALL")
        for draw in self.symbols:
            draw()
        return walls

    # ------------------------------------------------------------- stairs
    def dogleg(self, x0, x1, y_first, n, tread, y_land_end, level="lower", well=200,
               name=""):
        """U-shaped stair, flights running north, half landing at the north end.
        The east flight is the lower one (ground floor -> half landing)."""
        d = self.d
        L = "A-STAIR"
        fw = (x1 - x0 - well) / 2
        xe0, xe1 = x1 - fw, x1          # east flight (up from the lower floor)
        xw0, xw1 = x0, x0 + fw          # west flight (arrives at the upper floor)
        y_top = y_first + n * tread
        land = y_land_end - y_top
        for i in range(n + 1):
            y = y_first + i * tread
            d.line((xe0, y), (xe1, y), L)
            d.line((xw0, y), (xw1, y), L)
        d.rect(xw1, y_first - 100, xe0, y_top + 100, L)         # well / balustrade
        d.rect(xw1 + 50, y_first - 50, xe0 - 50, y_top + 50, L)
        xu, xd = (xe0 + xe1) / 2, (xw0 + xw1) / 2
        ym = y_top + 0.68 * land
        if name:
            d.text(name, ((x0 + x1) / 2, y_top + 0.27 * land), 150, "A-TEXT-ROOM", "MC",
                   style="ARIALBD")
        if level == "lower":
            d.pl([(xu, y_first - 350), (xu, ym), (xd, ym), (xd, y_first + 2.5 * tread)], L)
            self._arrow((xd, y_first + 2.5 * tread), 270)
            d.text("UP", (xu, y_first - 600), 160, "A-TEXT", "MC")
            yb = y_first + 6.5 * tread                      # break line on the up flight
            d.pl([(xe0 - 60, yb - 220), (xu - 120, yb - 40), (xu - 40, yb + 140),
                  (xu + 40, yb - 140), (xu + 120, yb + 40), (xe1 + 60, yb + 220)], L)
        else:
            d.pl([(xd, y_first - 350), (xd, ym), (xu, ym), (xu, y_first + 2.5 * tread)], L)
            self._arrow((xu, y_first + 2.5 * tread), 270)
            d.text("DN", (xd, y_first - 600), 160, "A-TEXT", "MC")

    def _arrow(self, tip, ang, size=260):
        d = self.d
        a = math.radians(ang)
        for da in (150, -150):
            b = a + math.radians(da)
            d.line(tip, (tip[0] + size * math.cos(b), tip[1] + size * math.sin(b)), "A-STAIR")

    # ---------------------------------------------------------------- grid
    def grid(self, gx, gy, x_ext, y_ext, r=420, labels_x=None, labels_y=None):
        d = self.d
        labels_x = labels_x or [str(i + 1) for i in range(len(gx))]
        labels_y = labels_y or [chr(65 + i) for i in range(len(gy))]
        for x, lab in zip(gx, labels_x):
            d.line((x, y_ext[0]), (x, y_ext[1]), "A-GRID")
            for y, sgn in ((y_ext[0], -1), (y_ext[1], 1)):
                d.circle((x, y + sgn * r), r, "A-GRID", linetype="Continuous")
                d.text(lab, (x, y + sgn * r), 300, "A-GRID", "MC", style="ARIALBD")
        for y, lab in zip(gy, labels_y):
            d.line((x_ext[0], y), (x_ext[1], y), "A-GRID")
            for x, sgn in ((x_ext[0], -1), (x_ext[1], 1)):
                d.circle((x + sgn * r, y), r, "A-GRID", linetype="Continuous")
                d.text(lab, (x + sgn * r, y), 300, "A-GRID", "MC", style="ARIALBD")


def rect(x0, y0, x1, y1):
    return box(x0, y0, x1, y1)

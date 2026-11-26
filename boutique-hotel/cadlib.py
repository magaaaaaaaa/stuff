"""Small drawing helpers on top of ezdxf + shapely (units: millimetres)."""
import math

import ezdxf
from ezdxf import const, units
from ezdxf.enums import TextEntityAlignment as TA
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

ALIGN = {
    "MC": TA.MIDDLE_CENTER, "ML": TA.MIDDLE_LEFT, "MR": TA.MIDDLE_RIGHT,
    "BL": TA.LEFT, "BC": TA.CENTER, "BR": TA.RIGHT,
    "TL": TA.TOP_LEFT, "TC": TA.TOP_CENTER, "TR": TA.TOP_RIGHT,
}

# name, ACI colour, linetype, lineweight (1/100 mm)
LAYERS = [
    ("A-WALL", 7, "Continuous", 50),
    ("A-WALL-HATCH", 8, "Continuous", 9),
    ("A-DOOR", 30, "Continuous", 25),
    ("A-WINDOW", 5, "Continuous", 18),
    ("A-DIMS", 1, "Continuous", 13),
    ("A-TEXT", 7, "Continuous", 18),
    ("A-TEXT-ROOM", 7, "Continuous", 18),
    ("A-GRID", 8, "HCENTER", 9),
    ("A-STAIR", 34, "Continuous", 18),
    ("A-FURNITURE", 8, "Continuous", 9),
    ("A-SANITARY", 150, "Continuous", 13),
    ("A-POOL", 140, "Continuous", 25),
    ("A-FLOOR-HATCH", 254, "Continuous", 5),
    ("A-BALCONY", 34, "Continuous", 25),
    ("A-BELOW", 8, "HDASH", 13),
    ("A-ABOVE", 8, "HDASH", 13),
    ("S-FOOTING", 5, "Continuous", 25),
    ("S-FOOTING-HATCH", 8, "Continuous", 5),
    ("S-FWALL", 7, "Continuous", 50),
    ("S-FWALL-HATCH", 8, "Continuous", 9),
    ("S-TEXT", 7, "Continuous", 18),
    ("S-DETAIL", 7, "Continuous", 25),
    ("L-BOUNDARY", 1, "HDASHDOT", 50),
    ("L-ZONE", 6, "HDASH", 18),
    ("L-EXISTING", 8, "Continuous", 25),
    ("L-BUILDING", 7, "Continuous", 50),
    ("L-BUILDING-HATCH", 8, "Continuous", 5),
    ("L-ROAD", 7, "Continuous", 25),
    ("L-PAVING", 34, "Continuous", 13),
    ("L-PAVING-HATCH", 254, "Continuous", 5),
    ("L-PLANT", 94, "Continuous", 13),
    ("L-TEXT", 7, "Continuous", 18),
    ("L-DIMS", 1, "Continuous", 13),
    ("T-FRAME", 7, "Continuous", 50),
    ("T-TITLE", 7, "Continuous", 18),
    ("T-TEXT", 7, "Continuous", 18),
    ("T-VIEWPORT", 8, "Continuous", 0),
]


def new_doc():
    doc = ezdxf.new("R2013", setup=True)
    doc.units = units.MM
    doc.header["$MEASUREMENT"] = 1
    doc.header["$INSUNITS"] = 4
    doc.header["$LUNITS"] = 2
    doc.header["$LUPREC"] = 0
    doc.header["$LTSCALE"] = 300.0
    doc.header["$PSLTSCALE"] = 0
    doc.header["$LWDISPLAY"] = 1
    doc.linetypes.add("HDASH", pattern=[0.75, 0.5, -0.25], description="Dashed __ __ __")
    doc.linetypes.add("HCENTER", pattern=[2.0, 1.25, -0.25, 0.25, -0.25],
                      description="Center ____ _ ____ _")
    doc.linetypes.add("HDASHDOT", pattern=[1.4, 1.0, -0.2, 0.0, -0.2],
                      description="Dash dot __ . __ .")
    doc.styles.add("ARIAL", font="arial.ttf")
    doc.styles.add("ARIALBD", font="arialbd.ttf")
    for name, color, lt, lw in LAYERS:
        doc.layers.add(name, color=color, linetype=lt, lineweight=lw)
    doc.layers.get("T-VIEWPORT").dxf.plot = 0
    for name, scale in (("A100", 100), ("A200", 200), ("A25", 25)):
        ds = doc.dimstyles.new(name)
        ds.dxf.dimscale = scale
        ds.dxf.dimtxt = 2.0
        ds.dxf.dimtxsty = "ARIAL"
        ds.dxf.dimasz = 1.2
        ds.dxf.dimtsz = 0.9        # oblique (architectural) ticks
        ds.dxf.dimexe = 1.0
        ds.dxf.dimexo = 1.0
        ds.dxf.dimdle = 0.8
        ds.dxf.dimgap = 0.5
        ds.dxf.dimtad = 1
        ds.dxf.dimtih = 0
        ds.dxf.dimtoh = 0
        ds.dxf.dimdec = 0
        ds.dxf.dimzin = 8
        ds.dxf.dimlunit = 2
        ds.dxf.dimclrd = 256
        ds.dxf.dimclre = 256
        ds.dxf.dimclrt = 256
    return doc


def polys(geom):
    """Yield every Polygon contained in a shapely geometry."""
    if geom is None or geom.is_empty:
        return
    if isinstance(geom, Polygon):
        yield geom
    elif hasattr(geom, "geoms"):
        for g in geom.geoms:
            yield from polys(g)


def dehole(poly):
    """Split a polygon with holes into hole-free pieces (robust hatch boundaries)."""
    if not poly.interiors:
        yield poly
        return
    from shapely.geometry import box as _box
    minx, miny, maxx, maxy = poly.bounds
    cx = poly.interiors[0].centroid.x
    for half in (_box(minx - 1, miny - 1, cx, maxy + 1), _box(cx, miny - 1, maxx + 1, maxy + 1)):
        for g in polys(poly.intersection(half)):
            if g.area > 1:
                yield from dehole(g)


def frame(pt, rot):
    """Local frame: d = depth away from the wall (direction rot), a = across."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def f(a, d):
        return (pt[0] + d * c - a * s, pt[1] + d * s + a * c)
    return f


class Dwg:
    """Drawing context: model space + origin offset."""

    def __init__(self, msp, ox=0.0, oy=0.0, dimstyle="A100", ltscale=1.0,
                 dim_layer="A-DIMS"):
        self.msp, self.ox, self.oy = msp, ox, oy
        self.dimstyle, self.lts, self.dim_layer = dimstyle, ltscale, dim_layer

    def p(self, pt):
        return (pt[0] + self.ox, pt[1] + self.oy)

    def _a(self, layer, kw):
        a = {"layer": layer}
        if self.lts != 1.0:
            a["ltscale"] = self.lts
        a.update(kw)
        return a

    def line(self, a, b, layer, **kw):
        return self.msp.add_line(self.p(a), self.p(b), dxfattribs=self._a(layer, kw))

    def pl(self, pts, layer, close=False, **kw):
        return self.msp.add_lwpolyline([self.p(q) for q in pts], close=close,
                                       dxfattribs=self._a(layer, kw))

    def plb(self, pts, layer, close=False, **kw):
        """Polyline with bulges: pts = [(x, y, bulge), ...]."""
        data = [(q[0] + self.ox, q[1] + self.oy, q[2]) for q in pts]
        return self.msp.add_lwpolyline(data, format="xyb", close=close,
                                       dxfattribs=self._a(layer, kw))

    def rect(self, x0, y0, x1, y1, layer, **kw):
        return self.pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, close=True, **kw)

    def circle(self, c, r, layer, **kw):
        return self.msp.add_circle(self.p(c), r, dxfattribs=self._a(layer, kw))

    def arc(self, c, r, a0, a1, layer, **kw):
        return self.msp.add_arc(self.p(c), r, a0, a1, dxfattribs=self._a(layer, kw))

    def ellipse(self, c, major, ratio, layer, **kw):
        return self.msp.add_ellipse(self.p(c), major_axis=(major[0], major[1], 0),
                                    ratio=ratio, dxfattribs=self._a(layer, kw))

    def text(self, s, pos, h, layer="A-TEXT", align="MC", rot=0, style="ARIAL"):
        t = self.msp.add_text(s, height=h, rotation=rot,
                              dxfattribs={"layer": layer, "style": style})
        t.set_placement(self.p(pos), align=ALIGN[align])
        return t

    def label(self, lines, pos, layer="A-TEXT-ROOM"):
        """lines = [(text, height, style)], vertically centred block at pos."""
        total = sum(h * 1.55 for _, h, _ in lines)
        y = pos[1] + total / 2
        for s, h, st in lines:
            y -= h * 1.55 / 2
            self.text(s, (pos[0], y), h, layer, "MC", style=st)
            y -= h * 1.55 / 2

    def shape(self, geom, layer, **kw):
        for g in polys(geom):
            self.pl(list(g.exterior.coords)[:-1], layer, close=True, **kw)
            for r in g.interiors:
                self.pl(list(r.coords)[:-1], layer, close=True, **kw)

    def hatch(self, geom, layer, pattern="ANSI31", scale=40.0, angle=0.0,
              solid=False, rgb=None):
        for g in (q for g0 in polys(geom) for q in dehole(g0)):
            h = self.msp.add_hatch(dxfattribs={"layer": layer})
            if solid:
                h.set_solid_fill()
                if rgb is not None:
                    h.rgb = rgb
            else:
                h.set_pattern_fill(pattern, scale=scale, angle=angle)
            h.paths.add_polyline_path([self.p(q) for q in list(g.exterior.coords)[:-1]],
                                      is_closed=True, flags=const.BOUNDARY_PATH_EXTERNAL)
            for r in g.interiors:
                h.paths.add_polyline_path([self.p(q) for q in list(r.coords)[:-1]],
                                          is_closed=True, flags=const.BOUNDARY_PATH_DEFAULT)

    # --- dimensions -------------------------------------------------------
    def dim_h(self, x0, x1, y_line, y_pts=None, text=None):
        y_pts = y_line if y_pts is None else y_pts
        d = self.msp.add_linear_dim(base=self.p((x0, y_line)), p1=self.p((x0, y_pts)),
                                    p2=self.p((x1, y_pts)), angle=0,
                                    dimstyle=self.dimstyle, text=text or "<>",
                                    dxfattribs={"layer": self.dim_layer})
        d.render()

    def dim_v(self, y0, y1, x_line, x_pts=None, text=None):
        x_pts = x_line if x_pts is None else x_pts
        d = self.msp.add_linear_dim(base=self.p((x_line, y0)), p1=self.p((x_pts, y0)),
                                    p2=self.p((x_pts, y1)), angle=90,
                                    dimstyle=self.dimstyle, text=text or "<>",
                                    dxfattribs={"layer": self.dim_layer})
        d.render()

    def dim_al(self, p1, p2, dist, text=None):
        d = self.msp.add_aligned_dim(p1=self.p(p1), p2=self.p(p2), distance=dist,
                                     dimstyle=self.dimstyle, text=text or "<>",
                                     dxfattribs={"layer": self.dim_layer})
        d.render()

    def chain_h(self, xs, y_line, y_pts=None):
        xs = sorted(set(round(v, 1) for v in xs))
        for a, b in zip(xs, xs[1:]):
            if b - a > 1:
                self.dim_h(a, b, y_line, y_pts)

    def chain_v(self, ys, x_line, x_pts=None):
        ys = sorted(set(round(v, 1) for v in ys))
        for a, b in zip(ys, ys[1:]):
            if b - a > 1:
                self.dim_v(a, b, x_line, x_pts)

    # --- furniture / sanitary symbols -------------------------------------
    def _lrect(self, f, a0, d0, a1, d1, layer):
        self.pl([f(a0, d0), f(a1, d0), f(a1, d1), f(a0, d1)], layer, close=True)

    def wc(self, pt, rot, layer="A-SANITARY"):
        f = frame(pt, rot)
        self._lrect(f, -200, 0, 200, 180, layer)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        self.ellipse(f(0, 430), (250 * c, 250 * s), 185 / 250, layer)

    def basin(self, pt, rot, layer="A-SANITARY"):
        f = frame(pt, rot)
        self._lrect(f, -260, 0, 260, 430, layer)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        self.ellipse(f(0, 235), (-190 * s, 190 * c), 140 / 190, layer)
        self.circle(f(0, 65), 25, layer)

    def shower(self, x0, y0, x1, y1, layer="A-SANITARY"):
        self.rect(x0, y0, x1, y1, layer)
        self.line((x0, y0), (x1, y1), layer)
        self.line((x0, y1), (x1, y0), layer)
        self.circle(((x0 + x1) / 2, (y0 + y1) / 2), 50, layer)

    def tub(self, x0, y0, x1, y1, layer="A-SANITARY"):
        self.rect(x0, y0, x1, y1, layer)
        r = 180
        a, b, c, d = x0 + 70, y0 + 70, x1 - 70, y1 - 70
        k = math.tan(math.pi / 8)
        self.plb([(a + r, b, 0), (c - r, b, k), (c, b + r, 0), (c, d - r, k),
                  (c - r, d, 0), (a + r, d, k), (a, d - r, 0), (a, b + r, k)],
                 layer, close=True)
        self.circle((a + 220 if (x1 - x0) > (y1 - y0) else (a + c) / 2,
                     (b + d) / 2 if (x1 - x0) > (y1 - y0) else b + 220), 35, layer)

    def bed(self, pt, rot, w=1600, l=2000, tables=(True, True), layer="A-FURNITURE"):
        f = frame(pt, rot)
        self._lrect(f, -w / 2, 0, w / 2, l, layer)
        if w >= 1400:
            self._lrect(f, -w / 2 + 90, 90, -50, 430, layer)
            self._lrect(f, 50, 90, w / 2 - 90, 430, layer)
        else:
            self._lrect(f, -w / 2 + 110, 90, w / 2 - 110, 430, layer)
        self.line(f(-w / 2, 680), f(w / 2, 680), layer)
        if tables[0]:
            self._lrect(f, -w / 2 - 480, 0, -w / 2 - 40, 420, layer)
        if tables[1]:
            self._lrect(f, w / 2 + 40, 0, w / 2 + 480, 420, layer)

    def wardrobe(self, x0, y0, x1, y1, layer="A-FURNITURE"):
        self.rect(x0, y0, x1, y1, layer)
        self.line((x0, y0), (x1, y1), layer)
        if (x1 - x0) > (y1 - y0):
            self.line((x0 + 60, (y0 + y1) / 2), (x1 - 60, (y0 + y1) / 2), layer)
        else:
            self.line(((x0 + x1) / 2, y0 + 60), ((x0 + x1) / 2, y1 - 60), layer)

    def desk(self, x0, y0, x1, y1, chair, layer="A-FURNITURE"):
        self.rect(x0, y0, x1, y1, layer)
        self.circle(chair, 220, layer)

    def table4(self, c, s=800, layer="A-FURNITURE", chairs="NSEW"):
        x, y = c
        self.rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2, layer)
        g, k = 70, 190
        if "N" in chairs:
            self.rect(x - k, y + s / 2 + g, x + k, y + s / 2 + g + 2 * k, layer)
        if "S" in chairs:
            self.rect(x - k, y - s / 2 - g - 2 * k, x + k, y - s / 2 - g, layer)
        if "E" in chairs:
            self.rect(x + s / 2 + g, y - k, x + s / 2 + g + 2 * k, y + k, layer)
        if "W" in chairs:
            self.rect(x - s / 2 - g - 2 * k, y - k, x - s / 2 - g, y + k, layer)

    def round_table(self, c, r=450, n=4, layer="A-FURNITURE", a0=45):
        self.circle(c, r, layer)
        for i in range(n):
            a = math.radians(a0 + i * 360 / n)
            self.circle((c[0] + (r + 290) * math.cos(a), c[1] + (r + 290) * math.sin(a)),
                        200, layer)

    def sofa(self, pt, rot, w=1800, d=850, layer="A-FURNITURE"):
        f = frame(pt, rot)
        self._lrect(f, -w / 2, 0, w / 2, d, layer)
        self._lrect(f, -w / 2 + 150, 180, w / 2 - 150, d, layer)

    def lounger(self, pt, rot, layer="A-FURNITURE"):
        f = frame(pt, rot)
        self._lrect(f, -325, 0, 325, 1900, layer)
        self.line(f(-325, 550), f(325, 550), layer)

    def tree(self, c, r, layer="L-PLANT", spokes=8):
        self.circle(c, r, layer)
        self.circle(c, r * 0.12, layer)
        for i in range(spokes):
            a = math.radians(i * 360 / spokes + 11)
            self.line((c[0] + r * 0.25 * math.cos(a), c[1] + r * 0.25 * math.sin(a)),
                      (c[0] + r * 0.85 * math.cos(a), c[1] + r * 0.85 * math.sin(a)), layer)


__all__ = ["new_doc", "Dwg", "polys", "frame", "unary_union", "MultiPolygon", "Polygon"]

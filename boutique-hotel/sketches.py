#!/usr/bin/env python3
"""Preliminary concept sketches (hand-sketch style) for the report: output/sketches/*.png"""
import logging
import math
import os
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

warnings.filterwarnings("ignore")
logging.getLogger("matplotlib").setLevel(logging.ERROR)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output", "sketches")
INK, RED, BLUE, GREEN, SAND = "#222222", "#b03a2e", "#1f5fa8", "#2e7d32", "#f3ead6"


def arrow(ax, a, b, color=INK, lw=2.0, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=18, lw=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}"))


def note(ax, xy, text, color=INK, size=10, ha="left", **kw):
    ax.text(xy[0], xy[1], text, color=color, fontsize=size, ha=ha, va="center", **kw)


def site_frame(ax):
    ax.add_patch(Rectangle((0, 0), 40, 60, fill=False, lw=2.2, ec=INK))
    ax.add_patch(Rectangle((0, 0), 40, 30, fc=SAND, ec=INK, lw=1.2, ls="--"))
    ax.add_patch(Rectangle((8.6, 46), 7.4, 11, fill=False, hatch="//", ec=INK, lw=1.4))
    ax.add_patch(Polygon([(18, 51.5), (19, 57), (22.5, 57.6), (26, 56.6), (26.6, 52.5), (24.5, 50.4),
                          (20.5, 50.2)], fill=False, ec=GREEN, lw=1.4))
    ax.add_patch(Rectangle((32, 53), 7.5, 5, fill=False, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((1, 46.5), 3, 3, fill=False, ec=INK, lw=1.2))
    for c in ((25, 48), (30, 50), (36, 50), (28, 45), (33, 46), (30, 43), (35, 42), (9, 39), (14, 40),
              (20, 40), (4, 37), (12, 36), (25, 36), (33, 37)):
        ax.add_patch(Circle(c, 1.2, fill=False, ec=GREEN, lw=1.0))


def sketch_site():
    fig, ax = plt.subplots(figsize=(8.2, 9.6))
    site_frame(ax)
    note(ax, (12.3, 51.5), "existing\nhouse", size=9, ha="center")
    note(ax, (22.4, 54), "garden", GREEN, 9, ha="center")
    note(ax, (35.7, 55.5), "terrace", size=9, ha="center")
    note(ax, (20, 15), "40 x 30 m\nhotel zone", size=13, ha="center")
    # gate + access
    ax.plot([4.5, 8], [60, 60], color=RED, lw=5)
    note(ax, (6.2, 62.2), "existing gate", RED, 10, ha="center")
    arrow(ax, (6.2, 59), (6.2, 41), RED, 2.4)
    arrow(ax, (6.2, 41), (27, 33), RED, 2.4, rad=0.25)
    note(ax, (13, 43.3), "new driveway ?", RED, 10)
    # sun path
    xs = [20 + 30 * math.cos(math.radians(a)) for a in range(-20, 201, 5)]
    ys = [16 - 26 * math.sin(math.radians(a)) for a in range(-20, 201, 5)]
    ax.plot(xs, ys, color="#e39b00", lw=2, ls="--")
    for a, lab in ((-12, "sunrise\n(E)"), (90, "noon sun (S)"), (192, "sunset\n(W)")):
        x, y = 20 + 30 * math.cos(math.radians(a)), 16 - 26 * math.sin(math.radians(a))
        ax.add_patch(Circle((x, y), 1.6, fc="#ffd24d", ec="#e39b00", lw=1.5))
        note(ax, (x + (2.4 if a < 90 else -2.4 if a > 90 else 0), y - (3.2 if a == 90 else 0)), lab,
             "#a86f00", 10, ha="left" if a < 90 else "right" if a > 90 else "center")
    arrow(ax, (47.5, 17.5), (40.6, 12), "#e39b00", 2)
    note(ax, (42.5, 7.5), "morning sun\n-> restaurant\n   on this side", "#a86f00", 10)
    # wind
    for dy in (0, 5, 10):
        arrow(ax, (-11, -7 + dy), (-1.5, 1.5 + dy), BLUE, 2.4)
    note(ax, (-13.5, -9.5), "cold SW winter wind", BLUE, 11)
    note(ax, (1, 3), "block the wind\nwith the building", BLUE, 10)
    # north arrow
    arrow(ax, (47, 52), (47, 60), INK, 2.5)
    note(ax, (47, 61.8), "N", size=14, ha="center")
    note(ax, (20, 31.5), "keep distance + trees towards the house (privacy)", GREEN, 9, ha="center")
    ax.set_title("Sketch 1 - site reading: sun, wind, access", fontsize=14, loc="left")
    ax.set_xlim(-16, 54)
    ax.set_ylim(-17, 66)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(os.path.join(OUT, "sketch1_site.png"), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def sketch_options():
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6))
    opts = [
        ("A  bar in the middle", [[(6, 10), (34, 10), (34, 20), (6, 20)]],
         ["+ simple, cheap", "- repeated rooms", "- leftover strips,", "  no sheltered place"], False),
        ("B  U around a court", [[(4, 4), (36, 4), (36, 26), (27, 26), (27, 12), (13, 12), (13, 26), (4, 26)]],
         ["+ protected court", "- court faces north:", "  shade + snow drifts", "- footprint > 600 m2"], False),
        ("C  L in the SW corner", [[(3, 3), (33, 3), (33, 14.4), (22.8, 14.4), (14.4, 22.8), (14.4, 27), (3, 27)]],
         ["+ blocks SW wind", "+ court opens to E sun", "+ rooms on S / W / E", "+ garden + parking left"], True),
    ]
    for ax, (title, polys, notes, chosen) in zip(axes, opts):
        ax.add_patch(Rectangle((0, 0), 40, 30, fc=SAND, ec=INK, lw=1.6, ls="--"))
        for p in polys:
            ax.add_patch(Polygon(p, fc="#d9d9d9" if not chosen else "#c9dcc0", ec=INK, lw=2.2))
        if chosen:
            arrow(ax, (29, 27), (21.5, 19.5), RED, 2.4)
            note(ax, (33, 28), "entrance", RED, 10, ha="center")
            for dy in (0, 5):
                arrow(ax, (-6, -5 + dy), (1.5, 1.5 + dy), BLUE, 2)
            ax.add_patch(Circle((28, 21), 2.4, fill=False, ec=GREEN, lw=1.6))
            note(ax, (34.8, 17.6), "court", GREEN, 10, ha="center")
            ax.add_patch(Rectangle((-2.5, -2.5), 45, 35, fill=False, ec=RED, lw=3))
            note(ax, (20, 35.5), "CHOSEN", RED, 13, ha="center")
        ax.set_title(title, fontsize=13, loc="left")
        for i, t in enumerate(notes):
            note(ax, (0, -5 - i * 3.3), t, GREEN if t.startswith("+") else RED if t.startswith("-") else INK, 10.5)
        ax.set_xlim(-8, 46)
        ax.set_ylim(-19, 40)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Sketch 2 - three massing options inside the 40 x 30 m zone (north is up)", fontsize=14,
                 x=0.02, ha="left")
    fig.savefig(os.path.join(OUT, "sketch2_options.png"), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def bubble(ax, c, r, text, fc):
    ax.add_patch(Circle(c, r, fc=fc, ec=INK, lw=1.8))
    ax.text(c[0], c[1], text, ha="center", va="center", fontsize=9.5)


def link(ax, a, b, lw=2.0, ls="-"):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=INK, lw=lw, ls=ls, zorder=0)


def sketch_bubbles():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.6))
    pub, prv, srv, wel = "#fbe3b5", "#cfe3f5", "#e3e3e3", "#cdebd5"
    B = {"ent": ((6.9, 7.0), 0.8, "entrance\n+ vestibule", "#f6c1b8"), "rec": ((5.2, 5.2), 1.15, "RECEPTION\nlobby", pub),
         "rest": ((8.2, 2.6), 1.25, "RESTAURANT\n(E + S sun)", pub), "kit": ((9.3, 4.9), 0.85, "kitchen", srv),
         "wc": ((5.6, 3.2), 0.6, "public\nWC", srv), "rooms1": ((5.4, 1.3), 0.95, "rooms\n101-102", prv),
         "st": ((3.4, 5.6), 0.6, "stair", srv), "pool": ((2.0, 1.9), 1.45, "POOL HALL\nhot tub", wel),
         "spa": ((2.0, 4.2), 0.9, "sauna\nchanging", wel), "rooms2": ((1.3, 6.6), 0.95, "rooms\n103-104", prv),
         "staff": ((3.5, 7.7), 0.75, "staff\nroom", srv)}
    for k, (c, r, t, fc) in B.items():
        bubble(a1, c, r, t, fc)
    for u, v in (("ent", "rec"), ("rec", "rest"), ("rest", "kit"), ("rec", "wc"), ("rec", "rooms1"),
                 ("rec", "st"), ("st", "spa"), ("spa", "pool"), ("st", "rooms2"), ("st", "staff")):
        link(a1, B[u][0], B[v][0])
    link(a1, B["kit"][0], (10.6, 6.3), ls="--")
    a1.text(10.6, 6.6, "service\ndoor", ha="center", fontsize=9)
    arrow(a1, (8.9, 8.4), (7.6, 7.5), RED, 2.2)
    a1.text(9.0, 8.4, "guests arrive\nfrom the court", color=RED, fontsize=10)
    a1.set_title("First floor - who needs to be next to whom", fontsize=13, loc="left")
    C = {"st": ((3.7, 6.0), 0.6, "stair 1", srv), "node": ((5.3, 4.5), 0.9, "lounge\nnode", pub),
         "west": ((1.6, 5.6), 1.3, "west rooms\n204-207", prv), "south": ((7.2, 1.6), 1.45, "south rooms\n201-203", prv),
         "d1": ((9.6, 2.9), 0.95, "DELUXE\nSE corner", "#b7d3ee"), "d2": ((6.6, 6.2), 1.0, "DELUXE\ncourt view", "#b7d3ee"),
         "r8": ((8.6, 5.0), 0.8, "room\n208", prv), "bal": ((1.9, 1.9), 1.35, "PUBLIC\nBALCONY\n(pool roof)", wel),
         "sto": ((3.9, 3.3), 0.62, "storage", srv), "st2": ((10.4, 4.6), 0.55, "stair 2", srv)}
    for k, (c, r, t, fc) in C.items():
        bubble(a2, c, r, t, fc)
    for u, v in (("st", "node"), ("node", "west"), ("node", "south"), ("node", "d2"), ("node", "bal"),
                 ("node", "sto"), ("south", "d1"), ("node", "r8"), ("r8", "st2"), ("west", "bal")):
        link(a2, C[u][0], C[v][0])
    a2.text(0.3, 8.3, "every room different:\nposition, shape, view", color=RED, fontsize=10.5)
    a2.set_title("Second floor - rooms around two corridors", fontsize=13, loc="left")
    for ax in (a1, a2):
        ax.set_xlim(-0.2, 11.6)
        ax.set_ylim(-0.3, 9.3)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Sketch 3 - bubble diagrams of the functional layout", fontsize=14, x=0.02, ha="left")
    fig.savefig(os.path.join(OUT, "sketch3_bubbles.png"), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    with plt.xkcd(scale=0.9, length=110, randomness=2.2):
        plt.rcParams["font.family"] = ["DejaVu Sans"]
        plt.rcParams["path.effects"] = []
        sketch_site()
        sketch_options()
        sketch_bubbles()
    print("sketches written to", OUT)


if __name__ == "__main__":
    main()

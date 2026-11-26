#!/usr/bin/env python3
"""Crop the rendered sheets into report figures: output/report_figures/*.png + figures.json"""
import json
import os

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
FIG = os.path.join(OUT, "report_figures")
CROPS = {
    "site": ("A-01_SITE_PLAN", (0.125, 0.06, 0.675, 0.95)),
    "gf": ("A-02_FIRST_FLOOR", (0.03, 0.055, 0.74, 0.93)),
    "ff": ("A-03_SECOND_FLOOR", (0.03, 0.055, 0.74, 0.93)),
    "fnd": ("S-01_FOUNDATION", (0.03, 0.055, 0.74, 0.93)),
    "fnd_detail": ("S-01_FOUNDATION", (0.765, 0.27, 0.995, 0.70)),
    "el_n": ("A-04_ELEVATIONS_N-S", (0.03, 0.15, 0.74, 0.455)),
    "el_s": ("A-04_ELEVATIONS_N-S", (0.03, 0.545, 0.74, 0.85)),
    "el_w": ("A-05_ELEVATIONS_E-W_SECTION", (0.09, 0.03, 0.68, 0.33)),
    "el_e": ("A-05_ELEVATIONS_E-W_SECTION", (0.09, 0.325, 0.68, 0.62)),
    "sec": ("A-05_ELEVATIONS_E-W_SECTION", (0.09, 0.61, 0.68, 0.975)),
}


def main():
    os.makedirs(FIG, exist_ok=True)
    meta = {}
    for key, (sheet, (a, b, c, e)) in CROPS.items():
        im = Image.open(os.path.join(OUT, sheet + ".png")).convert("RGB")
        w, h = im.size
        cr = im.crop((int(a * w), int(b * h), int(c * w), int(e * h)))
        path = os.path.join(FIG, key + ".png")
        cr.save(path, optimize=True)
        meta[key] = {"path": path, "w": cr.size[0], "h": cr.size[1]}
    for n in ("sketch1_site", "sketch2_options", "sketch3_bubbles"):
        path = os.path.join(OUT, "sketches", n + ".png")
        im = Image.open(path)
        meta[n] = {"path": path, "w": im.size[0], "h": im.size[1]}
    with open(os.path.join(FIG, "figures.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("figures:", ", ".join(meta))


if __name__ == "__main__":
    main()

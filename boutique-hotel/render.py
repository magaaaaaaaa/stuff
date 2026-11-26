#!/usr/bin/env python3
"""Render every paper-space sheet of the DXF to PDF (true A2 size) and PNG previews."""
import os
import sys

import ezdxf
import pymupdf
from ezdxf.addons.drawing import Frontend, RenderContext, config, layout
from ezdxf.addons.drawing import pymupdf as ezmu

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")


def main(dpi=150):
    doc = ezdxf.readfile(os.path.join(OUT, "AUL_Boutique_Hotel.dxf"))
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.COLOR,
        lineweight_scaling=0.8,
    )
    merged = pymupdf.open()
    for name in doc.layouts.names_in_taborder():
        if name == "Model":
            continue
        lay = doc.layouts.get(name)
        ctx = RenderContext(doc)
        be = ezmu.PyMuPdfBackend()
        Frontend(ctx, be, config=cfg).draw_layout(lay, finalize=True)
        page = layout.Page(594, 420, layout.Units.mm, margins=layout.Margins.all(0))
        st = layout.Settings(fit_page=True)
        slug = name.replace(" ", "_")
        pdf = be.get_pdf_bytes(page, settings=st)
        with open(os.path.join(OUT, slug + ".pdf"), "wb") as f:
            f.write(pdf)
        with open(os.path.join(OUT, slug + ".png"), "wb") as f:
            f.write(be.get_pixmap_bytes(page, fmt="png", settings=st, dpi=dpi))
        merged.insert_pdf(pymupdf.open(stream=pdf, filetype="pdf"))
        print("rendered", name)
    merged.save(os.path.join(OUT, "AUL_Boutique_Hotel_all_sheets.pdf"))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 150)

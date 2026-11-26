#!/bin/sh
# Rebuild everything: DXF -> sheet PDFs/PNGs -> sketches -> report figures -> report (docx + pdf)
set -e
cd "$(dirname "$0")"
python3 build.py
python3 render.py 220
python3 sketches.py
python3 report_figures.py
node make_report.js
cd output
soffice --headless --convert-to pdf AUL_Boutique_Hotel_Report.docx >/dev/null 2>&1 || echo "PDF export of the report needs LibreOffice (or export from Word)"

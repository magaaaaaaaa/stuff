# AUL Boutique Hotel — CEE 204 individual project drawings

Two-storey boutique hotel on the 40 × 60 m plot in Astana (hotel zone = southern 40 × 30 m).

## What is in `output/`

| File | Content |
|---|---|
| `AUL_Boutique_Hotel.dxf` | The CAD file: all drawings in model space + six A2 layouts with title blocks |
| `AUL_Boutique_Hotel_all_sheets.pdf` | The six sheets in one PDF (true A2 size) |
| `A-01_SITE_PLAN` .pdf / .png | Site plan, 1:200 |
| `A-02_FIRST_FLOOR` .pdf / .png | First-floor plan, 1:100 |
| `A-03_SECOND_FLOOR` .pdf / .png | Second-floor plan, 1:100 |
| `A-04_ELEVATIONS_N-S` .pdf / .png | North (front) and south elevations, 1:100 |
| `A-05_ELEVATIONS_E-W_SECTION` .pdf / .png | East and west (side) elevations and section A-A, 1:100 |
| `S-01_FOUNDATION` .pdf / .png | Foundation plan, 1:100 + strip-footing detail, 1:25 |
| `AUL_Boutique_Hotel_Report.docx` / `.pdf` | The project report (all ten sections of the manual) |
| `sketches/` | Three preliminary concept sketches used in the report |
| `report_figures/` | The drawing crops used as figures in the report |
| `room_schedule.md`, `rooms.json` | Room areas against the manual's limits |

## Before submitting

1. Open `AUL_Boutique_Hotel.dxf` in AutoCAD and **Save As → AutoCAD Drawing (.dwg)**. The manual asks for a DWG.
2. Replace `STUDENT NAME` and `ID ________` in the title block of each of the six layout tabs
   (or change `STUDENT`, `STUDENT_ID`, `DATE` at the top of `build.py` and run `./make_all.sh`).
3. Look through every layout tab once. The file was generated with a script and checked by rendering it,
   but it has **not** been opened in AutoCAD itself.
4. In the report (`.docx`), fill in everything highlighted in yellow:
   - student name, student ID and submission date on the title page;
   - section 2.2 **Location**: coordinates, map screenshot and the reason for the choice (the manual requires this
     in the designer notes; use the location submitted on 30 October);
   - references [6]–[8]: the Kazakh code numbers and titles were written from memory — check each one and
     delete any that were not actually consulted.
5. The preliminary sketches in section 3 were made for this design. If different sketches were handed in on
   30 October, replace them with those (the manual allows only minor changes between the two submissions).
6. Read the designer notes and put them into your own words, then export the report from Word as PDF.

## The design in short

- **Concept — "aul".** An L-shaped building wrapped around an arrival court, with a diagonal entrance
  facade at the inner corner and a "shanyrak" circle in the plaza paving and as a rooflight.
- **Placement at the edge.** The L sits 3.0 m from the west and south boundaries. Its two wings shield the
  court from the south-west and leave it open to the east.
- **Access.** Existing north gates → new 3.5 m driveway → drop-off aisle, 5 parking bays (1 accessible) →
  plaza → steps and a 1:12 ramp → vestibule.
- **First floor.** Reception at the corner; restaurant (east + south windows, east terrace) and kitchen in
  the east; indoor pool hall with hot tub, sauna and changing rooms in the south-west; four guest rooms
  (102 is the accessible one); staff room; two public WCs (one accessible); two stairs.
- **Second floor.** Eight standard and two deluxe rooms, storage, lounge node, and the public balcony on
  the pool-hall roof, reached from both corridors.
- **Every room is different.** No two rooms share size, shape, orientation and bathroom position:
  south, west, north-court and corner rooms, two L-shaped rooms, and a deluxe room with the diagonal
  glazed wall.
- **Elevations and section.** Two-storey wings with parapet at +7.200 m, single-storey pool hall with the
  balcony on its roof; section A-A is an offset section through the pool and stair 1.
- **Foundation.** Continuous RC strip footings under the load-bearing walls (1200 mm under exterior,
  800 mm under interior), underside at −2.300 m, plus an RC pool basin.

## Checked against the manual

| Requirement | In the drawing |
|---|---|
| Footprint 400–600 m² | 573.5 m² |
| Reception 20–50 | 45.1 m² |
| Restaurant 50–90, morning daylight | 69.3 m², east and south glazing |
| Kitchen 20–40 | 22.7 m² |
| Staff room 15–30 | 20.4 m² |
| 4 standard rooms on 1st floor, 18–25 | 20.2 / 22.1 / 22.2 / 23.7 m² |
| 2 public restrooms, 3–8 | 5.8 and 7.9 m² |
| 8 standard rooms on 2nd floor, 18–25 | 19.0 – 24.7 m² |
| 2 deluxe rooms, 28–40 | 30.0 and 38.4 m² |
| Storage 6–12 | 10.6 m² |
| Private bathroom in every guest room | yes |
| Accessible entrance and guest room | ramp 1:12; room 102 with 915 mm doors and 1500 mm turning circle |
| Walls 600 / 250 / 300 | exterior 600, interior 250, bathrooms and vestibule 300 |
| Doors 813 interior, 915 exterior | yes (915 also used for the accessible room and WC) |
| Layers, dimensions, hatching, gridlines, title blocks | separate layers per element type; grid 1–8 / A–H |

Guest-room areas include the private bathroom.

## Assumptions made

- North is up, as in Figure 1 of the manual. The existing site (house, terraces, garden, container, trees)
  was redrawn from that figure because the `SiteLayout.dwg` from Moodle was not available — positions are
  approximate and should be checked against the original file.
- Floor-to-floor height 3.30 m (22 risers of 150 mm); ground level −0.450 m.
- Frost depth for Astana taken as about 1.8–2.0 m; footing depth is conceptual.
- The pool-hall wall towards the building is drawn 300 mm (wet-room wall).

## Files

`build.py` (sheets, site, foundation) · `hotel.py` (floor-plan geometry) · `elev.py` (elevations, section) ·
`plan.py`, `cadlib.py` (helpers) · `render.py` (PDF/PNG export) · `sketches.py` · `report_figures.py` ·
`make_report.js` (report) · `make_all.sh` (runs everything).
Requires Python with `ezdxf`, `shapely`, `pymupdf`, `matplotlib`, `pillow`; Node with `docx`; LibreOffice for the report PDF.

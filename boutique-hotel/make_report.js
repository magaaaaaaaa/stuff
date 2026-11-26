// Builds output/AUL_Boutique_Hotel_Report.docx (CEE 204 individual project report).
// Formatting follows the manual: Arial 12 pt, 1.5 line spacing, 25 mm margins, left aligned,
// bold headings, page numbers on every page except the title page, numbered figures and tables.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, Footer, PageNumber, BorderStyle, ShadingType, LevelFormat, PageBreak, VerticalAlign,
} = require("docx");

const OUT = path.join(__dirname, "output");
const FIGS = JSON.parse(fs.readFileSync(path.join(OUT, "report_figures", "figures.json")));
const ROOMS = JSON.parse(fs.readFileSync(path.join(OUT, "rooms.json")));
const FONT = "Arial";
const W = 9072; // text width in DXA (A4 minus 2 x 25 mm)
const MARGIN = 1417; // 25 mm

// ---------------------------------------------------------------- helpers
const body = (text, opts = {}) =>
  new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 360, after: 160 },
    ...opts.para,
    children: (Array.isArray(text) ? text : [text]).map((t) =>
      typeof t === "string" ? new TextRun({ text: t, font: FONT, size: 24 }) : t
    ),
  });
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: 24, ...o });
const fill = (text) => run(text, { highlight: "yellow" });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: FONT })] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: FONT })] });
const bullet = (text) =>
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    alignment: AlignmentType.LEFT,
    spacing: { line: 360, after: 60 },
    children: (Array.isArray(text) ? text : [text]).map((t) => (typeof t === "string" ? run(t) : t)),
  });

let figNo = 0;
let tabNo = 0;
function figure(key, caption, widthPx = 600) {
  figNo += 1;
  const f = FIGS[key];
  const h = Math.round((widthPx * f.h) / f.w);
  return [
    new Paragraph({
      alignment: AlignmentType.LEFT,
      keepNext: true,
      spacing: { before: 120, after: 80 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(f.path), transformation: { width: widthPx, height: h } })],
    }),
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { line: 300, after: 240 },
      children: [run(`Figure ${figNo}. `, { bold: true, size: 22 }), run(caption, { size: 22 })],
    }),
  ];
}
const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(caption, header, rows, widths) {
  tabNo += 1;
  const cell = (text, w, head) =>
    new TableCell({
      width: { size: w, type: WidthType.DXA },
      borders,
      verticalAlign: VerticalAlign.CENTER,
      shading: head ? { fill: "E7E6E6", type: ShadingType.CLEAR, color: "auto" } : undefined,
      margins: { top: 50, bottom: 50, left: 90, right: 90 },
      children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [new TextRun({ text: String(text), font: FONT, size: 20, bold: !!head })] })],
    });
  return [
    new Paragraph({
      alignment: AlignmentType.LEFT,
      keepNext: true,
      spacing: { line: 300, before: 160, after: 100 },
      children: [run(`Table ${tabNo}. `, { bold: true, size: 22 }), run(caption, { size: 22 })],
    }),
    new Table({
      width: { size: W, type: WidthType.DXA },
      columnWidths: widths,
      rows: [
        new TableRow({ tableHeader: true, children: header.map((t, i) => cell(t, widths[i], true)) }),
        ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, widths[i], false)) })),
      ],
    }),
    new Paragraph({ spacing: { after: 200 }, children: [] }),
  ];
}
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

// ---------------------------------------------------------------- title page (Appendix 1)
const line = (label, value, placeholder) =>
  new Paragraph({
    spacing: { line: 360, after: 200 },
    tabStops: [{ type: "left", position: 3000 }],
    children: [run(label), run("\t"), placeholder ? fill(value) : run(value)],
  });
const titlePage = [
  new Paragraph({ spacing: { before: 1400, after: 60 }, alignment: AlignmentType.CENTER, children: [run("NAZARBAYEV UNIVERSITY", { bold: true, size: 36 })] }),
  new Paragraph({ spacing: { after: 1200 }, alignment: AlignmentType.CENTER, children: [run("School of Engineering", { size: 26 })] }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 200 },
    border: { top: { style: BorderStyle.SINGLE, size: 8, color: "000000", space: 8 }, bottom: { style: BorderStyle.SINGLE, size: 8, color: "000000", space: 8 } },
    children: [run("INDIVIDUAL PROJECT", { bold: true, size: 52 })],
  }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 1000 }, children: [run("Two-Storey Boutique Hotel “AUL”, Astana", { bold: true, size: 30 })] }),
  line("Course code and title", "CEE 204 Civil Engineering CAD and Surveying"),
  line("Student name", "[student name]", true),
  line("Student ID", "[student ID]", true),
  line("Course instructor", "Bakhyt Aubakirova"),
  new Paragraph({
    spacing: { before: 2600, line: 360, after: 400 },
    children: [
      run(
        "I declare that all material in this project is my own work except where there is clear acknowledgment or reference to the work of others and I have read the University statement on Academic Misconduct (Plagiarism) in the Student Handbook."
      ),
    ],
  }),
  new Paragraph({ spacing: { line: 360 }, children: [run("Submission date: "), fill("[date]"), run(".")] }),
];

// ---------------------------------------------------------------- tables data
const specRows = [
  ["Reception", "1", "20 – 50", "1", "45.1"],
  ["Restaurant", "1", "50 – 90", "1", "69.3"],
  ["Kitchen", "1", "20 – 40", "1", "22.7"],
  ["Staff room", "1", "15 – 30", "1", "20.4"],
  ["Standard room, first floor", "4", "18 – 25", "4", "20.2 – 23.7"],
  ["Public restroom", "2", "3 – 8", "2", "5.8 and 7.9"],
  ["Staircase", "1", "–", "2", "14.5 and 14.1"],
  ["Standard room, second floor", "8", "18 – 25", "8", "19.0 – 24.7"],
  ["Deluxe room", "2", "28 – 40", "2", "30.0 and 38.4"],
  ["Storage", "1", "6 – 12", "1", "10.6"],
  ["Building footprint", "", "400 – 600", "", String(ROOMS.footprint)],
];
const techRows = [
  ["Exterior walls", "600 mm", "600 mm"],
  ["Interior walls", "250 mm", "250 mm"],
  ["Bathroom walls", "300 mm", "300 mm (also the wet-room walls of the pool hall)"],
  ["Entrance room walls", "300 mm", "300 mm (vestibule)"],
  ["Interior doors", "2032 × 813 mm", "2032 × 813 mm; 915 mm wide in the accessible room 102 and public WC 1"],
  ["Exterior doors", "2134 × 915 mm", "2134 × 915 mm; double leaf (2 × 915) at the main entrance and the terrace"],
  ["Windows", "Assume", "600 – 2400 mm wide; sill 0.9 m in rooms, 0.3 m in the restaurant and pool hall"],
];
const sheetRows = [
  ["A-01", "Site plan", "1:200"],
  ["A-02", "First floor plan", "1:100"],
  ["A-03", "Second floor plan", "1:100"],
  ["A-04", "North (front) and south elevations", "1:100"],
  ["A-05", "East and west (side) elevations, section A-A", "1:100"],
  ["S-01", "Foundation plan and strip-footing detail", "1:100, 1:25"],
];
const footRows = [
  ["FS-1", "Strip footing", "1200 × 400", "Exterior walls (600 mm)"],
  ["FS-2", "Strip footing", "800 × 400", "Interior load-bearing walls"],
  ["FS-3", "Strip footing", "800 × 400", "Vestibule walls"],
  ["–", "RC basin", "walls 250, base 300", "Pool and hot tub"],
];
const roomRows = (list) => list.map(([n, a, s]) => [n, a, s === "extra" ? "additional" : s || "–"]);

// ---------------------------------------------------------------- content
const content = [
  h1("1. Project specifications"),
  body(
    "The task is to design a two-storey boutique hotel for a client in Astana. The client’s plot measures 40 m × 60 m and already contains a two-storey house, terraces, a gardening area and a steel storage container. The southern 40 m × 30 m of the plot is reserved for the hotel. Table 1 compares the designer specifications of the project manual with the areas achieved in the final drawings, and Table 2 does the same for the technical specifications."
  ),
  ...table("Designer specifications and the values achieved", ["Space", "Min. qty", "Area range, m²", "Provided", "Area provided, m²"], specRows, [3100, 1000, 1700, 1100, 2172]),
  body("Guest-room areas include the private bathroom. All spaces are inside the specified ranges, so the permitted ±20 % deviation was not needed."),
  ...table("Technical specifications", ["Element", "Required", "As drawn"], techRows, [2200, 1900, 4972]),
  body("The remaining requirements of the manual are met as follows:"),
  bullet("The restaurant has windows on the east and south sides and an east terrace, so it receives daylight from sunrise onwards."),
  bullet("Every guest room has a private bathroom."),
  bullet("Corridors and two staircases are shown on both floor plans."),
  bullet("The main entrance has a 1:12 ramp, and room 102 on the first floor is an accessible guest room next to the reception."),
  body("In addition to the manual, the following personal requirements were set for the design:"),
  bullet("an indoor swimming pool with a sauna;"),
  bullet("the hotel placed near the edge of the site;"),
  bullet("a public balcony on the second floor;"),
  bullet("no repeated room pattern: every room has its own layout and its own position, while the plan stays logical and functional."),
  body("The AutoCAD file contains six drawing sheets, listed in Table 3. All drawings use millimetres; levels are given in metres."),
  ...table("Drawing sheets in the DWG file", ["Sheet", "Content", "Scale"], sheetRows, [1300, 5772, 2000]),

  h1("2. Designer notes"),
  h2("2.1 Concept and inspiration"),
  body(
    "The hotel is called AUL. An aul is the traditional Kazakh settlement: a small group of dwellings, each slightly different, gathered around a shared open space and turned away from the wind. I used this idea instead of the usual hotel block with one straight corridor and identical rooms on both sides."
  ),
  body(
    "The building is an L that wraps around an arrival court. The entrance sits on a diagonal wall at the inner corner of the L, so it faces guests as they arrive. The shanyrak, the circular crown of the yurt roof, appears twice: as the paving pattern of the court and as a round rooflight above the lounge where the two wings meet. Each guest room is treated as its own small “house”: the rooms differ in size, proportion, orientation and in the position of the bathroom and the entrance."
  ),
  h2("2.2 Location"),
  body([
    fill(
      "[To be completed by the student: coordinates of the selected plot in Astana, the map screenshot with nearby sites, and two or three sentences explaining why this location was chosen. Use the same location that was submitted on 30 October.]"
    ),
  ]),
  h2("2.3 Organisation of the functional spaces"),
  body(
    "The first floor has three zones. The public zone is the reception at the corner of the L and the restaurant in the east end of the south wing. From the reception desk the staff can see the entrance, both corridors and the restaurant door. The kitchen lies on the north side of the restaurant and has its own service door to the parking aisle, so deliveries never cross the lobby."
  ),
  body(
    "The wellness zone is the pool hall in the south-west corner. Guests reach it only through the changing rooms; the sauna opens to the pool through a shower lobby, and the plant room is next to the pool. The private zone consists of four guest rooms: two facing south, including the accessible room 102 beside the reception, and two in the quiet west wing. The staff room is at the north end of the west wing and has its own entrance."
  ),
  body(
    "On the second floor ten rooms are arranged along two corridors that meet in a lounge. Storage is next to stair 1. The two staircases are at opposite ends of the building, so every room has two escape routes. The roof of the single-storey pool hall is the public balcony, and both corridors open onto it. Wherever possible, bathrooms are placed against corridors, staircases and north walls, so that the bedrooms keep the facades with the best light and are shielded from noise."
  ),
  h2("2.4 Influence of the site and of Astana’s climate"),
  body(
    "The existing gates are in the north-west corner of the plot and the existing house stands in the north. I placed the hotel 3.0 m from the west and south boundaries. This leaves the north-east part of the hotel zone free for the arrival court, the drop-off aisle and five parking bays, and it keeps the largest possible distance from the existing house. The new driveway runs from the existing gates along the west boundary and turns east below the tree belt. The house, the terraces and the gardening area are not changed."
  ),
  body("Astana has long and very cold winters, strong steppe winds that blow mostly from the south-west, and short hot summers. The design responds in these ways:"),
  bullet("The two wings of the L block the south-west wind, and the court opens to the east, where it receives the morning sun."),
  bullet("Guests enter through a vestibule that works as an air lock, under a canopy."),
  bullet("The volume is compact and two storeys high, with 600 mm exterior walls."),
  bullet("Large windows face south and east. The north facades carry stairs, bathrooms, the kitchen and storage, and have only small openings."),
  bullet("The flat roof drains internally behind a parapet, so snow and ice do not slide onto the entrances."),
  bullet("The first-floor level is 450 mm above the ground, and the footings are at −2.300 m, below the assumed frost depth."),
  bullet("The pool and the sauna can be used all winter; the balcony faces south-west for summer evenings."),
  h2("2.5 Challenges and how they were resolved"),
  bullet([run("Footprint limit. ", { bold: true }), "The pool hall alone takes about 95 m². I kept it single-storey and used its roof as the public balcony, and I kept the corridors short. The final footprint is " + ROOMS.footprint + " m²."]),
  bullet([run("Variety without disorder. ", { bold: true }), "All rooms sit on one grid of load-bearing walls (axes 1–8 and A–H). The variety comes from orientation, proportion, corner positions and bathroom placement, not from arbitrary shapes."]),
  bullet([run("The diagonal entrance wall. ", { bold: true }), "A 45° wall leaves triangular corners. They became the luggage room on the first floor, and a reading nook and the dressing room of deluxe room 210 on the second floor."]),
  bullet([run("Humidity and noise from the pool. ", { bold: true }), "The pool hall is a separate volume with 300 mm wet-room walls and its own plant room; the bathroom of room 101 acts as a buffer on the shared wall."]),
  bullet([run("Accessibility. ", { bold: true }), "Because the floor is 450 mm above the ground, a 5.4 m long ramp at 1:12 runs beside the entrance steps. Room 102 and public WC 1 have 915 mm doors and a 1500 mm turning circle."]),
  bullet([run("Morning light at the west edge. ", { bold: true }), "With the building in the south-west corner, the restaurant was moved to the far east end of the south wing, where it has both east and south windows and a terrace."]),
  h2("2.6 Additional features"),
  bullet("Indoor pool (4.0 × 8.2 m) with a hot tub, a sauna and changing rooms: a reason to stay in the hotel during the long winter."),
  bullet("Public balcony of 51 m² on the pool-hall roof: an outdoor room shared by all guests of the second floor."),
  bullet("Arrival court with shanyrak paving: gives the hotel its identity and a sheltered place to arrive."),
  bullet("Second staircase: a second escape route from the upper floor."),
  bullet("Lounge with a circular rooflight and a reading nook: daylight in the middle of the plan and a place to meet."),
  bullet("Luggage room, plant room and restaurant terrace: make the daily operation of the hotel easier."),
  h2("2.7 Assumptions"),
  bullet("North is at the top of the drawings, as in Figure 1 of the project manual; the existing site features were redrawn from that figure."),
  bullet("Storey height 3.30 m, clear height 3.00 m, ground level −0.450 m."),
  bullet("Structure: load-bearing masonry walls with 300 mm reinforced-concrete floor and roof slabs."),
  bullet("Seasonal frost depth taken as about 2 m; it must be confirmed by a geotechnical survey."),

  h1("3. Preliminary sketching"),
  body(
    "The design started with a reading of the site (Figure 1): the path of the sun, the prevailing winter wind, the position of the existing gates and the distance to the existing house. This showed that the building should stand in the south-west of the hotel zone and open towards the east."
  ),
  ...figure("sketch1_site", "Preliminary sketch 1: sun, wind and access on the site.", 400),
  body(
    "Three building forms were then compared inside the 40 m × 30 m zone (Figure 2). A simple bar leaves no sheltered outdoor space and leads to repeated rooms. A U-shaped building protects a court, but the court faces north and the footprint exceeds 600 m². The L in the south-west corner blocks the wind, opens the court to the morning sun and gives rooms on three different sides, so it was chosen."
  ),
  ...figure("sketch2_options", "Preliminary sketch 2: three massing options; option C was chosen."),
  body("Finally, bubble diagrams (Figure 3) fixed which spaces must be next to each other before any walls were drawn."),
  ...figure("sketch3_bubbles", "Preliminary sketch 3: bubble diagrams of the first and second floors."),

  h1("4. Site plan"),
  body(
    "Figure 4 shows the hotel inside the site. The building stands 3.0 m from the west and south boundaries and 5.2 m from the east boundary. Guests arrive through the existing gates, follow the new 3.5 m driveway and stop in a 6.0 m wide aisle beside the arrival plaza. There are five parking bays, one of them accessible, and a step-free route leads from this bay over the plaza and the ramp to the entrance. A footpath links the plaza with the existing garden. The restaurant terrace lies on the east side, a small sun deck serves the pool hall on the west side, and hedges fill the two 3.0 m setbacks."
  ),
  ...figure("site", "Site plan, scale 1:200 (sheet A-01).", 500),

  h1("5. Floor plans"),
  body(
    "The first-floor plan is shown in Figure 5 and its rooms are listed in Table 4. The structural grid has eight axes in the east–west direction (1–8) and eight in the north–south direction (A–H). Section line A-A is marked on both plans."
  ),
  ...figure("gf", "First floor plan, scale 1:100 (sheet A-02)."),
  ...table("Room schedule, first floor", ["Room", "Area, m²", "Specified, m²"], roomRows(ROOMS.gf), [5072, 2000, 2000]),
  body(
    "The second-floor plan is shown in Figure 6 and its rooms in Table 5. Rooms 201–203 face south, 204–206 face west, 207 looks north-east, 208 looks north into the court, deluxe room 209 occupies the south-east corner and deluxe room 210 has the diagonal glazed wall above the entrance."
  ),
  ...figure("ff", "Second floor plan, scale 1:100 (sheet A-03)."),
  ...table("Room schedule, second floor", ["Room", "Area, m²", "Specified, m²"], [...roomRows(ROOMS.ff), ["Public balcony (open)", "51.3", "additional"]], [5072, 2000, 2000]),

  h1("6. Foundation plan"),
  body(
    "The foundation is a simplified conceptual layout (Figure 7). Continuous reinforced-concrete strip footings run under all load-bearing walls on the grid; light partitions stand on the 150 mm ground slab. The pool and the hot tub have their own reinforced-concrete basins. The footing types are listed in Table 6, and Figure 8 shows a typical section through the exterior strip footing."
  ),
  ...figure("fnd", "Foundation plan, scale 1:100 (sheet S-01)."),
  ...table("Footing schedule", ["Mark", "Type", "Size, mm", "Position"], footRows, [1200, 2200, 2400, 3272]),
  ...figure("fnd_detail", "Typical strip footing FS-1, scale 1:25 (sheet S-01).", 330),

  h1("7. Elevations"),
  body(
    "The north elevation (Figure 9) is the front of the hotel: it faces the arrival court. The diagonal entrance wall with the vestibule, canopy, steps and ramp appears foreshortened in the middle. The south elevation (Figure 10) shows the single-storey pool hall with the public balcony on its roof and the large restaurant windows."
  ),
  ...figure("el_n", "North (front) elevation, scale 1:100 (sheet A-04)."),
  ...figure("el_s", "South elevation, scale 1:100 (sheet A-04)."),
  body(
    "The side elevations are shown in Figures 11 and 12. The upper floor is clad with horizontal boards, the first floor is rendered and the plinth is finished with stone up to the floor level. The parapet of the two-storey wings is at +7.200 m."
  ),
  ...figure("el_e", "East (side) elevation, scale 1:100 (sheet A-05)."),
  ...figure("el_w", "West (side) elevation, scale 1:100 (sheet A-05)."),

  h1("8. Building section"),
  body(
    "Section A-A (Figure 13) is an offset section looking east. Its southern part cuts through the pool and the public balcony above it; its northern part cuts through the plant room, the corridors, stair 1 and the staff room with room 207 above. The section shows the storey height of 3.30 m, the half landing of the stair at +1.650 m, the 300 mm floor and roof slabs, the roof insulation laid to falls and the strip footings at −2.300 m."
  ),
  ...figure("sec", "Section A-A, scale 1:100 (sheet A-05)."),

  h1("9. References"),
  ...[
    "Nazarbayev University, School of Engineering. Individual Project Manual, CEE 204 Civil Engineering CAD & Surveying (course handout).",
    "Neufert, E. and Neufert, P. (2012). Architects’ Data. 4th ed. Chichester: Wiley-Blackwell.",
    "Buxton, P. (ed.) (2018). Metric Handbook: Planning and Design Data. 6th ed. Abingdon: Routledge.",
    "Ching, F. D. K. (2020). Building Construction Illustrated. 6th ed. Hoboken: Wiley.",
    "ISO 21542:2021. Building construction – Accessibility and usability of the built environment. Geneva: International Organization for Standardization.",
    "SP RK 2.04-01-2017. Building climatology. Astana: Committee for Construction, Housing and Utilities of the Republic of Kazakhstan.",
    "SP RK 3.02-107-2014. Public buildings and structures. Astana: Committee for Construction, Housing and Utilities of the Republic of Kazakhstan.",
    "SP RK 5.01-102-2013. Foundations of buildings and structures. Astana: Committee for Construction, Housing and Utilities of the Republic of Kazakhstan.",
  ].map(
    (t, i) =>
      new Paragraph({
        numbering: { reference: "refs", level: 0 },
        alignment: AlignmentType.LEFT,
        spacing: { line: 360, after: 100 },
        children: [i >= 5 ? run(t, { highlight: "yellow" }) : run(t)],
      })
  ),
];

// ---------------------------------------------------------------- document
const page = { size: { width: 11906, height: 16838 }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } };
const doc = new Document({
  creator: "",
  title: "Individual Project – Two-Storey Boutique Hotel AUL",
  styles: {
    default: {
      document: { run: { font: FONT, size: 24 } },
      heading1: { run: { font: FONT, size: 30, bold: true, color: "000000" }, paragraph: { spacing: { before: 360, after: 180 }, keepNext: true } },
      heading2: { run: { font: FONT, size: 26, bold: true, color: "000000" }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true } },
    },
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 280 } } } }] },
      { reference: "refs", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "[%1]", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 620, hanging: 620 } } } }] },
    ],
  },
  sections: [
    { properties: { page }, children: titlePage },
    {
      properties: { page },
      footers: {
        default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 22 })] })] }),
      },
      children: content,
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(OUT, "AUL_Boutique_Hotel_Report.docx");
  fs.writeFileSync(out, buf);
  console.log("written", out, "figures", figNo, "tables", tabNo);
});

## 11 November 2026 — IR results and N17–N22 (84 lessons)

Lab 6 SPM IR drop was run in OpenROAD on the existing `final/` (read_db, liberty tt_025C_1v80, SDC, SPEF nom; set_pdnsim_net_voltage VPWR 1.80 / VGND 0; analyze_power_grid with -voltage_file and -enable_em). Official run without an activity override: total power 1.28 mW (STA report_power 1.275 mW), VPWR worst 132 µV / average 35.2 µV, VGND worst 100 µV / average 33.2 µV, combined 217 µV at clkbuf_0_clk; EM max 35.5 µA (VPWR, 743 resistors) and 30.5 µA (VGND, 751). Recorded heat map, CSVs and logs in `labs/analysis_examples/irdrop/`. A first run with activity 0.1 (0.622 mW) was discarded. The original Lab 6 folder still has no IR step. Lesson 63 and related wording in lessons 8, 14, 38, 56 and 62 use these recorded figures. No VSRC_LOC_FILES; static vectorless; EM currents are not a pass/fail against LEF limits.

Six new lessons complete the gap analysis. N18 (24, liberty_characterization.html) after Liberty tables: teaching sweep and bisection; no new 7×7. N19 (27, latch_time_borrowing.html) after Setup/Hold: HD latch LEF sizes, teaching STA. N17 (31, reliability_aging.html) after EM: HCI, BTI, TDDB, self-heating; no SKY130 aging parameter. N22 (32, dfm_yield.html) after N17: corners vs MC, redundant vias, lesson-2 yield arithmetic; no invented yield. N21 (57, hierarchical_eco.html) after Caravel: abstracts, budgets, LibreLane using_ecos.md; no ECO run. N20 (77, comparators_ldo_por.html) after References: StrongARM, LDO, POR; teaching. Former 24–25 are 25–26; 26–28 are 28–30; 29–52 are 33–56; 53–71 are 58–76; 72–78 are 78–84. Antenna is lesson 51. IR signoff is 63.

## 11 November 2026 — N13–N16 (78 lessons)

Four new lessons, first Tier-3 checkpoint. N16 (32, clock_generation.html) after the Clock Tree: recorded 11-stage inv_1 ring, ngspice 44.2, 1.849 GHz / 24.58 ps at 1.80 V; Caravel DCO from official housekeeping docs. N15 (55, digital_signal_integrity.html) after Routing: Miller factors and a labelled met1 hand estimate. N14 (58, power_integrity_signoff.html) after Physical Signoff: LibreLane IRDropReport from the local irdrop.tcl; Lab 6 IR still not executed, no invented map. N13 (66, post_silicon_bringup.html) after Tapeout: wafer sort, shmoo, debug order, Caravel SPI and microcotb, from documentation. Former 32–53 are 33–54; 54–55 are 56–57; 56–62 are 59–65; 63–74 are 67–78. Antenna is lesson 47.

## 11 November 2026 — N9 RTL patterns, N11 Caravel, N12 tapeout (74 lessons)

Three new lessons. N9 (29, rtl_patterns.html) opens Part V: Yosys 0.52 binary vs one-hot traffic light on the filtered HD Liberty (98.8448 vs 177.6704 µm²); one-hot reset bit maps to dfstp_2; Verilator 5.032 CASEINCOMPLETE on a latch pitfall; SPM lint already recorded as all-zero. N11 (51, caravel_integration.html) after Floorplan: wrapper ports from the local LibreLane example, 38 GPIOs from defines.v, three documented hardening strategies; no wrapper run. N12 (62, tapeout.html) after Power/Package: Lab 6 final/ deliverables, signoff checklist, Tiny Tapeout official SKY 161 × 112 µm and FAQ about 160×100 µm. Former 29–49 are 30–50; 50–59 are 52–61; 60–71 are 63–74. Antenna is lesson 46.

## 11 November 2026 — lesson 37 dont_use correction; N8 power analysis (71 lessons)

Lesson 37 (Datapath; now 38 after N8’s insertion) was re-run through Yosys 0.52 with LibreLane Classic’s default exclusion lists (`no_synth.cells` + `drc_exclude.cells`, the same paths as the Lab 6 SPM `resolved.json`). Headline inferred-add area is 1,089.7952 µm² (121 cells), inferred 8-bit mul 2,828.9632 µm² (293 cells); unfiltered 713.184 / 1,904.3264 kept only as the reason the lists exist (ABC had used `lpflow_*` as ordinary gates). Structural RCA unchanged at 320.3072 µm². The floorplan macro power-ring table’s I/O-ring cross-reference was corrected from a stale “45” to lesson 53 (now 54 after N8).

New lesson 32, Power Analysis & Low-Power Cells, after Clock Gating: OpenSTA `report_power` on the Lab 6 SPM, nine post-PnR corners, pre-PnR vs post-CTS vs post-route at nom_tt, `lpflow` LEF table, activity caveat. Former 32–70 are 33–71. Antenna is lesson 45.

## 11 November 2026 — lessons 34, 36 and 37; E16 and E21 (70 lessons)

The LibreLane Classic 80-step diagram, a `final/` directory tour and a metrics table were added to lesson 8 (design flow), from Classic.Steps and the Lab 6 SPM run `RUN_2026-11-11_16-09-06`. New lesson 34 covers DFT beyond the scan chain (fault models, test time, BIST, JTAG); lesson 36 covers SRAM and the OpenRAM macros in this PDK; lesson 37 covers adders and multipliers with recorded Yosys 0.52 mappings. Timed Path is now 35; former 35–67 are 38–70. A short SPM utilization table was added to the floorplan lesson (full table remains in Placement).

## 11 November 2026 — lessons 46, 47, 49 and Labs 6–7 (67 lessons)

Placement, routing & timing closure, and physical signoff were added after Floorplan. Metal Fill is lesson 48; former 47–64 are 50–67. Lab 6 is a recorded LibreLane 3.0.17 RTL-to-GDS run of the bundled SPM (45% core utilization, GDS, DRC, XOR and LVS all clean) plus a 30/45/60 routing sweep. Lab 7 is Magic/KLayout/Netgen debug on a SKY130 inverter, with antenna left in lesson 41.

# ASIC design lessons — registry

Reorganized on 9 November 2026; see the final section.

Reviewed and expanded on 6 November 2026.

Open [index.html](index.html) for the course and [review.html](review.html) for the technical review, scope and next steps. Original lesson numbering and filenames are preserved. The earlier working notes have been consolidated here so that superseded technical claims do not conflict with the revised lessons.


## 11 November 2026 — lessons 35 and 36 (64 lessons)

- New [lesson 35, Multi-Corner STA](multicorner_sta.html): nine-corner OpenSTA/LibreLane results on the SKY130 SPM, OCV, CRPR, hold delay cells. Recorded reports in `labs/analysis_examples/multicorner_sta/`.
- New [lesson 36, Functional Verification](functional_verification.html): self-checking TBs, cocotb 2.1, SymbiYosys formal (BMC, cover, k-induction, a planted-bug FAIL), and SKY130 gate-level sim with OpenSTA SDF. Recorded sources and logs in `labs/analysis_examples/verification/`.
- Former lessons 35–62 are now 37–64. Filenames unchanged. Navigation, index, topic lists, in-text “lesson N” links, glossary, labs pages, review notes and `course_manifest.json` updated. `tools/validate.py` checks 1–64.

## Revision

- Reviewed all 34 original lessons against published primary sources.
- Corrected identified schematic, timing, process-interpretation and unit/scope errors.
- Added sources, worked examples, cross-disciplinary connections and solved checkpoints.
- Added 8 analog and mixed-signal lessons in the existing illustrated format.
- Added a searchable directory, glossary and three suggested learning paths.
- Kept local assets and scripts so the course can be read offline.
- Analytical plots are teaching models; no circuit/signoff simulation is claimed.


## Next development priority

Add a few reproducible SKY130 labs: inverter characterization, bias/startup, acquisition settling, extracted coupling, and an analog-ready/CDC integration example. Pin the PDK and tools, include runnable inputs, and distinguish measured or simulated results from expectations. See the review page for specific remaining limits and advanced topic ideas.


## Practical lab expansion — 6 November 2026

Added lessons 43–50 (original numbering) and five detailed runnable labs, preserving the prior 42-lesson sequence. Added pinned local SKY130 model subset, exact offline synthesis Liberty, source hashes/licenses, actual recorded SPICE and digital results, numerical FFT/trim examples, and shared lab setup/navigation. Lab4 is explicitly a geometry-derived analytical RC teaching estimator, not qualified PEX. Added source-link repair, targeted numerical refinement and portable-path checks. See review.html and review/validation_summary.json for the complete current scope.


## Reorganization and foundations — 9 November 2026

- Added nine foundation lessons (Part I) that define the physical chip and the shared vocabulary before any other lesson uses it.
- Reordered the 50 existing lessons into eight further parts so that prerequisites come first. Notable moves: Setup & Hold now follows Timing; Power Grid follows Site Rows because Cell Template uses its routing tracks; Electromigration follows Parasitics; Feedback precedes Differential Pairs because common-mode feedback is a feedback loop; the analog and mixed-signal lessons start from the MOSFET and signals foundations.
- Updated every in-text lesson reference; rewrote six phrases whose meaning depended on the old order ("the next lesson", "lessons 1–3", "lessons 1–5", "lessons 1–42").
- Spelled out 20 acronyms at their first use in the existing lessons; added an FFT definition to the FFT measurement lesson.
- Expanded the glossary to 192 terms (221 since 11 November) and added dotted-underline term definitions to every lesson page (assets/course.js).
- Bundled four Apache-2.0 images from the SkyWater PDK and Caravel documentation (assets/foundations/ATTRIBUTION.txt).

## Cleanup pass — 9 November 2026
- Every lesson opens with "What you will learn" and has at least two checkpoints.
- Notes about which files a reviewer opened were rewritten as guidance or moved into
  "Where the numbers come from" boxes; duplicated passages were removed.
- Overlaps trimmed: Timing vs Setup & Hold, Metal Layers vs lesson 3, RDL vs lesson 6.
- Context pass, 10 November 2026: lesson 8 walks through every step of the digital and
  analog flows (what happens, files in and out, open-source and commercial tools, example
  commands, what to check); every other lesson has a "Where this fits" panel; 22 sections
  gained "In the open SKY130 flow" notes; the glossary gained the tool names.
- Liberty was split into lessons 22 and 23, giving 60 lessons (62 since 11 November).
- Choppy captions and fact-list paragraphs were rewritten as flowing prose; the repeated
  caveats in I/O Power and Cell Template were consolidated into one note each.
- Floorplan (now lesson 43; 41 at the time) and Clock Tree (now lesson 30; 29 at the time) were expanded with new
  sections, figures and a core-sizing calculator.
- Consistent naming (SKY130; met1–met5, with generic M1 only in generic diagrams;
  LibreLane first) and American spelling throughout.
- Legacy per-page style blocks that duplicated assets/course.css were removed;
  page-specific rules were kept.

## Delay physics, the timed path and a figure audit — 11 November 2026

Lesson numbers in this section use the 11 November order.

### New lessons
- **Lesson 27, [Delay from Physics: Transistor, Contact, Via, Wire & Gate](delay_physics.html)** (Part IV, after Parasitics). One SKY130 net, from the inv_4 drain through licon, li1, mcon, met1, via, met2 and via2 to 1&nbsp;mm of met3 and back down to an inv_1 gate. Sections: the five physical pieces; the transistor as a current source (ngspice I–V of nfet_01v8 W 0.65 and pfet_01v8_hvt W 1.0, L 0.15&nbsp;µm: 336 and 148&nbsp;µA on-current); g<sub>m</sub>, r<sub>out</sub> and gain and why they do not set delay; effective resistance over the half swing (4.2 and 9.8&nbsp;kΩ); the gate as a capacitor (C<sub>ox</sub>·W·L plus overlap, 2.47&nbsp;fF estimate against 2.302&nbsp;fF Liberty); FO4; contacts and vias in series and parallel (SkyWater Table 91 against ORFS setRC.tcl); wire R by the square and C per micrometer (HD tech LEF); Elmore and distributed RC (0.38&nbsp;RC against 0.69&nbsp;RC); the worked chain (103.6 / 199.1&nbsp;ps hand estimate against 110.7 / 182.1&nbsp;ps ngspice); fanout; logical effort and buffer trees; wire length and repeaters; a whole-chain calculator. 16 figures, 9 tables, 5 checkpoints.
- **Lesson 34, [A Timed Logic Path: Registers, Clocks, Scan & Speed/Power](timed_path.html)** (Part V, after Scan). sdfxtp_1 → nand2_1 → inv_1 → nor2_1 → buf_2 → sdfxtp_1 with a buffered clock tree (launch 420&nbsp;ps, capture 470&nbsp;ps) and the scan chain. Arrival and slew stage by stage from Liberty tt; setup slack +0.276&nbsp;ns and hold slack +0.648&nbsp;ns, drawn to scale and in OpenSTA report layout; the scan-shift hold check (+0.370&nbsp;ns); slack against skew (all checks pass from −226 to +420&nbsp;ps); the speed/power levers: αCV²f plus leakage, supply voltage (FO4 and energy from 1.0 to 1.8&nbsp;V, minimum energy-delay product at 1.6&nbsp;V), sizing into a fixed load, threshold voltage and pipelining; a setup/hold/scan-hold calculator. 8 figures, 8 tables, 4 checkpoints.
- Reproducible numbers for both lessons: labs/analysis_examples/delay_physics/ (ngspice decks and summary, Liberty path timing, hand calculations; see its README.txt). liberty_path.py and hand_calcs.py were re-run on a copy and reproduced the recorded JSON byte for byte.

### Renumbering and integration
- Old 27–32 became 28–33 and old 33–60 became 35–62; filenames are unchanged. Updated: lesson-meta lines, prev/next footers, topic lists, the index (62 cards, part ranges, reading paths), every in-text "lesson N" reference and link text, labs pages, glossary, review.html (map table) and review/course_manifest.json.
- A renumbering bug was found and fixed: references followed by a period had been skipped. Corrected: the Drive Strength ECO link (→ 41), a Floorplan aria-label (37/36), two Setup & Hold references (Scan → 33, bilinear interpolation → 23) and a Timing figure label (→ 23). All remaining references were then reviewed one by one.
- Glossary: 26 new terms (218 rows; 213 terms underlined by assets/course.js). Cross-links to the new lessons from Parasitics, Drive Strength, Timing, Setup & Hold, Scan, Clock Tree and Metal Layers.

### Figure audit (every page rendered headlessly in Chrome)
Two automated checks (text overlapping text or leaving the SVG; text crossed by a drawn line) plus a visual review of every figure. Both checks now report nothing that is not intentional (labels placed on pins, tracks or dimension lines), and every JS-generated figure's static fallback equals its rendered output (77 figures). Fixes:
- **Redrawn:** Clock Tree figure 2 (skew between FF1 and FF2 clock waveforms, jitter around ideal edges with T₁ ≠ T₂, a two-level H-tree with 16 sinks); Level Shifters figure 2 (a transistor-level low-to-high shifter: VDDL inverter, NMOS pull-downs N1/N2, cross-coupled PMOS P1/P2 on VDDH, with the switching sequence).
- **Layout:** assets/course.css no longer forces side-by-side figures to 560&nbsp;px on desktop (Gate Topologies figure overflowed).
- **Labels moved off lines, shapes or each other, or given a white halo:** antenna, bigger_cells (3 figures), cell_layout (2), cell_template (3), clock_gating_power_states, crosstalk_return_paths, decap (2), delay_physics (cross-section title, breakdown total), dff_inside (2), die_anatomy (2; callouts re-ordered so leaders do not cross), drive_strength (2), feedback_stability, fill_cells, floorplan (callouts re-ordered), gate_topologies (3), liberty, liberty_tables, loads (2), logic_gates (2), metal_layers, mosfet_basics, pcb_path, pin_access (3; pin letters A and C had been hidden under their M2 risers), power_grid (3), signals_primer (2), silicon_wafer, site_rows (2), spare_eco (stray line replaced by a labeled arrow), timed_path (2), timing.
- **Clipping:** logic_gates figure viewBox widened (right-hand NAND2 wiring was cut off); pcb_path, pin_access, signals_primer and silicon_wafer viewBoxes enlarged; delay_physics cross-section cropped.
- **Typesetting and units:** subscripts in mosfet_basics (I<sub>D</sub>, V<sub>GS</sub>, V<sub>th</sub>) and loads (C<sub>load</sub>); Black's equation in electromigration with real superscript and subscript; Ω in parasitics; Drive Strength figure 6 gained axes (h, d in units of τ) and its caption states the units; proper minus signs in timed_path.
- **Numbers rechecked:** delay_physics parallel cuts 4.5/4 = 1.125&nbsp;Ω (was shown rounded to 1.12); loads figure 2 now reads "≈27&nbsp;µm of met1" (2.30&nbsp;fF ÷ 0.0847&nbsp;fF/µm = 27.2&nbsp;µm). The metal_fill density statement (MAXIMUMDENSITY 70, 700&nbsp;µm window, 70&nbsp;µm step on met1–met4 only) was checked against sky130_fd_sc_hd.tlef; the contact and via resistances against SkyWater RCX Table 91.
- **Spelling:** honour → honor (cell_template), neighbours → neighbors (site_rows, cell_layout).
- Generic teaching diagrams keep M1/M2/… labels by design (stated in Metal Layers); SKY130-specific figures use li1 and met1–met5.

### Labs
- Labs 2 and 4: run_lab.py plotting now picks round axis ticks (and 10⁻ⁿ labels on log axes); the recorded result SVGs were re-ticked in place without touching the data. review/lab_file_hashes.json was recomputed for every listed file.

## Power rings for dropped-in macros — 11 November 2026
- Request: add the concept of a power ring for a dropped-in macro. Placed as a new section 7 of
  Floorplan (lesson 43) rather than a new lesson, so no lesson numbers changed; the old
  sections 7–10 became 8–11 (no page linked to those anchors).
- Content: the hard macro's LEF abstract (pins, OBS); the hierarchical method (met5 straps over
  a macro with no met5, via4 onto its met4 ring) and the ring method (a ring around the macro
  that the core straps end on), named as in LibreLane's integration and power-routing guide;
  a table of core ring, built-in ring, block ring and pad/seal ring; halo, cut rows, endcaps;
  a met4/met5/via3/via4 table; worked example 1 (the SRAM: 5.33 mA, 4 via4 taps per net at
  1.33 mA = 53% of 2.49 mA, ≈ 9 mV for power plus ground); worked example 2 (illustrative
  400 × 300 µm, 20 mA block: ΔV = (I/P)(Rs/W)s²/8; 106 mV with one feed on 1.6 µm met4, 1.1 mV
  with ten); the mixed-signal case (Caravel vdda1/vssa1 at 3.3 V versus vccd1/vssd1 at 1.8 V,
  own ring, own feeds, routing blockage, guard ring is not a supply ring); an "In the open
  SKY130 flow" note with LibreLane's default macro grid, PDN_MACRO_CONNECTIONS and a labeled
  sketch of a custom add_pdn_ring script; a "Where the numbers come from" box.
- Sources checked: the SRAM LEF (size 479.78 × 397.5 µm; vssd1 ring 1.36–3.1 µm and vccd1
  4.76–6.5 µm in from each edge; OBS met1 99.4%, met2 99.4%, met3 96.5%, met4 96.9%, no met5),
  its TT Liberty file and OpenRAM datasheet (4.79 mW per port read or write; 9.59 per access in
  the .lib; leakage 0.0095 mW); HD tech LEF (met4 0.047 Ω/sq, 6.8 mA/µm; met5 0.0285 Ω/sq,
  10.17 mA/µm; via4 0.8 µm cut, 0.8 µm spacing, enclosure 0.19/0.31 µm, 2.49 mA; via3 0.48 mA);
  SkyWater Table 91 (via4 0.38 Ω, via3 3.41 Ω); open_pdks LibreLane config (strap 1.6 µm,
  spacing 1.7 µm, pitch 153.6/153.18 µm, offsets 16.32/16.65 µm); LibreLane variables
  (PDN_*_HALO and FP_MACRO_*_HALO 10 µm, PDN_CORE_RING false, PDN_CONNECT_MACROS_TO_GRID true,
  PDN_MULTILAYER, PDN_MACRO_CONNECTIONS with its old name FP_PDN_MACRO_HOOKS) and its default
  pdn_cfg.tcl; the OpenROAD pdn README; the Caravel wrapper Verilog. Illustrative: the SRAM
  placement, the block, its current, the ring widths and feeds, the 1% budget and the
  custom-script sketch.
- Figures 4–7 are static SVGs generated by tools/macro/mr_svg.py (not shipped), rendered
  headlessly at 1000 px and in the page at 1280 px and checked by eye and by the overlap,
  clipping and font audit. The line-through-text audit flags five marker numbers that sit
  on purpose on a white disc over a strap.
- Glossary: Power ring, Routing blockage and Strap added (221 rows, 216 terms in course.js);
  OBS now also matches "obstruction".
- Cross-links added to Power Grid (14), Electromigration (28), I/O Power (49), Crosstalk &
  Return Paths (61) and Mixed-Signal Verification (62).

## Lesson registry

Numbers are the current (11 November 2026) order. "10 Nov" is the number used from 9 to 10 November; "Original" is the number before the 9 November reorganization.

| No. | 10 Nov | Original | Lesson | Part | Status |
|---|---|---|---|---|---|
| 1 | 1 | — | [What Is a Chip? Board, Package & Die](chip_overview.html) | I | New, 9 November 2026 |
| 2 | 2 | — | [The Silicon Wafer: From Crystal to Dies](silicon_wafer.html) | I | New, 9 November 2026 |
| 3 | 3 | — | [How a Die Is Built: SKY130 Layers & Lithography](fabrication_layers.html) | I | New, 9 November 2026 |
| 4 | 4 | — | [The MOSFET: SKY130’s Transistor](mosfet_basics.html) | I | New, 9 November 2026 |
| 5 | 5 | — | [Anatomy of a Die: Core, Pad Ring & Seal Ring](die_anatomy.html) | I | New, 9 November 2026 |
| 6 | 6 | — | [Packages: Wire Bonds, Flip-Chip, QFN & WLCSP](packages.html) | I | New, 9 November 2026 |
| 7 | 7 | — | [The PCB and the Path to the Transistor](pcb_path.html) | I | New, 9 November 2026 |
| 8 | 8 | — | [The Design Flow and Its Files: RTL to GDS](design_flow.html) | I | New, 9 November 2026 |
| 9 | 9 | — | [Signals Primer: DC, AC, RMS, Decibels & the FFT](signals_primer.html) | I | New, 9 November 2026 |
| 10 | 10 | 5 | [Logic Gates at Transistor Level](logic_gates.html) | II | Reviewed lesson |
| 11 | 11 | 7 | [Drive Strength & Transistor Sizing](drive_strength.html) | II | Reviewed lesson |
| 12 | 12 | 8 | [More Gate Topologies](gate_topologies.html) | II | Reviewed lesson |
| 13 | 13 | 1 | [Site Rows & Standard Cell Placement](site_rows.html) | III | Reviewed lesson |
| 14 | 14 | 3 | [Power Grid & Routing Grids](power_grid.html) | III | Reviewed lesson |
| 15 | 15 | 4 | [Metal Layers, Vias & Stackup](metal_layers.html) | III | Reviewed lesson |
| 16 | 16 | 6 | [Inside a Standard Cell Layout](cell_layout.html) | III | Reviewed lesson |
| 17 | 17 | 9 | [Cell Template: Tracks, Sites & Edges](cell_template.html) | III | Reviewed lesson |
| 18 | 18 | 11 | [Anatomy of a Bigger Cell](bigger_cells.html) | III | Reviewed lesson |
| 19 | 19 | 10 | [Pin Access & Porosity](pin_access.html) | III | Reviewed lesson |
| 20 | 20 | 12 | [A Flip-Flop from the Inside](dff_inside.html) | III | Reviewed lesson |
| 21 | 21 | 13 | [Loads](loads.html) | IV | Reviewed lesson |
| 22 | 22 | 14 | [Liberty Files: What a Cell Library Records](liberty.html) | IV | Reviewed lesson |
| 23 | 23 | — | [Reading Liberty Timing Tables](liberty_tables.html) | IV | Split from lesson 22, 9 November 2026 |
| 24 | 24 | 15 | [Timing](timing.html) | IV | Reviewed lesson |
| 25 | 25 | 34 | [Setup & Hold](setup_hold.html) | IV | Reviewed lesson |
| 26 | 26 | 16 | [Routing Resistance & Parasitics](parasitics.html) | IV | Reviewed lesson |
| 27 | — | — | [Delay from Physics: Transistor, Contact, Via, Wire & Gate](delay_physics.html) | IV | New, 11 November 2026 |
| 28 | 27 | 17 | [Electromigration](electromigration.html) | IV | Reviewed lesson |
| 29 | 28 | 45 | [RTL, Synthesis & Timing Constraints](rtl_synthesis_constraints.html) | V | Added 6 November 2026 |
| 30 | 29 | 23 | [The Clock Tree](clock_tree.html) | V | Reviewed lesson |
| 31 | 30 | 46 | [Clock Gating & Power States](clock_gating_power_states.html) | V | Added 6 November 2026 |
| 32 | 31 | 37 | [Clock-Domain Crossings & Reset](cdc_reset.html) | V | Reviewed lesson |
| 33 | 32 | 24 | [Scan](scan.html) | V | Reviewed lesson |
| 34 | — | — | [A Timed Logic Path: Registers, Clocks, Scan & Speed/Power](timed_path.html) | V | New, 11 November 2026 |
| 35 | — | — | [Multi-Corner STA: OCV, CRPR & Hold Cells](multicorner_sta.html) | V | New, 11 November 2026 |
| 36 | — | — | [Functional Verification: Testbenches, Assertions, Formal & Gate-Level Sim](functional_verification.html) | V | New, 11 November 2026 |
| 37 | 33 | 2 | [Fill Cells](fill_cells.html) | VI | Reviewed lesson |
| 38 | 34 | 18 | [Well Taps & Latch-up](well_taps.html) | VI | Reviewed lesson |
| 39 | 35 | 19 | [Endcaps](endcaps.html) | VI | Reviewed lesson |
| 40 | 36 | 20 | [Tie Cells](tie_cells.html) | VI | Reviewed lesson |
| 41 | 37 | 21 | [Antenna Diodes](antenna.html) | VI | Reviewed lesson |
| 42 | 38 | 22 | [Decap Cells](decap.html) | VI | Reviewed lesson |
| 43 | 39 | 25 | [Spare Cells & ECO](spare_eco.html) | VI | Reviewed lesson |
| 44 | 40 | 26 | [Level Shifters](level_shifters.html) | VI | Reviewed lesson |
| 45 | 41 | 27 | [Floorplan](floorplan.html) | VI | Reviewed lesson |
| 46 | 42 | 28 | [Metal Fill & Cell Fill](metal_fill.html) | VI | Reviewed lesson |
| 47 | 43 | 29 | [The I/O Ring](io_ring.html) | VII | Reviewed lesson |
| 48 | 44 | 30 | [ESD & Clamps](esd_clamps.html) | VII | Reviewed lesson |
| 49 | 45 | 31 | [I/O Fill](io_fill.html) | VII | Reviewed lesson |
| 50 | 46 | 32 | [RDL Routing](rdl.html) | VII | Reviewed lesson |
| 51 | 47 | 33 | [I/O Power & IR Drop](io_power.html) | VII | Reviewed lesson |
| 52 | 48 | 48 | [Power, Package & Thermal Coupling](power_package_thermal.html) | VII | Added 6 November 2026 |
| 53 | 49 | 35 | [MOSFET Bias, Gain & Headroom](analog_bias.html) | VIII | Reviewed lesson |
| 54 | 50 | 36 | [Feedback & Stability](feedback_stability.html) | VIII | Reviewed lesson |
| 55 | 51 | 43 | [Differential Pairs, Common Mode & CMFB](differential_pairs.html) | VIII | Added 6 November 2026 |
| 56 | 52 | 39 | [Noise, Mismatch & Variation](noise_mismatch.html) | VIII | Reviewed lesson |
| 57 | 53 | 44 | [References, Temperature & Startup](references_startup.html) | VIII | Added 6 November 2026 |
| 58 | 54 | 47 | [Matching, Layout & Extracted Netlists](matching_layout_extraction.html) | VIII | Added 6 November 2026 |
| 59 | 55 | 40 | [Sampling, Aliasing & Settling](sampling_aliasing.html) | IX | Reviewed lesson |
| 60 | 56 | 38 | [ADC & DAC Interfaces](converters.html) | IX | Reviewed lesson |
| 61 | 57 | 50 | [FFT, Noise & Distortion Measurements](spectral_measurements.html) | IX | Added 6 November 2026 |
| 62 | 58 | 49 | [Calibration, Trimming & Testability](calibration_trim.html) | IX | Added 6 November 2026 |
| 63 | 59 | 41 | [Crosstalk, Return Paths & Isolation](crosstalk_return_paths.html) | IX | Reviewed lesson |
| 64 | 60 | 42 | [Mixed-Signal Verification & Bring-Up](mixed_signal_verification.html) | IX | Reviewed lesson |

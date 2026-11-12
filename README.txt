ASIC DESIGN — SHARED FOUNDATIONS
Reorganized and expanded 9 November 2026; lessons 35–36 and 46, 47, 49 added 11 November 2026.
84 lessons in nine parts, and 7 practical labs.

Extract the ZIP completely. Open learning/index.html in a browser.
All HTML, diagrams, tables, plots and recorded lab results are local.
No simulator or PDK installation is needed to read the course.

Course structure
  Part I    Foundations: the physical chip and its vocabulary (lessons 1–9)
  Part II   Transistors to logic gates (lessons 10–12)
  Part III  Standard-cell layout (lessons 13–20)
  Part IV   Loads, timing and interconnect (lessons 21–32)
  Part V    Digital implementation (lessons 33–46)
  Part VI   Physical cells and the floorplan (lessons 47–63)
  Part VII  The chip boundary: I/O, ESD and package (lessons 64–71)
  Part VIII Analog circuits (lessons 72–78)
  Part IX   Mixed-signal: sampling, conversion and verification (lessons 79–84)

What changed later on 11 November 2026 (IR results, N17–N22, 84 lessons)
- The course is 84 lessons and 7 labs. The gap analysis is complete.
- Lab 6 SPM IR drop was actually run in OpenROAD (analyze_power_grid on VPWR and
  VGND at nom_tt, with -enable_em). Official numbers, without an activity override,
  match STA power (1.28 mW vs report_power 1.275 mW): worst VPWR drop 132 µV,
  worst VGND drop 100 µV, combined 217 µV at clkbuf_0_clk; EM max 35.5 µA (VPWR)
  and 30.5 µA (VGND). Recorded map and logs are in labs/analysis_examples/irdrop/.
  A first run with set_power_activity 0.1 (0.622 mW) was discarded. The original
  Lab 6 folder still has no IR step directory (resume was at Magic.StreamOut).
  Lesson 63 (power_integrity_signoff.html) and lessons 8, 14, 38, 56 and 62
  quote these recorded figures.
- New lesson 24, Standard-Cell Characterization (liberty_characterization.html),
  after Reading Liberty Timing Tables. How a 7×7 NLDM table and a setup bisection
  are produced. Thresholds already verified in lesson 23; lesson 20’s dfxtp_1
  pushout is cited, not replaced. No new 7×7 table is claimed.
- New lesson 27, Latch-Based Design & Time Borrowing (latch_time_borrowing.html),
  after Setup and Hold. HD LEF sizes: dlxtp_1 5.520 µm (12 sites), dlrtp_1 5.980,
  dlxbn_1 6.900; dfxtp_1 is 7.360 (16 sites). Teaching STA; DFFRAM not re-run.
- New lesson 31, Reliability & Aging (reliability_aging.html), after Electromigration:
  HCI, BTI, TDDB, self-heating. Teaching; no SKY130 aging parameter extracted.
- New lesson 32, DFM, Variation & Yield (dfm_yield.html), after Reliability:
  systematic vs random, corners vs Monte Carlo, litho hotspots, redundant vias,
  yield in cost via lesson 2. No invented SKY130 yield.
- New lesson 57, Hierarchical Design, Abstracts & ECO (hierarchical_eco.html),
  after Caravel. LEF/Liberty/Verilog abstracts, timing budgets, and LibreLane
  Classic 3.0.17 using_ecos.md (Odb.InsertECOBuffers, Odb.InsertECODiodes,
  --with-initial-state). Complements metal-only spare-cell ECO (lesson 53).
  No ECO or hierarchical LEF run is claimed.
- New lesson 77, Comparators & Power Management (comparators_ldo_por.html),
  after References, Temperature & Startup: StrongARM, LDO loop, POR. Teaching;
  no SKY130 characterisation.
- Mapping from the previous 78-lesson course: former 24–25 are 25–26; 26–28
  are 28–30; 29–52 are 33–56; 53–71 are 58–76; 72–78 are 78–84. Antenna is
  lesson 51. Clock generation is 36. Digital SI is 60. IR signoff is 63.
  Tapeout is 70. Post-silicon is 71. Mixed-signal verification is 84.

What changed later on 11 November 2026 (clock generation, digital SI, IR signoff, post-silicon)
- The course is 78 lessons and 7 labs.
- New lesson 32, Clock Generation: Oscillators, DCO, PLL & Jitter (clock_generation.html),
  after the Clock Tree. An 11-stage inv_1 ring, ngspice 44.2, course models, tt 25 °C:
  1.849 GHz at 1.80 V, stage delay 24.58 ps (0.341 of the lesson-27 FO4 72.15 ps).
  f vs VDD recorded 185 MHz at 1.00 V to 2.130 GHz at 1.95 V. Decks in
  labs/analysis_examples/ring_osc/. Caravel’s 26-bit thermometer DCO (approx. 90–215 MHz,
  and 90–200 MHz on the same official page) is from the housekeeping docs, not a measurement.
- New lesson 55, Digital Signal Integrity (digital_signal_integrity.html), after Routing.
  Miller 0/1/2, a labelled parallel-plate met1 estimate (86.3 fF/mm; 38 ps for 100 µm at M=2
  versus M=1), windows and NDRs. Not an OpenRCX or STA result. Analog-victim SI is lesson 77.
- New lesson 58, Power-Integrity Signoff (power_integrity_signoff.html), after Physical Signoff.
  LibreLane Classic 3.0.17 OpenROAD.IRDropReport / irdrop.tcl described from the local
  scripts (static analyze_power_grid; no -enable_em). Lab 6 RUN_IRDROP_REPORT was true but
  the report was not executed (resume at Magic.StreamOut). No invented IR map.
- New lesson 66, Post-Silicon Bring-Up (post_silicon_bringup.html), after Tapeout.
  Wafer sort vs final test, shmoo, debug order, Caravel SPI and Tiny Tapeout microcotb,
  from official docs; no tester session was run.
- Mapping from the previous 74-lesson course: former 32–53 are 33–54; 54–55 are 56–57;
  56–62 are 59–65; 63–74 are 67–78. Antenna is lesson 47. Clock Tree is 31. Tapeout is 65.

What changed later on 11 November 2026 (RTL patterns, Caravel, tapeout)
- The course is 74 lessons and 7 labs.
- New lesson 29, RTL Patterns: FSMs, Handshakes, Resets & Lint (rtl_patterns.html, Part V).
  Yosys 0.52 mapped a 3-state traffic light on the same filtered HD Liberty as the datapath
  lesson: binary 7 cells, 98.8448 µm² (2×dfrtp_2); one-hot 13 cells, 177.6704 µm²
  (2×dfrtp_2 + 1×dfstp_2). No STA. Verilator 5.032 CASEINCOMPLETE on a latch pitfall;
  Lab 6 SPM lint metrics all zero (Verilator 5.044).
- New lesson 51, Caravel Integration (caravel_integration.html, Part VI, after Floorplan 50).
  Ports from the LibreLane 3.0.17 user_project_wrapper.v (38 GPIOs, 29 analog_io, Wishbone,
  128-bit LA, eight supplies). Three official hardening strategies from LibreLane docs.
  Physical sizes unchanged: 2920 × 3520 µm, 637 signal pins, 3.60 × 5.20 mm die.
  This course has not hardened a full wrapper.
- New lesson 62, Tapeout, MPW & Tiny Tapeout (tapeout.html, Part VII, after Power/Package).
  Lab 6 final/ deliverables (recorded sizes from lesson 8). Official TT SKY 1×1 161 × 112 µm
  (Creating Silicon Art guide) and FAQ “about 160×100 µm”; check the shuttle yaml.
  No precheck and no TT Action was run.
- Former lessons 29–49 are 30–50; 50–59 are 52–61; 60–71 are 63–74. Antenna is lesson 46.

What changed later on 11 November 2026 (placement, routing, signoff)
- Three new Part VI lessons, after Floorplan (45): Placement (46, placement.html), Routing & Timing Closure (47, routing_timing_closure.html), and Physical Verification Signoff (49, physical_signoff.html). Metal Fill moved from 46 to 48; former lessons 47–64 are now 50–67.
- Placement, routing and the 30/45/60 utilization table are OpenROAD/LibreLane 3.0.17 runs on the bundled 32-bit SPM (sky130_fd_sc_hd). The 45% run RUN_2026-11-11_16-09-06 completed RTL-to-GDS, including Magic/KLayout DRC 0, XOR 0 and Netgen LVS unique match. Lab 6 (lab_rtl_to_gds.html) is that flow. Lab 7 (lab_drc_lvs.html) is Magic/KLayout/Netgen debug on an inverter row, with antenna left in lesson 41.
- The course is 67 lessons and 7 labs.

What changed on 11 November 2026
- New lesson 27, Delay from Physics: Transistor, Contact, Via, Wire & Gate (delay_physics.html,
  Part IV). It follows one SKY130 net from the inv_4 drain through licon, li1, mcon, met1, via,
  met2 and via2 to a met3 route and back down to an inv_1 gate, and builds the delay from
  physical quantities: ngspice I–V curves of nfet_01v8 / pfet_01v8_hvt (gm, output resistance
  and gain, and why they are not the delay), an effective resistance over the output swing,
  gate capacitance from Cox·W·L plus overlap against the Liberty pin capacitance, contact and
  via resistance in series and in parallel, wire R by the square and C per micrometer from the
  HD tech LEF, Elmore and distributed RC, a worked driver-to-gate breakdown checked against
  ngspice, fanout, logical effort and buffer trees, wire length and repeaters, and a calculator.
- New lesson 34, A Timed Logic Path: Registers, Clocks, Scan & Speed/Power (timed_path.html,
  Part V). One sdfxtp_1 → nand2_1 → inv_1 → nor2_1 → buf_2 → sdfxtp_1 path with its clock
  tree and scan chain: stage-by-stage arrival and slew from Liberty, the setup and hold checks
  drawn to scale and in OpenSTA's report layout, the scan shift path and its hold check, slack
  against skew, and the speed/power levers (αCV²f plus leakage, supply voltage, sizing,
  threshold voltage, pipelining), with a setup/hold/scan-hold slack calculator.
- New lesson 35, Multi-Corner STA: OCV, CRPR & Hold Cells (multicorner_sta.html,
  Part V). Nine LibreLane sky130A corners on the bundled SPM multiplier, with
  recorded OpenSTA 2.7 post-route slacks, annotated max_ss setup and min_ff hold
  paths, a Liberty table of HD delay cells, a 10% OCV derate, and CRPR from the
  signoff reports. Signal-integrity delta-delay was not measured on this run.
- New lesson 36, Functional Verification: Testbenches, Assertions, Formal &
  Gate-Level Sim (functional_verification.html, Part V). Self-checking Icarus
  TBs and cocotb 2.1 tests (both PASS), SymbiYosys BMC/cover/k-induction with Z3
  (including a planted-bug FAIL), and a Yosys-mapped sky130_fd_sc_hd netlist with
  an OpenSTA SDF whose CLK→Q delays were measured in Icarus.
- Lessons that were 35–62 became 37–64. Filenames did not change. Navigation, the
  index, the topic list, in-text “lesson N” links, the glossary, the labs pages,
  review notes and course_manifest.json were updated to 64.

- Every lesson from the old 27 onward was renumbered (old 27–32 → 28–33, old 33–60 → 35–62).
  Filenames did not change. Navigation, the index, the topic lists, every in-text "lesson N"
  reference, the labs pages, the glossary, review.html and diary.md were updated.
- Glossary: 26 new terms for the two lessons, then 3 more for the floorplan section below
  (221 rows; 216 underlined terms in assets/course.js).
- Floorplan (lesson 43) gained section 7, "A power ring for a dropped-in macro" (old sections
  7–10 are now 8–11). It covers what a hard macro brings (the OpenRAM SRAM
  sky130_sram_1kbyte_1rw1r_32x256_8: its met4/met3 vccd1/vssd1 rings, met1–met4 obstructions and
  no met5, from its LEF), the core ring versus a macro's built-in ring versus a block ring,
  LibreLane's hierarchical and ring methods, the 10 µm halo, cut rows and endcaps, met4 straps
  stopping at the halo and met5 straps dropping one via4 per crossing, a worked SRAM feed check
  (about 9 mV), ring sizing for IR drop, EM and via count with an illustrative 20 mA block, a
  separate vdda1/vssa1 ring and routing blockage for an analog block, the LibreLane and pdngen
  settings (PDN_MACRO_CONNECTIONS, halos, PDN_MULTILAYER, PDN_CORE_RING, add_pdn_ring), four
  new figures (4–7), four tables, three checkpoints and a ring-sizing calculator. Power Grid,
  I/O Power, Electromigration, Crosstalk & Return Paths and Mixed-Signal Verification link to it.
- Cross-links to the new lessons from Parasitics, Drive Strength, Timing, Setup & Hold, Scan,
  Clock Tree and Metal Layers.
- Every diagram in the course was rendered headlessly (Chrome) and checked for overlapping
  text, clipping and legibility; about 55 figures on 34 pages were fixed. Two figures were
  redrawn: Clock Tree figure 2 (skew and jitter waveforms and a real H-tree) and Level Shifters
  figure 2 (a transistor-level low-to-high shifter). The full list is in diary.md.
- Side-by-side figures are no longer forced to 560 px wide on desktop (assets/course.css).
- Labs 2 and 4: the plotting code in run_lab.py now chooses round axis ticks; the recorded
  result SVGs were re-ticked (data unchanged) and review/lab_file_hashes.json was recomputed.
- labs/analysis_examples/delay_physics/ holds the ngspice decks and numbers behind lesson 27.

What changed on 9 November 2026
- Nine foundation lessons (1–9) were added: what a chip is, the silicon wafer, how a die
  is built in SKY130, the MOSFET, anatomy of a die, packages, the PCB and the supply path,
  the design flow and its files, and a signals primer (DC, AC, RMS, decibels, FFT).
- The 50 existing lessons were reordered so that each lesson builds on earlier ones.
  Filenames did not change. Lesson numbers, navigation, the index, the glossary and every
  in-text "lesson N" reference were updated. The old-to-new map is in diary.md and review.html.
- Terminology: acronyms are spelled out where they are first used, the glossary was
  expanded to 192 terms (221 since 11 November), and the first use of each glossary term on a lesson page is
  underlined with a dotted line; hover over it or focus it to read the definition.
- Four Apache-2.0 images from the SkyWater PDK and Efabless Caravel documentation are bundled
  in assets/foundations/ with ATTRIBUTION.txt and the license text.
- Labs were not changed, except that their pages show the new lesson numbers.

Cleanup pass, 9 November 2026
- Every lesson opens with "What you will learn" and has at least two checkpoints.
- Notes about which files a reviewer opened were rewritten as guidance or moved into
  "Where the numbers come from" boxes; duplicated passages were removed.
- Overlaps trimmed: Timing vs Setup & Hold, Metal Layers vs lesson 3, RDL vs lesson 6.
- Context pass, 10 November 2026: lesson 8 walks through every step of the digital and
  analog flows (what happens, files in and out, open-source and commercial tools, example
  commands, what to check); every other lesson has a "Where this fits" panel; 22 sections
  gained "In the open SKY130 flow" notes; the glossary gained the tool names.
- Liberty was split into lessons 22 and 23, giving 60 lessons (62 later on 11 November, 64 after lessons 35 and 36).
- Choppy captions and fact-list paragraphs were rewritten as flowing prose; the repeated
  caveats in I/O Power and Cell Template were consolidated into one note each.
- Floorplan (now lesson 43) and Clock Tree (now lesson 30) were expanded with new
  sections, figures and a core-sizing calculator.
- Consistent naming (SKY130; met1–met5, with generic M1 only in generic diagrams;
  LibreLane first) and American spelling throughout.
- Legacy per-page style blocks that duplicated assets/course.css were removed;
  page-specific rules were kept.

Open labs.html for the practical sequence. Detailed tool installation and reproduction
instructions are in labs/README.txt.

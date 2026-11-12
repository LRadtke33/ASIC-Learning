LESSONS 27 AND 34 — DELAY-PHYSICS AND TIMED-PATH NUMBERS
Open ../../delay_physics.html (lesson 27) and ../../timed_path.html (lesson 34).

Three scripts, all run from learning/:

  python labs/analysis_examples/delay_physics/run.py [--ngspice PATH]
      ngspice runs of the bundled SKY130 tt models (labs/common/models), 25 C, 1.80 V:
      nfet_01v8 W 0.65 / L 0.15 um and pfet_01v8_hvt W 1.0 / L 0.15 um I-V curves,
      inv_1 fanout 1-16 waveforms, FO4 against supply (1.0-1.8 V), leakage, sizing into
      a fixed 50 fF load, met1/met3 routes with via stacks (10 um - 2 mm), and repeated
      met1 lines (3 and 6 mm). Inverters are N parallel copies of the inv_1 device pair,
      as in the HD library; there are no cell layout parasitics.
      Writes run_results/ (or --output DIR); results/spice_summary.json and the decks in
      results/decks/ are the supplied reference record. Needs ngspice and NumPy; the
      ngspice version used for the record is not stored in it.

  python labs/analysis_examples/delay_physics/liberty_path.py
      No simulator. Reads the bundled sky130_fd_sc_hd__tt_025C_1v80.lib
      (labs/L05_mixed_signal_integration/reference/) and fits effective resistance and
      intrinsic delay for inv_1..inv_8, reads inv_1 delay against fanout, and times the
      sdfxtp_1 -> nand2_1 -> inv_1 -> nor2_1 -> buf_2 -> sdfxtp_1 path of lesson 34 with
      slew propagation, plus its scan-shift hold path. Rewrites results/liberty_summary.json.

  python labs/analysis_examples/delay_physics/hand_calcs.py
      Recomputes every hand calculation quoted in the two lessons (Cox and gate
      capacitance, effective resistance, cut and wire RC, Elmore terms, the worked
      driver-to-gate breakdown, logical-effort and repeater estimates) from the recorded
      JSON files and writes results/hand_calcs.json.

Sources of the fixed inputs
- Cut resistance per cut: SkyWater RCX Table 91 (licon 15, mcon 152, via 4.5, via2 and
  via3 3.41, via4 0.38 ohm); https://skywater-pdk.readthedocs.io/en/main/rules/rcx.html
  Lesson 27 also shows the much lower OpenROAD-flow-scripts setRC.tcl values.
- Wire sheet resistance and capacitance per length (minimum width): the HD tech LEF,
  sky130_fd_sc_hd.tlef (RPERSQ, CPERSQDIST, EDGECAPACITANCE).
- Gate oxide thickness and overlap capacitance: the bundled model files (toxe, cgso).
- Cell pin capacitances, delays, setup and hold: the tt_025C_1v80 Liberty file above.

All results are nominal teaching estimates at one corner; none is signoff timing, and no
result represents a fabricated chip.

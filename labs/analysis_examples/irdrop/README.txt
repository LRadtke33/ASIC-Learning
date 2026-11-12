Lab 6 SPM — static IR drop and EM currents (lesson 58)
=====================================================
Recorded 11 November 2026, America/Chicago, with OpenROAD
dcf36133a369abc8f3c5e5738cd4d82e4903c0e0 — the same binary LibreLane
Classic 3.0.17 uses in this course’s nix environment
(/nix/store/2y36a4sr078y15ick388dncqjdzmlxga-openroad-2026-02-17/bin/openroad).

Design: 45% SPM, run RUN_2026-11-11_16-09-06.
Inputs, all from that run’s final/:
  odb/spm.odb
  spef/nom/spm.nom.spef          (nom_tt extraction)
  sdc/spm.sdc
Liberty: sky130A HD tt_025C_1v80, the same file the run resolved.

This is what LibreLane’s OpenROAD.IRDropReport would have invoked, plus
-enable_em (Classic 3.0.17’s irdrop.tcl does not pass that flag). There is
no VSRC_LOC_FILES, matching the Lab 6 resolved.json; OpenROAD’s default
voltage-source placement is used. The analysis is static and vectorless
(Liberty + SDC; no VCD, no activity override). That is why the reported
total power, 1.28 mW, agrees with the Lab 6 STA report_power of
1.275050 mW at nom_tt_025C_1v80.

VPWR  (set_pdnsim_net_voltage 1.80 V)
  Average IR drop   35.2 µV
  Worstcase IR drop 132 µV   (0.01 % as printed by OpenROAD;
                              132 µV / 1.80 V = 0.0073 %)
  CSV worst terminal: FILLER_11_180 li1 (89.01, 40.80) µm, 1.799868 V
  EM: max 35.5 µA, avg 6.02 µA, 743 resistor elements
      max element met1 (70.52, 40.80) to met2

VGND  (set_pdnsim_net_voltage 0 V)
  Average IR drop   33.2 µV
  Worstcase IR drop 100 µV   (OpenROAD, 0.01 %)
  CSV worst terminal: clkbuf_0_clk li1 (52.90, 54.40) µm, 0.000100 V
  EM: max 30.5 µA, avg 5.73 µA, 751 resistor elements
      max element met1 (42.78, 70.72) to met2

INFO PSM-0040: all shapes on each net are connected.

A rail-to-rail sum at the same instance (VPWR drop + VGND rise) is at
most 217 µV, at clkbuf_0_clk. These drops are small because the SPM die
is 96.6 × 107.32 µm and the current is 1.28 mW / 1.80 V ≈ 0.71 mA.
They are a real OpenROAD result, not a teaching invention. They are not
a top-level chip signoff with package bumps as voltage sources, and the
EM section reports currents, not a comparison against LEF current-density
limits.

Reproduce: openroad -no_init -exit irdrop.tcl
(paths inside the tcl point at the Lab 6 run and the PDK liberty).
Files: irdrop.json, net-VPWR.csv, net-VGND.csv, em-VPWR.txt, em-VGND.txt,
irdrop.log, vpwr_map.svg.

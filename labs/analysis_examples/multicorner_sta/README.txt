Multi-corner STA records for course lesson 35
=============================================

Design:  LibreLane "spm" (32-bit shift-and-add multiplier), sky130_fd_sc_hd
Run:     RUN_2026-11-11_16-09-06  (continued through OpenROAD.STAPostPNR)
Tools:   LibreLane 3.0.17, OpenROAD dcf36133, OpenSTA 2.7.0
PDK:     sky130A (ciel 8afc8346a57fe1ab7934ba5a6056ea8b43078e71)
Clock:   10 ns period, 0.10 ns signoff uncertainty, propagated clock, SPEF from RCX

summary.json
  The nine post-route corners (min|nom|max RC × ff|tt|ss PVT), slacks,
  CRPR, clock latency/skew, and the earlier pre-PNR / post-CTS numbers.

reports/
  max_ss/   worst-setup corner (ss 100 C 1.60 V, max RC): annotated max.rpt
  min_ff/   worst-hold corner  (ff -40 C 1.95 V, min RC): annotated min.rpt
  nom_tt/   typical corner reports, including the setup skew / CRPR report
  max_ss_setup_path.txt, min_ff_hold_path.txt  — first path of each, extracted

postcts_opensta/
  A separate OpenSTA 2.7 run on the post-CTS netlist (no SPEF) at tt/ss/ff,
  plus a 10% OCV derate on tt (set_timing_derate -early 0.90 -late 1.10).

delay_cells.json
  Liberty lookups at 0.05 ns input slew and 5 fF load, for the HD delay
  and clock-delay cells, at tt_025C_1v80, ss_100C_1v60 and ff_n40C_1v95.

These files are recorded results, not a flow you re-run from this folder.
Reproducing them means running LibreLane on the bundled SPM example through
STAPostPNR and copying the 54-openroad-stapostpnr reports.

Lesson 30 — a measured CTS result on the LibreLane SPM example
==============================================================

Open ../../clock_tree.html (lesson 30).

These reports were produced on 11 November 2026 (America/Chicago) by
LibreLane 3.0.17, PDK sky130A (ciel 8afc8346a57fe1ab7934ba5a6056ea8b43078e71),
standard-cell library sky130_fd_sc_hd, running the bundled example
librelane/librelane/examples/spm (32-bit serial/parallel multiplier,
CLOCK_PERIOD 10 ns) with:

  librelane --manual-pdk --pdk-root <PDK> --pdk sky130A --scl sky130_fd_sc_hd \
    --to OpenROAD.ResizerTimingPostCTS config.yaml

The run was stopped after OpenROAD.ResizerTimingPostCTS. It is mid-PnR:
placement-based estimated parasitics, not routed, not a signoff result.
notes.json repeats the numbers cited in the lesson. The .rpt files are
unedited tool output from that run.

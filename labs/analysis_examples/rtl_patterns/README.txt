RTL-patterns lesson artifacts. 11 November 2026, America/Chicago.

Yosys 0.52 (fee39a3284c90249e1d9684cf6944ffbbcbb8f90) + ABC, against the
filtered SKY130 HD tt_025C_1v80 Liberty used in the datapath lesson
(LibreLane 3.0.17 no_synth.cells + drc_exclude.cells). Script:

  proc; flatten; opt; memory; opt; techmap; opt
  dfflibmap -liberty <filtered.lib>
  abc -liberty <filtered.lib>
  clean
  stat -liberty <filtered.lib>

The Yosys fsm pass was not run (no recoding).

  traffic_bin.v / traffic_oh.v     source RTL (async-assert reset)
  traffic_bin.ys / traffic_oh.ys   Yosys scripts
  traffic_*_mapped.v               mapped netlists
  traffic_*_stat.txt               stat excerpts
  latch_pitfall.v                  incomplete case, for Verilator

Recorded areas:
  traffic_bin  7 cells,  2 x dfrtp_2,               98.8448 um^2 (seq 52.5504)
  traffic_oh  13 cells,  2 x dfrtp_2 + 1 x dfstp_2, 177.6704 um^2 (seq 78.8256)

Verilator 5.032 (Debian) --lint-only -Wall: traffic_bin clean;
latch_pitfall: %Warning-CASEINCOMPLETE (example pattern 0x2), fatal under -Wall.

No STA was run. Do not cite a delay from these files.

Setup-time pushout of sky130_fd_sc_hd__dfxtp_1
================================================
Lesson 20 (dff_inside.html). ngspice 44.2, 11 November 2026, America/Chicago.

Same cell netlist, models, 1.678 fF load and 20 ps 0-to-100% edges as the
CDC metastability record in labs/analysis_examples/metastability/.
Schematic-level, tt 25 C 1.80 V, no layout parasitics.

CLK 50% is at 2.02 ns (PULSE delay 2.01 ns + 10 ps). D 50% is offset by
delta (negative = D first). Clock-to-Q is the 50% (0.90 V) Q rise minus
the 50% CLK rise. Q is initialized to 0; D rises through the capturing edge.

See pushout.json. The comfortable-setup clk-to-Q is about 169 ps and is
flat until the offset approaches a few tens of picoseconds, then stretches
(pushout). The published Liberty setup of 0.103 ns is a characterized
library number, not this schematic sweep, and is not contradicted by it.

The extreme (few-picosecond) end of the same cell is the resolve-time
measurement in lesson 34 (cdc_reset.html).

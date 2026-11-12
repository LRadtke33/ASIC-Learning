Lesson 32 — metastability of sky130_fd_sc_hd__dfxtp_1
=====================================================

Open ../../cdc_reset.html (lesson 32).

  python labs/analysis_examples/metastability/run.py [--ngspice PATH] [--output DIR]

ngspice transient runs of the bundled SKY130 tt models (labs/common/models) at 25 C
and 1.80 V, using the published sky130_fd_sc_hd__dfxtp_1 schematic netlist in this
folder (HD revision ac7fb61f06e6470b94e8afdf7c25268f62fbd7b1). There are no cell
layout parasitics. The load is 1.678 fF, the Liberty D-pin capacitance of dfxtp_1,
standing in for a following synchronizer stage. Clock and data 0-to-100% rises are
20 ps. Q is initialized to 0; D rises near the capturing edge.

Method A sweeps the D-edge to CLK-edge offset around the functional boundary,
measures clock-to-Q resolve time (50% and 90% of 1.80 V), and fits

    T_r = tau * ln(T0 / |t_D - t_m|)

on the polarity that produces a visible Q transition (resolve-to-1). When the
master resolves back to the value the slave already holds, Q may never move;
that polarity is not fitted here.

The record in results/summary.json was taken with ngspice 44.2. It is a
schematic-level typical-corner characterization: not a silicon MTBF, not a
signoff number, and not a foundry reliability limit. Voltage, temperature,
mismatch and extracted parasitics all change tau and T0.

Writes --output DIR (default results/). The shipped record is results/summary.json
and the two SVG figures; re-running recreates the full deck set.

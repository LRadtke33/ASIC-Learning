`timescale 1ns/1ps
`define FUNCTIONAL
`ifndef UNIT_DELAY
`define UNIT_DELAY #0.001
`endif
// Functional HD models (no specify, no power pins).  Used for correctness
// of the Yosys-mapped netlist.  See tb_ckq_specify.v for a specify-delay
// measurement of the OpenSTA SDF CLK->Q numbers.
`include "primitives.v"
`include "sky130_fd_sc_hd.v"

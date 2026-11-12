Functional-verification examples for course lesson 36
=====================================================

RTL
  rtl/gray4.v        4-bit Gray-code counter
  rtl/sync_fifo.v    4-deep, 8-bit synchronous FIFO

Self-checking Verilog testbenches (Icarus Verilog 12.0)
  tb/tb_gray4.v      32 Gray steps + hold-when-disabled; drive and sample
                     on the falling edge to avoid a race with the DUT clock
  tb/tb_sync_fifo.v  fill, write-to-full ignored, drain against a queue
                     scoreboard, simultaneous wr+rd

  iverilog -o tb_gray4 rtl/gray4.v tb/tb_gray4.v && vvp tb_gray4
  iverilog -o tb_fifo  rtl/sync_fifo.v tb/tb_sync_fifo.v && vvp tb_fifo

  Recorded: both PASS (0 errors).

cocotb 2.1.0  (Python tests, same Icarus backend)
  cocotb/test_gray4.py, test_sync_fifo.py, Makefile
  From cocotb/:  make SIM=icarus
                 make SIM=icarus TOPLEVEL=sync_fifo MODULE=test_sync_fifo \
                      VERILOG_SOURCES=../rtl/sync_fifo.v
  Recorded: test_reset_and_sequence PASS (425 ns);
            test_fill_drain_scoreboard PASS (225 ns).

Formal (SymbiYosys + Yosys 0.62 + yosys-smtbmc + Z3 4.13.3)
  formal/gray4_formal.v, sync_fifo_formal.v   RTL with immediate assertions
  formal/*.sby                                BMC, cover, prove (k-induction),
                                              and a deliberate Gray-counter mutant
  Engine is `smtbmc z3`.  A system Boolector 1.5 on PATH is too old for
  yosys-smtbmc (it rejects SMT-LIB `set-option`).

  Recorded:
    gray4_bmc    PASS, depth 24
    gray4_cover  PASS, wrap 0000..1000..0000 reached at step 18
    gray4_prove  PASS, k-induction (basecase + induction)
    gray4_bug    FAIL at step 4 (binary counter violates Hamming distance 1)
    fifo_bmc     PASS, depth 20
    fifo_cover   PASS (full at step 6, empty-after-full at step 10,
                 simultaneous wr/rd at step 5)
  All of these assume a starting reset (`initial assume (rst_n == 0)`),
  otherwise formal explores arbitrary power-on register values.

Gate-level (Yosys 0.62, OpenSTA 2.7, Icarus 12, sky130_fd_sc_hd)
  gl/synth.ys, gray4_gl.v, gray4.sdf, write_sdf.tcl, tb_gray4_gl.v,
  pdk_cells.v, tb_ckq_specify.v
  Recorded:
    16 HD cells, chip area 196.4384 µm², 4× dfrtp_1
    OpenSTA (no SPEF, tt 25 C 1.80 V, 10 ns clock): setup WS 8.40 ns (MET);
      a removal check on unconstrained rst_n is VIOLATED (−0.31 ns) — that
      is a constraint issue, not a datapath hold fail (datapath hold 0.10 ns MET)
    Functional GL sim (`define FUNCTIONAL, UNIT_DELAY #0.001): PASS, 32 steps,
      CLK→Q = 0.001 ns (the unit delay)
    OpenSTA SDF: dfrtp_1 instance _21_ IOPATH CLK Q (0.374::0.374) (0.389::0.389) ns
    Icarus 12.0's $sdf_annotate accepted the call but did not apply IOPATH
      delays in a controlled one-buffer test.  Compiling those same OpenSTA
      numbers as `specify` delays (tb_ckq_specify.v, -gspecify) measured
      CLK→Q rise 0.3740 ns and fall 0.3890 ns.

Run everything that is local (iverilog + cocotb) with ./run.sh.
Formal and Yosys-to-HD synthesis need the LibreLane nix-shell (sby, yosys 0.62, sta).

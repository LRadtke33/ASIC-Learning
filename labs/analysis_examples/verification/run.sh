#!/usr/bin/env bash
# Run the Icarus self-checking TBs and, if cocotb is on PATH, the Python tests.
# Formal / GL synthesis are documented in README.txt (need Yosys 0.62 + sby + sta).
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "==== iverilog tb_gray4 ===="
iverilog -g2012 -o /tmp/tb_gray4 rtl/gray4.v tb/tb_gray4.v
vvp /tmp/tb_gray4
echo "==== iverilog tb_sync_fifo ===="
iverilog -g2012 -o /tmp/tb_fifo rtl/sync_fifo.v tb/tb_sync_fifo.v
vvp /tmp/tb_fifo
if command -v cocotb-config >/dev/null 2>&1; then
  echo "==== cocotb gray4 ===="
  make -C cocotb SIM=icarus TOPLEVEL=gray4 MODULE=test_gray4 VERILOG_SOURCES="$(pwd)/rtl/gray4.v"
  echo "==== cocotb sync_fifo ===="
  make -C cocotb SIM=icarus TOPLEVEL=sync_fifo MODULE=test_sync_fifo VERILOG_SOURCES="$(pwd)/rtl/sync_fifo.v"
else
  echo "cocotb not on PATH — skipping Python tests (see README.txt)"
fi
echo "==== specify-delay CLK->Q demo (OpenSTA SDF numbers) ===="
iverilog -g2012 -gspecify -o /tmp/tb_ckq gl/tb_ckq_specify.v
vvp /tmp/tb_ckq
echo ALL_OK

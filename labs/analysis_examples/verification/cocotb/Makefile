# Run:  source ../../../.venv?  The venv lives at /workspace/learn/.venv
#   make -C cocotb SIM=icarus
SIM ?= icarus
TOPLEVEL_LANG = verilog

# default target is gray4; `make TOPLEVEL=sync_fifo MODULE=test_sync_fifo` for the FIFO
RTL_DIR = $(PWD)/../rtl
VERILOG_SOURCES ?= $(RTL_DIR)/gray4.v
TOPLEVEL ?= gray4
MODULE   ?= test_gray4

# cocotb 2.x
include $(shell cocotb-config --makefiles)/Makefile.sim

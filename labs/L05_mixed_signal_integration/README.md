# Lab 5 — Mixed-signal integration across clocks and power events

Open `../../lab_mixed_signal_integration.html` for the complete lesson, diagrams,
worked examples, expected results, and solved exercises.

## What runs

The main experiment is a **digital event simulation** of a one-entry, four-phase
request/acknowledge mailbox. Source and readout clocks differ. A qualified
analog-ready contract and power-good indication control coordinated reset of
both protocol endpoints. The receiver consumes every `dst_valid` pulse.

No PDK, network connection, SPICE installation, or physical analog model is
needed for the main lab. RTL does not simulate analog metastability, settling,
voltage collapse, isolation-cell behavior, or routing delays.

## Main experiment

Prerequisites: Python 3 and Icarus Verilog (`iverilog` and `vvp` on PATH).
The reference run used Icarus Verilog 12.0.

From this directory:

```sh
python3 run.py
```

This compiles the RTL and self-checking SystemVerilog testbench, then runs three
clock/phase configurations. Each must print:

```text
PASS: all digital protocol assertions and directed tests passed
```

Optional commands:

```sh
python3 run.py --case fast_source --waves
python3 run.py --case fast_source --negative-control
python3 run.py --iverilog /path/to/iverilog --vvp /path/to/vvp
```

The negative control generates a broken copy under `run_results/`; it does not
modify the supplied RTL. Success means the expected data-hold assertion fails
and the runner reports `NEGATIVE CONTROL PASS`.

Tools can also be selected with the `IVERILOG` and `VVP` environment variables.
Fresh outputs go under `run_results/`, including logs, traces, optional VCDs, and
`observed.json`. Recorded reference evidence remains under `results/`.

## Tests and interface contract

The directed tests cover reset/analog-not-ready blocking, normal coherent words,
rapid offers while busy, a paused readout clock, in-flight power loss with that
clock stopped, readiness withdrawal, and external-reset restart. Checks compare
accepted words against delivered words, detect stale/duplicate/out-of-order data,
verify the held bus stays constant while busy, enforce synchronous reset release,
and verify `accepted = delivered + aborted` after the test drains.

An offer is accepted only on a source edge with `src_send && src_ready`. Busy
requests are deliberately rejected, not queued. The four-phase handshake must
return fully to idle before another word can be accepted. A reset, power loss,
or readiness withdrawal resets both protocol endpoints and aborts any accepted
word not already delivered. There is no automatic replay and no crash-durable
exactly-once guarantee. Hardware implementation still needs CDC/RDC review,
characterized synchronizers, bounded bundled-data delay, and reset timing checks.

The logical supervisor inputs are assumed already qualified. The RTL expression
combining them is not a physical analog power-good or reset-distribution circuit.

## Optional, separate synthesis example (lesson 49)

The small `enabled_xor.v` design illustrates RTL inference; it is separate from
the mailbox. It needs Yosys with ABC and uses the bundled, checksum-verified
SKY130 TT/25 C/1.8 V Liberty file. The default run is offline:

```sh
python3 synthesis_example/run_synthesis.py
```

Explicit tool paths are supported:

```sh
python3 synthesis_example/run_synthesis.py --yosys /path/to/yosys --abc /path/to/abc
```

`YOSYS` and `ABC` environment variables are also supported. `--lib PATH` selects
a byte-identical copy. `--fetch-lib` explicitly downloads a fresh pinned copy;
it is not needed for ordinary offline use.

The recorded Yosys 0.52 run mapped two enabled bits to two
`sky130_fd_sc_hd__edfxtp_1` cells plus two `sky130_fd_sc_hd__xor2_1` cells. The
reported library cell-area sum was 77.5744 µm² (matching the published cell footprints). The tool proved both output bits
functionally equivalent using the Liberty Boolean/sequential models.

**No SDC-driven optimization, STA, placement, routing, clock-tree synthesis, or
power estimation was executed.** `synthesis_example/example.sdc` is an explicitly
assumed teaching constraint file and is not read by the synthesis runner.

## Reference data and attribution

`reference/SOURCE.json` records the exact upstream source, revision, file size,
and SHA-256 of the included Liberty. Upstream licenses and attribution are in
`reference/`. The single typical library is not a complete PDK or process/corner
signoff set. Do not infer a fabrication qualification from the successful lab.

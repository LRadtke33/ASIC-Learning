# Recorded execution evidence

Recorded on 6 November 2026 with Icarus Verilog 12.0 and Yosys 0.52.
`observed.json` records the three passing directed simulation cases;
`observed_negative.json` records the intended failing negative control.
CSV files contain source acceptance, receiver delivery, and cancellation events.
The largest delivery latencies include the intentional readout-clock pause.

`synthesis_observed.json`, `synthesis_mapped.v`, and synthesis logs record the
separate two-bit enabled-XOR mapping and functional equivalence result.
No STA or physical implementation was run. The full Liberty reference and its
source/license metadata are under `../reference/`.

Workspace-specific absolute prefixes in text logs were normalized to `<lab>`
for portability. Numeric results and diagnostic messages are unchanged.
`source_hashes.json` identifies the shipped RTL, testbench, runners, and teaching
SDC. The SDC is included for discussion; neither runner executes it.

Reruns write `../run_results/` and preserve this reference evidence.

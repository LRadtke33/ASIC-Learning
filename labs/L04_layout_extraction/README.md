# Lab 4 — Geometry, interconnect estimates, and measured response

**Run a complete geometry → analytical RC estimate → transient simulation workflow.** Four routes share the same logical driver/receiver connection. Their geometry and electrical surroundings differ. The files expose every coefficient, network element, physical probe location, stimulus, and measurement.

The shipped `results/` were generated with **ngspice 44.2**. This is an actual simulation of the supplied linear RC networks. Those networks are **analytical estimates**, not foundry-qualified parasitic extraction. No Magic extraction, GDS generation, DRC, LVS, device-model simulation, or tapeout qualification was performed for this lab. The drawings are geometry illustrations, not manufacturing layouts.

Read the illustrated lesson at `../../lab_layout_extraction.html`. Related theory is in `../../matching_layout_extraction.html`.

## Run it

Requirements: Python 3.10 or newer. The estimator and fallback integrator use only the Python standard library. A local ngspice executable is optional; no PDK or network access is needed.

From this lab directory:

```sh
python3 run_lab.py
```

The default uses ngspice if it is on `PATH` or named by the `NGSPICE` environment variable. Otherwise it uses the explicitly identified Python backward-Euler solver. New results go into **`run_results/`**, preserving the shipped reference results.

To require ngspice, rather than silently selecting the fallback:

```sh
python3 run_lab.py --engine ngspice --ngspice /absolute/path/to/ngspice
```

To deliberately use the independent Python solver:

```sh
python3 run_lab.py --engine builtin --output python_results
```

To refine both the spatial segmentation and maximum time step:

```sh
python3 run_lab.py --engine ngspice --segment-um 10 --step-ps 5 --output refined_results
```

The original reference command was the ngspice run with 20 µm segments, a 10 ps maximum time step, and `--output results`. The complete version, settings, inputs' SHA-256 hashes, and results are recorded in `results/summary.json`.

## Inputs and units

| Input | Meaning |
|---|---|
| `geometry/*.json` | Manhattan met3 signal centerline, width, reference plane, and upper conductor rectangles; all distances in µm |
| `sky130_coefficients.json` | Published SKY130 coefficients, source URL, source snapshot hash, and limitations |
| `run_lab.py` | Estimator, SPICE exporter, simulator driver, independent solver, measurements and SVG plotting |

All four signals begin at `(20,40)` and end at `(220,40)` µm. The compact route is 200 µm long. The three detours travel through `(20,240)` and `(220,240)`, giving 600 µm. Narrow routes are 0.4 µm wide; the wide detour is 1.2 µm. A broad, quiet met2 plane lies below every route. The met4 aggressor lies over the upper part of the detours. The final case adds a separate met4 patch tied ideally to the reference.

This deliberately restricted input model rejects non-Manhattan paths, zero-width routes, self-touching/crossing paths, incomplete reference-plane coverage, overlapping upper rectangles, and partial coverage of the signal width. It does not check SKY130 design rules.

## Estimator equations

The public SKY130 [RCX tables](https://skywater-pdk.readthedocs.io/en/main/rules/rcx.html), checked 6 November 2026, give:

| Quantity used here | Value |
|---|---:|
| met3 sheet resistance | 0.047 Ω/□ |
| met2–met3 parallel area capacitance | 86.1861 aF/µm² |
| met3 toward a large lower met2 plate: fringe capacitance | 69.846 aF/µm |
| met3–met4 parallel area capacitance | 84.0346 aF/µm² |

For a segment of length ΔL and width W, the estimator uses:

```text
Rsegment = Rsheet × ΔL/W
Cto_lower_reference = Carea_down × W×ΔL + Cfringe_down × 2ΔL
Cto_aggressor = Carea_up × overlapped area
Cto_grounded_patch = Carea_up × overlapped area
```

Segment capacitances are split equally between its two endpoints. Two physical end-edge fringe terms, `Cfringe_down × W`, are added once at the route endpoints. Numerical segment boundaries do not create extra perimeter. Grounded-patch capacitance is added to reference capacitance; aggressor capacitance remains connected to the aggressor node.

The source's fringe coefficients are plate-based approximations, described using a 5 µm × 10 µm plate and a much larger facing plate. Applying them to these long wires is a transparent teaching approximation. This estimator omits upper fringe fields, lateral coupling, field redistribution, via/contact resistance, corner and width corrections, process variation, temperature dependence, and substrate/package effects. A zero area-overlap coupling result does not prove that the physical coupling is zero.

## Experiments and measurement definitions

All source/load values below are assumptions: 20 kΩ source resistance, 50 fF receiver load, 1.8 V stimulus, ramp beginning at 2 ns with a 0.2 ns duration. Simulations stop at 60 ns.

1. **Step experiment:** source ramps; aggressor stays at zero. Measure receiver rise, propagation delay, settling, and the voltage at 10 ns.
2. **Coupling experiment:** source stays at zero through 20 kΩ; aggressor ramps. Measure peak absolute receiver disturbance.

`t50_delay_ns` is receiver 0.9 V crossing minus **the simulated source's** 0.9 V crossing. It is not time from simulation start. `half_LSB_settling_after_ramp_ns` is the last exit from the ±1.8/8192 V error band, measured after the ramp ends at 2.2 ns. The illustrative 12-bit half-LSB is 219.727 µV. The circuit contains no ADC; this is a precision-settling criterion imposed on a linear network.

## Reference results

| Route | Estimated R (Ω) | C to reference (fF) | C to aggressor (fF) | 50% delay (ns) | Half-LSB settling after ramp (ns) | Coupling peak (mV) |
|---|---:|---:|---:|---:|---:|---:|
| Compact | 23.5 | 34.8892 | 0 | 1.1790 | 15.2113 | 0* |
| Detour | 70.5 | 104.5557 | 16.1346 | 2.3728 | 30.7142 | 165.1007 |
| Wide detour | 23.5 | 146.0368 | 48.4039 | 3.3917 | 43.9758 | 349.1446 |
| Detour + grounded patch | 70.5 | 107.9171 | 16.1346 | 2.4195 | 31.3205 | 162.0029 |

`*` Compact coupling is zero in this overlap-only upper-field model. It is not a physical isolation guarantee.

The wide detour has lower wire resistance but greater loading. With the assumed 20 kΩ source, that extra capacitance dominates and slows the response. The grounded patch adds 3.361384 fF. At 10 ns, the otherwise matched detour and patched detour differ by **8.149249 mV**. Their final DC voltages are equal because capacitors carry no DC current in this ideal model.

## Outputs and probes

| Output | Use |
|---|---|
| `summary.json`, `summary.csv` | Numeric results, engine identity, settings and input hashes |
| `networks/*.spice` | Distributed RC subcircuits; ports are `SIG_DRV SIG_RX AGG REF` |
| `networks/*_estimate.json` | Every segment, node coordinate, R and capacitance allocation |
| `mapping/*_probes.csv` | Schematic net, physical role, coordinates, SPICE node and simulator vector |
| `decks/*_step.cir`, `*_coupling.cir` | Complete ngspice benches, exported for either integration engine |
| `waveforms/*.csv` | Time in seconds and source/driver/midpoint/receiver/aggressor voltages in volts |
| `raw/*.dat`, `logs/*.log` | ngspice raw text and logs; only created by ngspice runs |
| `figures/*.svg` | Geometry views and measured-response plots |

The subcircuit's internal `SIG_015` node appears as `v(xroute.sig_015)` in ngspice. Its position for the default detour is `(120,240)` µm. The exported mapping file is authoritative: refining the segmentation changes internal indices. `v(sig_rx)` always probes the receiver port. The main bench ties `REF` to simulator ground; a different reference connection changes the experiment.

To run one exported bench independently, change into its `decks/` directory, then invoke `ngspice -b detour_step.cir`. Relative includes and output paths are resolved from that working directory.

## Exercises, with answer checks

1. **Check the units:** the compact route has `200/0.4 = 500` squares, so its resistance is `0.047 × 500 = 23.5 Ω`. The compact area is 80 µm², contributing 6.894888 fF; its idealized perimeter is 400.8 µm, contributing 27.9942768 fF. Total reference capacitance is 34.8891648 fF.
2. **Predict before running:** triple route length at fixed width. The sheet-resistance estimate triples. Ground capacitance approximately triples, but the two end-edge terms are not tripled. Mutual capacitance depends on overlap, not total length alone.
3. **Widen the detour:** wire R falls by three, while upper area coupling triples. The computed timing gets worse under this high source-resistance assumption. Try reducing `SOURCE_R` in a copied runner, and record the new assumption with the result.
4. **Reinterpret the patch:** do not relabel it “floating fill.” It is explicitly tied to REF. A floating island requires a separate node with capacitances to surrounding conductors and an appropriate initial-charge treatment. Simply grounding it changes the circuit.
5. **Compare probes:** driver and receiver share logical net SIG but are separated by R. During charging they need not have the same voltage. Probe both before diagnosing a disagreement with a schematic simulation.
6. **Refine:** repeat with 10 µm segments and 5 ps maximum time step. Compare summary values before claiming numerical precision. Shipped `verification.json` records the performed comparison and independent-solver check.

## What a real PEX extension must add

`OPTIONAL_MAGIC.md` describes an **unexecuted extension** using an installed compatible Magic/SKY130 technology and a genuine labeled layout. It requires DRC/LVS, correct extraction style, preserved coupling, model accounting, and port/probe verification. There is no qualified PDK extraction hidden behind this estimator. A production flow must use the tools, technology files, rule revisions, and acceptance criteria appropriate to its fabrication route.

## Troubleshooting

If ngspice is missing, use `--engine builtin` or pass its absolute executable path. If `--engine ngspice` fails, inspect the generated `logs/` and retain the deck rather than trusting an old summary. Small solver differences are expected: ngspice uses its configured adaptive integration; the fallback uses fixed-step backward Euler. Both simulate the same finite RC ladder. Tightening the step and segment length addresses numerical discretization, not the physical omissions of the model.

Checked and reference runs generated 6 November 2026. No third-party device-model files or simulator binaries are bundled with this lab.
